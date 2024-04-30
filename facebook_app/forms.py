from django import forms
from .models import FaceBookUsers, Photos


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput())
    CHOICES = [
        ('Female', 'Female'),
        ('Male', 'Male'),
        ('Custom', 'Custom'),
     ]
    gender = forms.ChoiceField(choices=CHOICES)
    class Meta:
        model = FaceBookUsers
        fields = ['first_name', 'last_name', 'phone_num', 'email', 'password', 'birthday', 'gender']

class LoginForm(forms.Form):
    email = forms.EmailField(label='Email')
    password = forms.CharField(label='Password', widget=forms.PasswordInput())

class OtherProfileForm(forms.Form):
    username = forms.CharField(label='Username', max_length=100)

class ChangeInfoForm(forms.Form):
    change_info = forms.CharField(label='Change Info', max_length=100)
    

class ChangeGenderForm(forms.Form):
    CHOICES = [
        ('Female', 'Female'),
        ('Male', 'Male'),
        ('Custom', 'Custom'),
     ]
    gender = forms.ChoiceField(choices=CHOICES)


class ChangeEmailForm(forms.Form):
    email = forms.EmailField(max_length=254)


class ChangePhoneForm(forms.Form):
    phone = forms.IntegerField()


class AddPostForm(forms.Form):
    post = forms.CharField(label='post', max_length=1000)


class ChangePasswordForm(forms.Form):
    password = forms.CharField(label='Password', widget=forms.PasswordInput())


class ChangeUsernameForm(forms.Form):
    username = forms.CharField(label='Username')


class ChangeBirthdayForm(forms.Form):
    birthday = forms.DateField(label='Birthday')


class PhotoForm(forms.ModelForm):
    class Meta:
        model = Photos
        fields = ['image']