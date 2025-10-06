from django.shortcuts import render, redirect, get_object_or_404
from .forms import VehicleForm, PropertyForm
from django.contrib.auth.decorators import login_required
from .models import Vehicle, Property, Booking
from django.contrib import messages
from datetime import datetime
from django.db.models import Q 
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from PIL import Image
import imagehash
from .ml_utils import predict_rent


def home(request):
    latest_vehicles = Vehicle.objects.filter(is_available=True).order_by('-id')[:6]
    latest_properties = Property.objects.filter(is_available=True).order_by('-id')[:6]

    latest_listings = list(latest_vehicles) + list(latest_properties)

    
    for listing in latest_listings:
        listing.listing_type = listing.get_listing_type()

    context = {"latest_listings": latest_listings}
    return render(request, "listings/index.html", context)





@login_required
def add_vehicle(request):
    if request.method == 'POST':
        form = VehicleForm(request.POST, request.FILES)
        if form.is_valid():
            vehicle = form.save(commit=False)
            vehicle.owner = request.user  

            # ✅ Check for similar images
            if vehicle.image:
                img = Image.open(vehicle.image)
                uploaded_hash = imagehash.phash(img)

                existing_vehicles = Vehicle.objects.all()
                for v in existing_vehicles:
                    if v.image:
                        try:
                            existing_img = Image.open(v.image)
                            existing_hash = imagehash.phash(existing_img)
                            diff = uploaded_hash - existing_hash

                            if diff < 5:  # Threshold for similarity
                                messages.error(request, "Duplicate image detected! Upload a different photo.")
                                return redirect('add_vehicle')
                        except:
                            continue

            vehicle.save()
            return redirect('/')  
    else:
        form = VehicleForm()
    return render(request, 'listings/add_vehicle.html', {'form': form})



# ✅ Add Property Listing
@login_required
def add_property(request):
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            property = form.save(commit=False)
            property.owner = request.user  

            # ✅ Check for similar images
            if property.image:
                img = Image.open(property.image)
                uploaded_hash = imagehash.phash(img)

                existing_properties = Property.objects.all()
                for p in existing_properties:
                    if p.image:
                        try:
                            existing_img = Image.open(p.image)
                            existing_hash = imagehash.phash(existing_img)
                            diff = uploaded_hash - existing_hash

                            if diff < 5:  # Threshold for similarity
                                messages.error(request, "Duplicate image detected! Upload a different photo.")
                                return redirect('add_property')
                        except:
                            continue

            property.save()
            return redirect('/')
    else:
        form = PropertyForm()
    return render(request, 'listings/add_property.html', {'form': form})



def listings(request):
    category = request.GET.get('category', '')
    location = request.GET.get('location', '')

    vehicles = Vehicle.objects.filter(is_available=True)
    properties = Property.objects.filter(is_available=True)

    if location:
        vehicles = vehicles.filter(location__icontains=location)
        properties = properties.filter(address__icontains=location)

    if category == "vehicle":
        properties = Property.objects.none()
    elif category == "property":
        vehicles = Vehicle.objects.none()

    for prop in properties:
        prop.is_best_deal = False
        predicted = predict_rent(
            location=prop.address.split(',')[-1].strip(),  # Extract city
            bedrooms=prop.bedrooms,
            size=prop.size
        )
        if predicted and prop.price <= predicted:
            prop.is_best_deal = True
            prop.predicted_price = predicted  # For template display

    context = {
        "vehicles": vehicles,
        "properties": properties,
        "category": category,
        "location": location
    }
    return render(request, "listings/listings.html", context)


# ✅ Booking Function (Prevent Self-Booking)
@login_required
def book_listing(request, listing_type, listing_id):
    if listing_type == 'vehicle':
        listing = get_object_or_404(Vehicle, id=listing_id)
    else:
        listing = get_object_or_404(Property, id=listing_id)

    # ✅ Prevent users from booking their own listings
    if listing.owner == request.user:
        messages.error(request, "You cannot book your own listing.")
        return redirect('listings')

    if request.method == "POST":
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

       # Convert to date objects
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()

        # Prevent past dates
        if start_date_obj < datetime.today().date():
            messages.error(request, "Start date cannot be in the past.")
            return redirect('listings')


        # Prevent invalid date ranges
        if end_date_obj < start_date_obj:
            messages.error(request, "End date cannot be before start date.")
            return redirect('listings')

        # Calculate total price
        num_days = (end_date_obj - start_date_obj).days
        total_price = num_days * (listing.price_per_day if listing_type == 'vehicle' else listing.price)

        # Create Booking
        Booking.objects.create(
            user=request.user,
            vehicle=listing if listing_type == 'vehicle' else None,
            property=listing if listing_type == 'property' else None,
            start_date=start_date_obj,
            end_date=end_date_obj,
            total_price=total_price,
            status='pending'
        )

        messages.success(request, "Booking request sent successfully!")
        return redirect('listings')

    return render(request, 'listings/book_listing.html', {'listing': listing, 'listing_type': listing_type})


