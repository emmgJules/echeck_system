from django import forms
from .models import UserProfile

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_picture']

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        self.fields['profile_picture'].widget.attrs.update({
            'class': 'form-control-file'
        })

from django import forms
from .models import Person

class PersonForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = '__all__'  # Include all fields from the model

    def __init__(self, *args, **kwargs):
        super(PersonForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control'
            })

from django import forms
from django.contrib.auth.models import User

class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Password', 
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        min_length=8
    )
    password2 = forms.CharField(
        label='Confirm Password', 
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    is_staff = forms.BooleanField(required=False, label='Staff Status', widget=forms.CheckboxInput(attrs={'class': 'form-control'}))
    is_superuser = forms.BooleanField(required=False, label='Superuser Status', widget=forms.CheckboxInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            self.add_error('password2', "Passwords don't match")

        if password1 and len(password1) < 8:
            self.add_error('password1', "Password must be at least 8 characters long.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
            user.is_staff = self.cleaned_data.get('is_staff')
            user.is_superuser = self.cleaned_data.get('is_superuser')
            user.save()
        return user
