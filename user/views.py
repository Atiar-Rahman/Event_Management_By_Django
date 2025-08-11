from django.urls import reverse_lazy
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, Count
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings

from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from events.models import Event, Category
from .forms import EventForm, CategoryForm


# =========================
# RBAC: Groups
# =========================
GROUP_ADMIN = 'admin'
GROUP_ORGANIZER = 'organizer'
GROUP_PARTICIPANT = 'participant'

def _in_groups(user, groups):
    """True if user is authenticated and in any of the groups (or is superuser)."""
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return user.groups.filter(name__in=groups).exists()

def role_required(*group_names, login_url='login'):
    """Decorator for FBVs to enforce group-based access."""
    return user_passes_test(lambda u: _in_groups(u, group_names), login_url=login_url)

class RoleRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin for CBVs: set allowed_groups = ('admin','organizer',...)"""
    allowed_groups: tuple[str, ...] = ()

    def test_func(self):
        return _in_groups(self.request.user, self.allowed_groups)

    def handle_no_permission(self):
        # If authenticated but not allowed, go to a friendly page
        if self.request.user.is_authenticated:
            return redirect('no-permission')
        return super().handle_no_permission()


# =========================
# Public views
# =========================
def home(request):
    events = (Event.objects
              .select_related('category')
              .prefetch_related('participants')
              .all()[:9])
    return render(request, 'events/home.html', {'events': events})


class EventListView(ListView):
    model = Event
    template_name = 'events/event_list.html'
    context_object_name = 'events'

    def get_queryset(self):
        qs = Event.objects.select_related('category').prefetch_related('participants')
        q = self.request.GET.get('search', '').strip()
        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(location__icontains=q))
        category_id = self.request.GET.get('category')
        if category_id:
            qs = qs.filter(category_id=category_id)
        d1 = self.request.GET.get('start_date')
        d2 = self.request.GET.get('end_date')
        if d1 and d2:
            qs = qs.filter(date__range=[d1, d2])
        return qs


class EventDetailView(DetailView):
    model = Event
    template_name = 'events/event_detail.html'
    context_object_name = 'event'
    pk_url_kwarg = 'id'

    def get_queryset(self):
        return Event.objects.select_related('category').prefetch_related('participants')


# =========================
# Event CRUD (Admin/Organizer)
# =========================
class EventCreateView(RoleRequiredMixin, CreateView):
    allowed_groups = (GROUP_ADMIN, GROUP_ORGANIZER)
    model = Event
    form_class = EventForm
    template_name = 'events/event_form.html'
    success_url = reverse_lazy('event_list')

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Event created successfully.")
        return super().form_valid(form)


class EventUpdateView(RoleRequiredMixin, UpdateView):
    allowed_groups = (GROUP_ADMIN, GROUP_ORGANIZER)
    model = Event
    form_class = EventForm
    template_name = 'events/event_form.html'
    success_url = reverse_lazy('event_list')
    pk_url_kwarg = 'id'

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Event updated successfully.")
        return super().form_valid(form)


@role_required(GROUP_ADMIN, GROUP_ORGANIZER, login_url='login')
def event_delete(request, id):
    event = get_object_or_404(Event, id=id)
    if request.method == 'POST':
        event.delete()
        messages.info(request, "Event deleted.")
        return redirect('event_list')
    return render(request, 'events/event_confirm_delete.html', {'event': event})


# =========================
# Dashboard (Admin/Organizer)
# =========================
@role_required(GROUP_ADMIN, GROUP_ORGANIZER, login_url='login')
def dashboard(request):
    today = timezone.now().date()
    counts = {
        'events': Event.objects.aggregate(
            total=Count('id'),
            upcoming=Count('id', filter=Q(date__gte=today)),
            past=Count('id', filter=Q(date__lt=today)),
        ),
        'categories': Category.objects.aggregate(total=Count('id')),
        'users': {
            'total': Event.participants.through.objects.count()  # total RSVPs
        }
    }

    data = Event.objects.select_related('category').prefetch_related('participants')
    t = request.GET.get('type', 'all')
    data_type = 'events'

    if t == 'upcoming':
        data = data.filter(date__gte=today)
        data_type = 'upcoming_events'
    elif t == 'past':
        data = data.filter(date__lt=today)
        data_type = 'past_events'
    elif t == 'categories':
        data = Category.objects.annotate(event_count=Count('events'))
        data_type = 'categories'

    return render(request, 'events/dashboard.html', {
        'counts': counts,
        'data': data,
        'data_type': data_type,
    })


# =========================
# RSVP (Participants/any logged in)
# =========================
@login_required
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
            from_email=settings.DEFAULT_FROM_EMAIL or settings.EMAIL_HOST_USER,
            recipient_list=[request.user.email] if request.user.email else [],
            fail_silently=True
        )

    return redirect('event_detail', id=event.id)


@login_required
def my_rsvped_events(request):
    rsvped_events = request.user.rsvped_events.all()
    return render(request, 'events/my_events.html', {'events': rsvped_events})


@login_required
def cancel_rsvp(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.user in event.participants.all():
        event.participants.remove(request.user)
        messages.info(request, "RSVP cancelled.")
    return redirect('participant-dashboard')  # ensure this URL exists or change name


# =========================
# Categories
# =========================
def category_list(request):
    categories = Category.objects.annotate(event_count=Count('events'))
    return render(request, 'events/category_list.html', {'categories': categories})


class CategoryCreateView(RoleRequiredMixin, CreateView):
    allowed_groups = (GROUP_ADMIN, GROUP_ORGANIZER)
    model = Category
    form_class = CategoryForm
    template_name = 'events/category_form.html'
    success_url = reverse_lazy('category_list')

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Category created.")
        return super().form_valid(form)


@role_required(GROUP_ADMIN, GROUP_ORGANIZER, login_url='login')
def category_update(request, id):
    category = get_object_or_404(Category, id=id)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Category updated.")
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'events/category_form.html', {'form': form})


@role_required(GROUP_ADMIN, GROUP_ORGANIZER, login_url='login')
def category_delete(request, id):
    category = get_object_or_404(Category, id=id)
    if request.method == 'POST':
        category.delete()
        messages.info(request, "Category deleted.")
        return redirect('category_list')
    return render(request, 'events/category_confirm_delete.html', {'category': category})


# =========================
# No permission + role redirect
# =========================
def no_permission(request):
    return render(request, 'no_permission.html')

@login_required
def dashboard_redirect(request):
    user = request.user
    if _in_groups(user, (GROUP_ADMIN,)):
        return redirect('admin-dashboard')  # define in urls.py or change target
    elif _in_groups(user, (GROUP_ORGANIZER,)):
        return redirect('dashboard')
    else:
        return redirect('participant-dashboard')
