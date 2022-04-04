from django import forms
from .models import Account

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs ={
        'placeholder' : "Enter Password",
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder' : "Confirm Password",
    }))
    class Meta:
        model = Account
        fields = [
            'first_name',
            'last_name',
            'email',
            'password',
            'phone_number'
        ]
    def __init__(self,*args,**kwargs):
        super(RegistrationForm,self).__init__(*args,**kwargs)
        self.fields['first_name'].widget.attrs['placeholder'] = 'Enter First Name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Enter Last Name'
        self.fields['email'].widget.attrs['placeholder'] = 'Enter Email Address'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Enter Phone Number'
        for feild in self.fields:
            self.fields[feild].widget.attrs['class'] = 'form-control'
    
    def clean(self):
        cleaned_data = super(RegistrationForm,self).clean()
        password = cleaned_data['password']
        confirm_password = cleaned_data['confirm_password']
        
        if password!=confirm_password:
            raise forms.ValidationError(
                "The password didn't match"
            )
    
class AdminRegistrationForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput(attrs ={
        'placeholder' : "Enter Password",
    }))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder' : "Confirm Password",
    }))
    class Meta:
        model = Account
        fields = [
            'first_name',
            'last_name',
            'email',
            'password',
            'phone_number'
        ]
        