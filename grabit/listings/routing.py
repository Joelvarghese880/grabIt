from django.urls import path
from .consumers import BookingStatusConsumer

websocket_urlpatterns = [
    path("ws/booking_status/", BookingStatusConsumer.as_asgi()),
]
