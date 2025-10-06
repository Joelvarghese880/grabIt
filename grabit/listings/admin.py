from django.contrib import admin
from .models import UserProfile, Vehicle, Property, Booking

admin.site.register(UserProfile)
admin.site.register(Vehicle)
admin.site.register(Property)
admin.site.register(Booking)
