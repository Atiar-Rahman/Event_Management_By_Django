from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count, Sum, Q
from django.http import JsonResponse
from django.utils import timezone
from .models import Event, Category, Participant
from .forms import EventForm, CategoryForm, ParticipantForm

# Event list with search, filter, optimized queries
def event_list(request):
    q = request.GET.get('q','').strip()
    category_id = request.GET.get('category')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    qs = Event.objects.select_related('category').prefetch_related('participants').annotate(num_participants=Count('participants'))

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

def event_create(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save()
            return redirect('event_app:event_detail', pk=event.pk)
    else:
        form = EventForm()
    return render(request, 'event_app/event_form.html', {'form': form, 'title':'Create Event'})

def event_update(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            return redirect('event_app:event_detail', pk=event.pk)
    else:
        form = EventForm(instance=event)
    return render(request, 'event_app/event_form.html', {'form': form, 'title':'Update Event'})

def event_delete(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        event.delete()
        return redirect('event_app:event_list')
    return render(request, 'event_app/confirm_delete.html', {'object': event})

# Category CRUD
def category_list(request):
    cats = Category.objects.all()
    return render(request, 'event_app/category_list.html', {'categories': cats})

def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('event_app:category_list')
    else:
        form = CategoryForm()
    return render(request, 'event_app/category_form.html', {'form': form})

def category_update(request, pk):
    cat = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=cat)
        if form.is_valid():
            form.save()
            return redirect('event_app:category_list')
    else:
        form = CategoryForm(instance=cat)
    return render(request, 'event_app/category_form.html', {'form': form})

def category_delete(request, pk):
    cat = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        cat.delete()
        return redirect('event_app:category_list')
    return render(request, 'event_app/confirm_delete.html', {'object': cat})

# Participant CRUD
def participant_list(request):
    parts = Participant.objects.all()
    return render(request, 'event_app/participant_list.html', {'participants': parts})

def participant_create(request):
    if request.method == 'POST':
        form = ParticipantForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('event_app:participant_list')
    else:
        form = ParticipantForm()
    return render(request, 'event_app/participant_form.html', {'form': form})

def participant_update(request, pk):
    part = get_object_or_404(Participant, pk=pk)
    if request.method == 'POST':
        form = ParticipantForm(request.POST, instance=part)
        if form.is_valid():
            form.save()
            return redirect('event_app:participant_list')
    else:
        form = ParticipantForm(instance=part)
    return render(request, 'event_app/participant_form.html', {'form': form})

def participant_delete(request, pk):
    part = get_object_or_404(Participant, pk=pk)
    if request.method == 'POST':
        part.delete()
        return redirect('event_app:participant_list')
    return render(request, 'event_app/confirm_delete.html', {'object': part})

# Organizer Dashboard
def organizer_dashboard(request):
    total_participants = Participant.objects.count()
    total_events = Event.objects.count()
    today = timezone.localdate()
    upcoming_events_count = Event.objects.filter(date__gt=today).count()
    past_events_count = Event.objects.filter(date__lt=today).count()

    todays_events = Event.objects.filter(date=today).select_related('category').prefetch_related('participants').annotate(num_participants=Count('participants'))

    context = {
        'total_participants': total_participants,
        'total_events': total_events,
        'upcoming_events': upcoming_events_count,
        'past_events': past_events_count,
        'todays_events': todays_events,
        'today': today,
    }
    return render(request, 'event_app/dashboard.html', context)

# API endpoint for interactive stats
def dashboard_stats_api(request):
    filter_type = request.GET.get('filter','all')
    today = timezone.localdate()
    qs = Event.objects.select_related('category').prefetch_related('participants').annotate(num_participants=Count('participants'))

    if filter_type == 'upcoming':
        qs = qs.filter(date__gte=today)
    elif filter_type == 'past':
        qs = qs.filter(date__lt=today)

    qs = qs.order_by('date')[:50]
    data = []
    for e in qs:
        data.append({
            'id': e.id,
            'name': e.name,
            'date': e.date.isoformat(),
            'time': e.time.isoformat() if e.time else '',
            'location': e.location,
            'category': e.category.name if e.category else '',
            'num_participants': e.num_participants
        })
    return JsonResponse({'events': data})
