from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.admin_login_view, name='admin_login'),
    path('', views.admin_dashboard, name='admin_dashboard'),
    path('pending/', views.admin_pending, name='admin_pending'),
    path('pending/<int:user_id>/approve/', views.admin_approve_user, name='admin_approve_user'),
    path('pending/<int:user_id>/reject/', views.admin_reject_user, name='admin_reject_user'),

    path('notices/', views.admin_notices, name='admin_notices'),
    path('notices/add/', views.admin_notice_add, name='admin_notice_add'),
    path('notices/<int:notice_id>/edit/', views.admin_notice_edit, name='admin_notice_edit'),
    path('notices/<int:notice_id>/delete/', views.admin_notice_delete, name='admin_notice_delete'),
    path('members/', views.admin_members, name='admin_members'),
path('members/<int:user_id>/', views.admin_member_detail, name='admin_member_detail'),

path('trainers/', views.admin_trainers, name='admin_trainers'),
path('trainers/add/', views.admin_trainer_add, name='admin_trainer_add'),
path('trainers/<int:trainer_id>/edit/', views.admin_trainer_edit, name='admin_trainer_edit'),
path('trainers/<int:trainer_id>/delete/', views.admin_trainer_delete, name='admin_trainer_delete'),

path('packages/', views.admin_packages, name='admin_packages'),
path('packages/add/', views.admin_package_add, name='admin_package_add'),
path('packages/<int:package_id>/edit/', views.admin_package_edit, name='admin_package_edit'),
path('packages/<int:package_id>/delete/', views.admin_package_delete, name='admin_package_delete'),

path('subscriptions/', views.admin_subscriptions, name='admin_subscriptions'),
path('feedback/', views.admin_feedback, name='admin_feedback'),

path('members/add/', views.admin_add_member, name='admin_add_member'),
path('members/<int:user_id>/assign-subscription/', views.admin_assign_subscription, name='admin_assign_subscription'),
]