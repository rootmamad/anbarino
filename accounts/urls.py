from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('logout/', views.logout_view, name='logout'),
    path('login/', views.login_view, name='login'),
    path('password_reset/', views.password_reset_view, name='password_reset'),
    path("profile/edit/", views.edit_user_view, name="edit_user"),
    path("staff/", views.staff_list, name="staff_list"),
    path("staff/add/", views.add_staff, name="add_staff"),
    path("staff/edit/<int:pk>/", views.edit_staff, name="edit_staff"),
    path("staff/delete/<int:pk>/", views.delete_staff, name="delete_staff"),
    path("staff/change_role/<int:pk>/", views.change_role, name="change_role"),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
