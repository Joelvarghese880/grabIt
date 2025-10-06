from django import forms
from .models import Vehicle, Property

class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['title', 'description', 'brand', 'model', 'year', 'price_per_day', 'location', 'image', 'is_available']
    
    def __init__(self, *args, **kwargs):
        super(VehicleForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

# Property Listing Form (Only for Rentals)
class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = ['title', 'description', 'address', 'location','price', 'bedrooms', 'bathrooms', 'size', 'image', 'is_available']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'price': forms.NumberInput(attrs={'step': '0.01'}),
            'size': forms.NumberInput(attrs={'min': 0}),
        }

