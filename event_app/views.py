from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count, Q
from django.http import JsonResponse
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

from .models import Event, Category
from .forms import EventForm, CategoryForm
from user.decorators import group_required

User = get_user_model()

# -------- Public: event list & detail --------
def event_list(request):
    q = request.GET.get('q','').strip()
    category_id = request.GET.get('category')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    qs = (Event.objects.select_related('category')
          .prefetch_related('participants')
          .annotate(num_participants=Count('participants')))

    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(location__icontains=q))
    if category_id:
        qs = qs.filter(category_id=category_id)
    if date_from:
        qs = qs.filter(date__gte=date_from)
    if date_to:
        qs = qs.filter(date__lte=date_to)

    categories = Category.objects.all()
    return render(request, 'event_app/event_list.html', {'events': qs, 'categories': categories, 'q': q})

def event_detail(request, pk):
    event = get_object_or_404(Event.objects.select_related('category').prefetch_related('participants'), pk=pk)
    return render(request, 'event_app/event_detail.html', {'event': event})

# -------- Event CRUD (admin & organizer) --------
@login_required
@group_required('admin', 'organizer')
def event_create(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save()
            messages.success(request, 'Event created successfully.')
            return redirect('event_app:event_detail', pk=event.pk)
    else:
        form = EventForm()
    return render(request, 'event_app/event_form.html', {'form': form, 'title':'Create Event'})

@login_required
@group_required('admin', 'organizer')
def event_update(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'Event updated.')
            return redirect('event_app:event_detail', pk=event.pk)
    else:
        form = EventForm(instance=event)
    return render(request, 'event_app/event_form.html', {'form': form, 'title':'Update Event'})

@login_required
@group_required('admin', 'organizer')
def event_delete(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        event.delete()
        messages.info(request, 'Event deleted.')
        return redirect('event_app:event_list')
    return render(request, 'event_app/confirm_delete.html', {'object': event})

# -------- Category CRUD (admin & organizer) --------
@login_required
@group_required('admin', 'organizer')
def category_list(request):
    cats = Category.objects.all()
    return render(request, 'event_app/category_list.html', {'categories': cats})

@login_required
@group_required('admin', 'organizer')
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category created.')
            return redirect('event_app:category_list')
    else:
        form = CategoryForm()
    return render(request, 'event_app/category_form.html', {'form': form})

@login_required
@group_required('admin', 'organizer')
def category_update(request, pk):
    cat = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=cat)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated.')
            return redirect('event_app:category_list')
    else:
        form = CategoryForm(instance=cat)
    return render(request, 'event_app/category_form.html', {'form': form})

@login_required
@group_required('admin', 'organizer')
def category_delete(request, pk):
    cat = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        cat.delete()
        messages.info(request, 'Category deleted.')
        return redirect('event_app:category_list')
    return render(request, 'event_app/confirm_delete.html', {'object': cat})

# -------- RSVP --------
@login_required
def rsvp_event(request, pk):
    event = get_object_or_404(Event, pk=pk)
    already = event.participants.filter(id=request.user.id).exists()
    event.participants.add(request.user)  # M2M ignores duplicates
    if already:
        messages.info(request, 'You already RSVPed to this event.')
    else:
        messages.success(request, 'RSVP confirmed! Check your email for confirmation.')
    return redirect('event_app:event_detail', pk=pk)

@login_required
def cancel_rsvp(request, pk):
    event = get_object_or_404(Event, pk=pk)
    event.participants.remove(request.user)
    messages.info(request, 'RSVP cancelled.')
    return redirect('event_app:event_detail', pk=pk)

# -------- Dashboards --------
@login_required
@group_required('organizer', 'admin')
def organizer_dashboard(request):
    today = timezone.localdate()
    unique_user_ids = Event.objects.values_list('participants', flat=True).distinct()
    total_participants = User.objects.filter(id__in=unique_user_ids).count()
    total_events = Event.objects.count()
    upcoming_events_count = Event.objects.filter(date__gt=today).count()
    past_events_count = Event.objects.filter(date__lt=today).count()

    todays_events = (Event.objects.filter(date=today)
                     .select_related('category')
                     .prefetch_related('participants')
                     .annotate(num_participants=Count('participants')))

    context = {
        'total_participants': total_participants,
        'total_events': total_events,
        'upcoming_events': upcoming_events_count,
        'past_events': past_events_count,
        'todays_events': todays_events,
        'today': today,
    }
    return render(request, 'event_app/dashboard.html', context)

@login_required
def participant_dashboard(request):
    my_events = (Event.objects.filter(participants=request.user)
                 .select_related('category')
                 .annotate(num_participants=Count('participants'))
                 .order_by('date', 'time'))
    return render(request, 'event_app/participant_dashboard.html', {'events': my_events})

# -------- Stats API (admin & organizer) --------
@login_required
@group_required('organizer', 'admin')
def dashboard_stats_api(request):
    filter_type = request.GET.get('filter','all')
    today = timezone.localdate()
    qs = (Event.objects.select_related('category')
          .prefetch_related('participants')
          .annotate(num_participants=Count('participants')))

    if filter_type == 'upcoming':
        qs = qs.filter(date__gte=today)
    elif filter_type == 'past':
        qs = qs.filter(date__lt=today)

    qs = qs.order_by('date')[:50]
    data = [{
        'id': e.id,
        'name': e.name,
        'date': e.date.isoformat(),
        'time': e.time.isoformat() if e.time else '',
        'location': e.location,
        'category': e.category.name if e.category else '',
        'num_participants': e.num_participants,
    } for e in qs]
    return JsonResponse({'events': data})
