from django.urls import path
from .views import home, add_vehicle, add_property, listings, book_listing, dashboard, confirm_booking, cancel_booking, user_cancel_booking, delete_listing, listing_detail, check_availability
from . import views
urlpatterns = [
    path('', home, name='home'),
    path('add-vehicle/', add_vehicle, name='add_vehicle'),
    path('add-property/', add_property, name='add_property'),
    path('listings/', listings, name='listings'),
    path('book/<str:listing_type>/<int:listing_id>/', book_listing, name='book_listing'),
    path('dashboard/', dashboard, name='dashboard'),
    path('booking/confirm/<int:booking_id>/', confirm_booking, name='confirm_booking'),
    path('booking/cancel/<int:booking_id>/', cancel_booking, name='cancel_booking'),
    path('booking/user_cancel/<int:booking_id>/', user_cancel_booking, name='user_cancel_booking'),
    path('delete/<str:listing_type>/<int:listing_id>/', delete_listing, name='delete_listing'), 
    path('<str:listing_type>/<int:listing_id>/', listing_detail, name='listing_detail'),
    path('check_availability/', check_availability, name="check_availability"),
]
