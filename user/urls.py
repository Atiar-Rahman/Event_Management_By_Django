from django.urls import path
from user.views import (
    sign_up, sign_in, user_logout, activate_user,
    post_login_redirect, admin_dashboard, assign_role, create_group, group_list
)

urlpatterns = [
    path('sign-up/', sign_up, name='sign-up'),
    path('sign-in/', sign_in, name='sign-in'),
    path('logout/', user_logout, name='logout'),
    path('activate/<int:user_id>/<str:token>/', activate_user, name='activate-user'),
    path('post-login-redirect/', post_login_redirect, name='post-login-redirect'),

    path('admin/dashboard/', admin_dashboard, name='admin-dashboard'),
    path('admin/<int:user_id>/assign-role/', assign_role, name='assign-role'),
    path('admin/create-group/', create_group, name='create-group'),
    path('admin/groups/', group_list, name='group-list'),
]
