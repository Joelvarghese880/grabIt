from django.urls import path
from .views import chat_room, send_message, chat_list  # Import the chat list view
from .views import dummy_payment

urlpatterns = [
    path("chat/<str:listing_type>/<int:listing_id>/", chat_room, name="chat_room"),
    path("chat/send/<str:listing_type>/<int:listing_id>/", send_message, name="send_message"),
    path("chat/", chat_list, name="chat_list"),
    path("payment/<int:booking_id>/", dummy_payment, name="dummy_payment"),
]
