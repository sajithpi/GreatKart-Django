from mimetypes import init
from charset_normalizer import models
from .models import Account,UserProfile
from django import forms


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={
            'placeholder' : 'Enter Password',
            'class' : 'form-control'
        }
    ))
    confirm_password = forms.CharField(widget=forms.PasswordInput(
        attrs={
            'placeholder' : 'Confirm Password',
            'class' : 'form-control'
        }
    ))
    class Meta:
        model = Account
        fields = ['first_name','last_name','phone_number','email','password']

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['placeholder'] = 'Enter First tName'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Enter Last Name'
        self.fields['email'].widget.attrs['placeholder'] = 'Enter Email'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Enter Phone number'
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
            

    def clean(self):
        cleaned_data = super(RegistrationForm,self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password != confirm_password:
            raise forms.ValidationError(
                "Passsword does not match"
            )
class UserForm(forms.ModelForm):
   
    class Meta:
        model = Account
        fields = ['first_name','last_name','phone_number']


    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        for fields in self.fields:
            self.fields[fields].widget.attrs['class'] = 'form-control'  

class UserProfileForm(forms.ModelForm):
    profile_picture = forms.ImageField(required = False, error_messages = {'invalid' : ('Image Files Only')}, widget=forms.FileInput)
    class Meta:
        model = UserProfile
        fields = ['address_line1','address_line2','profile_picture','city','state','country']

        
    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        for fields in self.fields:
            self.fields[fields].widget.attrs['class'] = 'form-control'
        