# ✅ Dashboard for Users
@login_required
def dashboard(request):
    user = request.user

    user_bookings = Booking.objects.filter(user=user)  # Bookings made by user
    owner_bookings = Booking.objects.filter(
        Q(vehicle__owner=user) | Q(property__owner=user)
    )  # Bookings received by user

    return render(request, 'listings/dashboard.html', {
        'user_bookings': user_bookings,
        'owner_bookings': owner_bookings,
    })


# ✅ Confirm Booking (Owner Only)
@login_required
def confirm_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if (booking.vehicle and booking.vehicle.owner == request.user) or (booking.property and booking.property.owner == request.user):
        booking.status = 'confirmed'
        booking.save()

        # Send real-time update
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "booking_updates",  # Group name
            {
                "type": "send_booking_update",
                "booking_id": booking.id,
                "status": "confirmed",
            }
        )

        messages.success(request, "Booking confirmed successfully.")
    return redirect('dashboard')



# ✅ Cancel Booking (Owner Only)
@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if (booking.vehicle and booking.vehicle.owner == request.user) or (booking.property and booking.property.owner == request.user):
        booking.status = 'canceled'
        booking.save()

        # Send real-time update
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "booking_updates",
            {
                "type": "send_booking_update",
                "booking_id": booking.id,
                "status": "canceled",
            }
        )

        messages.success(request, "Booking canceled successfully.")
    return redirect('dashboard')


# ✅ User Cancels Their Own Booking
@login_required
def user_cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    if booking.user == request.user:
        booking.status = 'canceled'
        booking.save()
        messages.success(request, "Your booking has been canceled.")
    else:
        messages.error(request, "You are not authorized to cancel this booking.")

    return redirect('dashboard')


# ✅ Delete Listing (Owner Only)
@login_required
def delete_listing(request, listing_type, listing_id):
    if listing_type == "vehicle":
        listing = get_object_or_404(Vehicle, id=listing_id, owner=request.user)
    elif listing_type == "property":
        listing = get_object_or_404(Property, id=listing_id, owner=request.user)
    else:
        messages.error(request, "Invalid listing type.")
        return redirect('listings')

    if request.method == "POST":
        listing.delete()
        messages.success(request, "Listing removed successfully.")
        return redirect('listings')

    return redirect('listings')

def listing_detail(request, listing_type, listing_id):
    if listing_type == "vehicle":
        listing = get_object_or_404(Vehicle, id=listing_id)
    else:
        listing = get_object_or_404(Property, id=listing_id)

    return render(request, "listings/listing_detail.html", {
        "listing": listing,
        "listing_type": listing_type
    })

@csrf_exempt
def check_availability(request):
    """API to check if a listing is available for the selected dates."""
    try:
        listing_type = request.GET.get('listing_type')
        listing_id = request.GET.get('listing_id')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        print(f"Received request: listing_type={listing_type}, listing_id={listing_id}, start_date={start_date}, end_date={end_date}")

        if not all([listing_type, listing_id, start_date, end_date]):
            return JsonResponse({'error': 'Missing parameters'}, status=400)

        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

        if listing_type == 'vehicle':
            listing = get_object_or_404(Vehicle, id=listing_id)
        elif listing_type == 'property':
            listing = get_object_or_404(Property, id=listing_id)
        else:
            return JsonResponse({'error': 'Invalid listing type'}, status=400)

        overlapping_bookings = Booking.objects.filter(
            start_date__lte=end_date,
            end_date__gte=start_date,
            status='confirmed'
        )

        if listing_type == 'vehicle':
            overlapping_bookings = overlapping_bookings.filter(vehicle=listing)
        else:
            overlapping_bookings = overlapping_bookings.filter(property=listing)

        print(f"Overlapping bookings count: {overlapping_bookings.count()}")

        if overlapping_bookings.exists():
            return JsonResponse({'available': False})
        return JsonResponse({'available': True})

    except Exception as e:
        print(f"Error in check_availability: {e}")
        return JsonResponse({'error': 'Server error'}, status=500)


