from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q
import imagehash
from PIL import Image

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    is_owner = models.BooleanField(default=False)  # True if user lists properties/cars

    def __str__(self):
        return self.user.username


class Vehicle(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.IntegerField()
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=255)
    image = models.ImageField(upload_to='vehicles/', blank=True, null=True)
    is_available = models.BooleanField(default=True)

    image_hash = models.CharField(max_length=100, blank=True, null=True)  # ✅ NEW field added

    def save(self, *args, **kwargs):
        # generate image hash when saving
        if self.image:
            img = Image.open(self.image)
            self.image_hash = str(imagehash.phash(img))
        super().save(*args, **kwargs)


    def get_listing_type(self):
        return "vehicle"


    def __str__(self):
        return f"{self.brand} {self.model} - {self.location}"


class Property(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    address = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    property_type = models.CharField(max_length=50, default='rent')  # Removed "sale"
    bedrooms = models.IntegerField()
    bathrooms = models.IntegerField()
    size = models.IntegerField(help_text="Size in square feet")
    image = models.ImageField(upload_to='properties/', blank=True, null=True)
    is_available = models.BooleanField(default=True)

    image_hash = models.CharField(max_length=100, blank=True, null=True)  # ✅ NEW field added

    def save(self, *args, **kwargs):
        # generate image hash when saving
        if self.image:
            img = Image.open(self.image)
            self.image_hash = str(imagehash.phash(img))
        super().save(*args, **kwargs)

    def get_listing_type(self):
        return "property"

    def __str__(self):
        return f"{self.title} - For Rent"

# 4️⃣ Booking Model (For Vehicle & Property Rentals)
class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('canceled', 'Canceled')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings")
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, null=True, blank=True)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def is_available(self):
        """Check if the listing is available for booking."""
        overlapping_bookings = Booking.objects.filter(
            Q(vehicle=self.vehicle) | Q(property=self.property),
            start_date__lte=self.end_date,
            end_date__gte=self.start_date,
            status='confirmed'
        )
        return not overlapping_bookings.exists()
    
