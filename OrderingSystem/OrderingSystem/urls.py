from django.contrib import admin
from django.urls import path, include
from MSMEOrderingWebApp import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.login_view, name='login'),
    path('MSMEOrderingWebApp/', include('MSMEOrderingWebApp.urls')),
    path('admin/', admin.site.urls),
    path('verify-email/', views.verify_email, name='verify_email'),
    path('Logout/', views.logout_view, name='logout'),
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('update-cart/<int:cart_id>/', views.update_cart, name='update_cart'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('forgot-password_otp/', views.forgot_passwordotp, name='forgot_passwordotp'),
    path('forgot-password_reset/', views.forgot_password_reset, name='forgot_password_reset'),
    path('save_customization/', views.customization_settings, name='save_customization'),
    path('update-review-response/<int:review_id>/', views.update_review_response, name='update_review_response'),
    path('hide-review/<int:review_id>/', views.hide_review, name='hide_review'),
    path('show-review/<int:review_id>/', views.show_review, name='show_review'),
    path('customer-reviews/', views.customer_reviews, name='customer_reviews'),
    path('reviews/', views.customer_reviews, name='reviews_page'), 
    path('customer/online-payment/', views.customer_viewonlinepayment, name='customer_viewonlinepayment'),
    path('business/pending-orders/', views.partial_pending_orders, name='partial_pending_orders'),
    path('partial/pending-orders/', views.partial_pending_orders, name='partial_pending_orders'),
    path('partial/customer-notifications/', views.partial_customer_notifications, name='partial_customer_notifications'),
    path('update-order-status/', views.update_order_status, name='update_order_status'),
    path('partial/customer-notifications/', views.partial_customer_notifications, name='partial_customer_notifications'),
    path('notifications/', views.notifications_redirect, name='notifications'),
    path('', views.route_home, name='home'),

    path('reset_customization/', views.reset_customization, name='reset_customization'),
    path('mark-as-delivered/', views.mark_as_delivered, name='mark_as_delivered'),
    path("upload-logo/", views.upload_logo, name="upload_logo"),
    path("toggle-shop-status/", views.toggle_shop_status, name="toggle_shop_status"),
    ]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
