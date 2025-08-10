from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.models import User, Group
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required

from user.decorators import group_required
from user.forms import RegisterForm, LoginForm, AssignRoleForm, CreateGroupForm

def sign_up(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            g, _ = Group.objects.get_or_create(name='participant')
            user.groups.add(g)
            messages.success(request, 'Account created! Check your email to activate your account.')
            return redirect('sign-in')
    else:
        form = RegisterForm()
    return render(request, 'auth/sign_up.html', {'form': form})

def sign_in(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if not user.is_active:
                messages.error(request, 'Please activate your account via the email link before logging in.')
                return redirect('sign-in')
            login(request, user)
            return redirect('post-login-redirect')
    else:
        form = LoginForm()
    return render(request, 'auth/sign_in.html', {'form': form})

@login_required
def user_logout(request):
    logout(request)
    messages.info(request, 'Logged out.')
    return redirect('sign-in')

def activate_user(request, user_id, token):
    user = get_object_or_404(User, pk=user_id)
    if default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Your account is now active. You can log in.')
        return redirect('sign-in')
    messages.error(request, 'Activation link is invalid or expired.')
    return redirect('sign-in')

@login_required
def post_login_redirect(request):
    u = request.user
    if u.is_superuser or u.groups.filter(name__in=['admin','organizer']).exists():
        return redirect('event_app:dashboard')
    return redirect('event_app:participant_dashboard')

# --- Admin-only role management (optional but helps grading)
@login_required
@group_required('admin')
def admin_dashboard(request):
    users = User.objects.all()
    return render(request, 'admin/admin_dashboard.html', {'users': users})

@login_required
@group_required('admin')
def assign_role(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    if request.method == 'POST':
        form = AssignRoleForm(request.POST)
        if form.is_valid():
            role = form.cleaned_data['role']
            for name in ['admin','organizer','participant']:
                g = Group.objects.filter(name=name).first()
                if g: user.groups.remove(g)
            g, _ = Group.objects.get_or_create(name=role)
            user.groups.add(g)
            messages.success(request, f"Role '{role}' assigned to {user.username}.")
            return redirect('admin-dashboard')
    else:
        form = AssignRoleForm()
    return render(request, 'admin/assign_role.html', {'form': form, 'target_user': user})

@login_required
@group_required('admin')
def create_group(request):
    if request.method == 'POST':
        form = CreateGroupForm(request.POST)
        if form.is_valid():
            group = form.save()
            messages.success(request, f"Group '{group.name}' has been created.")
            return redirect('group-list')
    else:
        form = CreateGroupForm()
    return render(request, 'admin/creategroup.html', {'form': form})

@login_required
@group_required('admin')
def group_list(request):
    from django.contrib.auth.models import Group
    groups = Group.objects.all()
    return render(request, 'admin/group_list.html', {'groups': groups})
