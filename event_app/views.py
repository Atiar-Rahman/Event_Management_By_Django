# event_app/views.py

from django.urls import reverse_lazy
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, Count
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model

from .models import Event, Category
from .forms import EventForm, CategoryForm


# -------------------------------
# No-permission landing page
# -------------------------------
def no_permission(request):
    return render(request, 'event_app/no_permission.html', status=403)


# -------------------------------
# Shared permission mixin (RBAC)
# -------------------------------
class RBACPermissionRequiredMixin(PermissionRequiredMixin):
    """
    If not authenticated -> send to login.
    If authenticated but missing perms -> send to 'event_app:no_permission'.
    """
    login_url = 'login'
    raise_exception = False
    redirect_field_name = None

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect(self.get_login_url())
        return redirect(reverse_lazy('event_app:no_permission'))


# -------------------------------
# Home page (latest events)
# -------------------------------
def home(request):
    events = (
        Event.objects
        .select_related('category')
        .prefetch_related('participants')
        .all()[:9]
    )
    return render(request, 'event_app/home.html', {'events': events})


# -------------------------------
# Event list with search/filter
# -------------------------------
class EventListView(ListView):
    model = Event
    template_name = 'event_app/event_list.html'
    context_object_name = 'events'

    def get_queryset(self):
        queryset = (
            Event.objects
            .select_related('category')
            .prefetch_related('participants')
            .all()
        )

        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(location__icontains=search_query)
            )

        category_id = self.request.GET.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        if start_date and end_date:
            queryset = queryset.filter(date__range=[start_date, end_date])

        return queryset


# -------------------------------
# Event detail
# -------------------------------
class EventDetailView(DetailView):
    model = Event
    template_name = 'event_app/event_detail.html'
    context_object_name = 'event'
    pk_url_kwarg = 'id'

    def get_queryset(self):
        return (
            Event.objects
            .select_related('category')
            .prefetch_related('participants')
        )


# -------------------------------
# Event create/update/delete (RBAC)
# -------------------------------
class EventCreateView(RBACPermissionRequiredMixin, CreateView):
    model = Event
    form_class = EventForm
    template_name = 'event_app/event_form.html'
    success_url = reverse_lazy('event_app:event_list')
    permission_required = 'event_app.add_event'


class EventUpdateView(RBACPermissionRequiredMixin, UpdateView):
    model = Event
    form_class = EventForm
    template_name = 'event_app/event_form.html'
    success_url = reverse_lazy('event_app:event_list')
    permission_required = 'event_app.change_event'
    pk_url_kwarg = 'id'


@permission_required('event_app.delete_event', login_url='login')
def event_delete(request, id):
    if not request.user.has_perm('event_app.delete_event'):
        return redirect('event_app:no_permission')
    event = get_object_or_404(Event, id=id)
    if request.method == 'POST':
        event.delete()
        return redirect('event_app:event_list')
    return render(request, 'event_app/event_confirm_delete.html', {'event': event})


# -------------------------------
# Dashboard (with total_participants)
# -------------------------------
@login_required(login_url='login')
def dashboard(request):
    # Only organizers/admins (or anyone with view permission)
    if not request.user.has_perm('event_app.view_event'):
        return redirect('event_app:no_permission')

    User = get_user_model()
    today = timezone.localdate()

    total_events = Event.objects.count()
    upcoming_events = Event.objects.filter(date__gt=today).count()
    past_events = Event.objects.filter(date__lt=today).count()

    # Unique users who RSVP’d to at least one event
    total_participants = (
        User.objects.filter(rsvped_events__isnull=False).distinct().count()
    )

    todays_events = (
        Event.objects
        .filter(date=today)
        .select_related('category')
        .prefetch_related('participants')
        .annotate(num_participants=Count('participants'))
    )

    context = {
        'total_events': total_events,
        'upcoming_events': upcoming_events,
        'past_events': past_events,
        'total_participants': total_participants,
        'todays_events': todays_events,
        'today': today,
    }
    return render(request, 'event_app/dashboard.html', context)


# -------------------------------
# Dashboard stats JSON API
# -------------------------------
@login_required(login_url='login')
def dashboard_stats_api(request):
    filter_type = request.GET.get('filter', 'all')
    today = timezone.localdate()

    qs = (
        Event.objects
        .select_related('category')
        .prefetch_related('participants')
        .annotate(num_participants=Count('participants'))
    )

    if filter_type == 'upcoming':
        qs = qs.filter(date__gte=today)
    elif filter_type == 'past':
        qs = qs.filter(date__lt=today)

    data = []
    for e in qs.order_by('date')[:50]:
        data.append({
            'id': e.id,
            'name': e.name,
            'date': e.date.isoformat(),
            'time': e.time.isoformat() if e.time else '',
            'location': e.location,
            'category': e.category.name if e.category else '',
            'num_participants': e.num_participants,
            'status': 'upcoming' if e.date >= today else 'past',
        })

    return JsonResponse({'events': data})


# -------------------------------
# RSVP actions (POST-only)
# -------------------------------
@login_required(login_url='login')
@require_POST
def rsvp_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.user in event.participants.all():
        messages.warning(request, "You have already RSVP’d to this event.")
    else:
        event.participants.add(request.user)
        messages.success(request, "RSVP successful. A confirmation email has been sent.")
        send_mail(
            subject="RSVP Confirmation",
            message=f"Hi {request.user.username},\n\nYou've successfully RSVP’d for '{event.name}'.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[request.user.email],
            fail_silently=True
        )
    return redirect('event_app:event_detail', id=event.id)


@login_required(login_url='login')
@require_POST
def cancel_rsvp(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.user in event.participants.all():
        event.participants.remove(request.user)
        messages.info(request, "Your RSVP has been cancelled.")
    return redirect('event_app:event_detail', id=event.id)


# -------------------------------
# Category views
# -------------------------------
def category_list(request):
    categories = Category.objects.annotate(event_count=Count('events'))
    return render(request, 'event_app/category_list.html', {'categories': categories})


class CategoryCreateView(RBACPermissionRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'event_app/category_form.html'
    success_url = reverse_lazy('event_app:category_list')
    permission_required = 'event_app.add_category'


@permission_required('event_app.change_category', login_url='login')
def category_update(request, id):
    if not request.user.has_perm('event_app.change_category'):
        return redirect('event_app:no_permission')
    category = get_object_or_404(Category, id=id)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('event_app:category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'event_app/category_form.html', {'form': form})


@permission_required('event_app.delete_category', login_url='login')
def category_delete(request, id):
    if not request.user.has_perm('event_app.delete_category'):
        return redirect('event_app:no_permission')
    category = get_object_or_404(Category, id=id)
    if request.method == 'POST':
        category.delete()
        return redirect('event_app:category_list')
    return render(request, 'event_app/category_confirm_delete.html', {'category': category})

@login_required(login_url='login')
def my_rsvped_events(request):
    events = (
        request.user.rsvped_events
        .select_related('category')
        .annotate(num_participants=Count('participants'))
        .order_by('date', 'time')
    )
    return render(request, 'event_app/my_events.html', {'events': events})