"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from accounts.views import register_view, LoginPage, LogoutPage
from services.views import ServiceListView, ServiceDetailView
from bookings import views_public as booking_public
from django.views.generic import TemplateView
from services import views_admin as admin_views
from accounts import views_admin as acc_admin
from bookings import views_admin as booking_admin
from reviews import views_public as review_public
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
    path("auth/register/", register_view, name="register"),
    path("auth/login/", LoginPage.as_view(), name="login"),
    path("auth/logout/", LogoutPage.as_view(), name="logout"),

    # Admin Barber
    path("dashboard/barbers/", acc_admin.barber_list, name="admin_barber_list"),
    path("dashboard/barbers/create/", acc_admin.barber_create, name="admin_barber_create"),
    path("dashboard/barbers/<int:pk>/edit/", acc_admin.barber_edit, name="admin_barber_edit"),
    path("dashboard/barbers/<int:pk>/delete/", acc_admin.barber_delete, name="admin_barber_delete"),

    # Service Public
    path("services/", ServiceListView.as_view(), name="service_list"),
    path("services/<int:pk>/", ServiceDetailView.as_view(), name="service_detail"),

    # Booking Public
    path("booking/step1/", booking_public.booking_step1, name="booking_step1"),
    path("booking/step2/<int:service_id>/", booking_public.booking_step2, name="booking_step2"),
    path("booking/step3/<int:service_id>/<int:barber_id>/", booking_public.booking_step3, name="booking_step3"),
    path("booking/confirm/<int:service_id>/<int:barber_id>/", booking_public.booking_confirm, name="booking_confirm"),
    path("booking/success/", booking_public.booking_online_success, name="booking_online_success"),
    path("my-bookings/", booking_public.my_bookings, name="my_bookings"),
    path("my-bookings/<int:pk>/edit/", booking_public.booking_edit, name="booking_edit"),
    path("my-bookings/<int:pk>/cancel/", booking_public.booking_cancel, name="booking_cancel"),

    # Admin Service
    path("dashboard/services/", admin_views.service_admin_list, name="admin_service_list"),
    path("dashboard/services/create/", admin_views.service_admin_create, name="admin_service_create"),
    path("dashboard/services/<int:pk>/edit/", admin_views.service_admin_update, name="admin_service_update"),
    path("dashboard/services/<int:pk>/delete/", admin_views.service_admin_delete, name="admin_service_delete"),

    # Admin Booking
    path("dashboard/", booking_admin.dashboard_home, name="admin_dashboard"),
    path("dashboard/bookings/", booking_admin.booking_admin_list, name="admin_booking_list"),
    path("dashboard/bookings/walkin/", booking_admin.booking_admin_walkin_create, name="admin_booking_walkin"),
    path("dashboard/bookings/<int:pk>/cancel/", booking_admin.booking_admin_cancel, name="admin_booking_cancel"),
    path("dashboard/bookings/<int:pk>/addon/", booking_admin.booking_admin_addon, name="admin_booking_addon"),

    # Review
    path("reviews/", review_public.reviews_page, name="reviews_page"),
    path("my-bookings/<int:booking_id>/review/", review_public.create_review_from_booking, name="review_create_from_booking",),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)