from .models import *
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Utilisateur

class InscriptionForm(UserCreationForm):
    nom = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'Nom'
        })
    )
    prenom = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'Prénom'
        })
    )
    adresse = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'Adresse'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'Email'
        })
    )
    telephone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'Téléphone'
        })
    )
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'Nom d\'utilisateur'
        })
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'Mot de passe'
        })
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'Confirmer le mot de passe'
        })
    )
    
    class Meta:
        model = Utilisateur
        fields = ['username', 'nom', 'prenom', 'adresse', 'email', 'telephone', 'password1', 'password2']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.nom = self.cleaned_data['nom']
        user.prenom = self.cleaned_data['prenom']
        user.adresse = self.cleaned_data['adresse']
        user.telephone = self.cleaned_data['telephone']
        user.role = 'client'  # Par défaut, nouveau utilisateur = client
        if commit:
            user.save()
        return user


class ConnexionForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'Nom d\'utilisateur'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'Mot de passe'
        })
    )

class DomaineForm(forms.ModelForm):
    class Meta:
        model = Domaine
        fields = ['intitule', 'description']
        widgets = {
            'intitule': forms.TextInput(attrs= {
                'class': 'input w-full',
                'placeholder': 'Entrer un domaine'
            }),
            'description': forms.Textarea(attrs= {
                'class': 'textarea w-full h-24',
                'placeholder': 'Décrire en quelques mots le domaine'
            })
        }


class DemandeForm(forms.ModelForm):
    class Meta:
        model = Demande
        fields = ['intitule', 'description', 'client', 'technicien']
        widgets = {
            'intitule': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Titre de la demande'
            }),
            'description': forms.Textarea(attrs={
                'class': 'textarea textarea-bordered w-full h-32',
                'placeholder': 'Description détaillée de la demande'
            }),
            'client': forms.Select(attrs={
                'class': 'select select-bordered w-full'
            }),
            'technicien': forms.Select(attrs={
                'class': 'select select-bordered w-full'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['client'].queryset = Utilisateur.objects.filter(role='client')
        self.fields['technicien'].queryset = Utilisateur.objects.filter(role='technicien')
        self.fields['technicien'].required = False