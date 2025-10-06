from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import ChatMessage
from listings.models import Vehicle, Property, Booking
from django.db.models import Q

@login_required
def chat_room(request, listing_type, listing_id):
    if listing_type == "vehicle":
        listing = get_object_or_404(Vehicle, id=listing_id)
        messages = ChatMessage.objects.filter(vehicle=listing)
    elif listing_type == "property":
        listing = get_object_or_404(Property, id=listing_id)
        messages = ChatMessage.objects.filter(property=listing)
    else:
        return JsonResponse({"error": "Invalid listing type"}, status=400)

    return render(request, "chat/chat_room.html", {
        "listing": listing,
        "messages": messages,
        "listing_type": listing_type,
        "listing_id": listing_id
    })

@login_required
def send_message(request, listing_type, listing_id):
    if request.method == "POST":
        message_text = request.POST.get("message", "").strip()
        if not message_text:
            return JsonResponse({"error": "Message cannot be empty"}, status=400)

        if listing_type == "vehicle":
            listing = get_object_or_404(Vehicle, id=listing_id)
            new_message = ChatMessage.objects.create(
                sender=request.user,
                receiver=listing.owner,
                vehicle=listing,
                message=message_text
            )
        elif listing_type == "property":
            listing = get_object_or_404(Property, id=listing_id)
            new_message = ChatMessage.objects.create(
                sender=request.user,
                receiver=listing.owner,
                property=listing,
                message=message_text
            )
        else:
            return JsonResponse({"error": "Invalid listing type"}, status=400)

        return JsonResponse({"success": True, "message": message_text})

    return JsonResponse({"error": "Invalid request"}, status=400)

@login_required
def chat_list(request):
    user = request.user

    # Fetch chat messages where user is either sender or receiver, sorted by latest timestamp
    chats = ChatMessage.objects.filter(Q(sender=user) | Q(receiver=user)).order_by("-timestamp")

    chat_partners = []

    for chat in chats:
        # Identify the other user in the chat
        other_user = chat.receiver if chat.sender == user else chat.sender

        # Avoid duplicate conversations
        if any(entry[0] == other_user for entry in chat_partners):
            continue

        # Determine listing type and ID
        listing_type = "vehicle" if chat.vehicle else "property" if chat.property else None
        listing_id = chat.vehicle.id if chat.vehicle else chat.property.id if chat.property else None

        if listing_type and listing_id:
            chat_partners.append((other_user, listing_type, listing_id))

    return render(request, "chat/chat_list.html", {"chat_users": chat_partners})

def dummy_payment(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, status="confirmed")
    return render(request, "chat/dummy_payment.html", {"booking": booking})