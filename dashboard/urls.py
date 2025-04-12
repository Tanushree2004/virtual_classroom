from django.urls import path
from .views import (
    dashboard_view, user_settings, landing_page, about, admin_dashboard, instructor_dashboard, student_dashboard,
    user_list,admin_register_view, add_user, edit_user, delete_user, custom_login, custom_logout, profile_view
)




urlpatterns = [
    path('', landing_page, name='landing_page'),
    path('about/', about, name='about'),
    path('settings/', user_settings, name='user_settings'),
    path('register/', admin_register_view, name='admin_register'),

    # ✅ Authentication URLs
    path('login/', custom_login, name='login'),
    path('logout/', custom_logout, name='logout'),
    path("profile/", profile_view, name="profile"),

    # ✅ Dashboard URLs
    path('dashboard/dashboard/', dashboard_view, name='dashboard_view'),
    path('dashboard/dashboard/admin/', admin_dashboard, name='admin_dashboard'),
    path('dashboard/dashboard/instructor/', instructor_dashboard, name='instructor_dashboard'),
    path('dashboard/dashboard/student/', student_dashboard, name='student_dashboard'),

    # ✅ User Management URLs
    path('dashboard/dashboard/users/', user_list, name='user_list'),
    path('dashboard/dashboard/users/add/', add_user, name='add_user'),
    path('dashboard/dashboard/users/edit/<int:user_id>/', edit_user, name='edit_user'),
    path('dashboard/dashboard/users/delete/<int:user_id>/', delete_user, name='delete_user'),
]
