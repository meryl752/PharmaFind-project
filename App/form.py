from django import forms
from .models import User
from django.contrib.auth import get_user_model

User = get_user_model()


class UserForm(forms.ModelForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Votre nom d\'utilisateur'})
    )
    password = forms.CharField(widget=forms.PasswordInput)

    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Enter your firstname'})
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Enter your lastname'})
    )
    tel = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': '+ 229'})
    )
    email = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Enter your email'})
    )
   
    
    class Meta:
        model = User 
        fields = ['username', 'first_name', 'last_name', 'tel', 'address', 'city', 'email','sexe', 'password',]


    def save(self, commit=True):
        user = super().save(commit=False)
        # Hashage du mot de passe
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user    




    def clean_email(self):
        email = self.cleaned_data['email']  
        if User.objects.filter(email = email).exists():
            raise forms.ValidationError("Cet email est déjà utilisé !")
        return email
    
    def clean_username(self):
        username = self.cleaned_data['username']  
        if User.objects.filter(username = username).exists():
            raise forms.ValidationError("Ce nom d'utilisateur est déjà utilisé !")
        return username
    
    def clean_tel(self):
        tel = self.cleaned_data['tel']  
        if User.objects.filter(tel = tel).exists():
            raise forms.ValidationError("Ce nom N° de téléphone n'est pas le votre car déjà utilisé !")
        return tel
    

class LoginForm(forms.Form):
    email = forms.EmailField(label="Entrer votre email", max_length=50)
    password = forms.CharField(label="Mot de passe", widget=forms.PasswordInput)

class SearchForm(forms.Form) :
    query = forms.CharField(label='Search for a product or a pharmacy..!')
    category = forms.CharField(label='Search for a product or a pharmacy..!')

class PharmacyLoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'placeholder': 'Email pharmacie',
        'class': 'form-input'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Mot de passe',
        'class': 'form-input'
    }))
