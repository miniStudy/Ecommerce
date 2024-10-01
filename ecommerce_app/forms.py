from ecommerce_app.models import *
from django import forms

class AdminForm(forms.ModelForm):
    class Meta:
        model = Admin
        fields = "__all__"
        labels = {
            'name': 'Full Name',
            'email': 'Email Address',
        }
