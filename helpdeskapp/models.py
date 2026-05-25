from django.db import models
from django.contrib.auth.models import AbstractUser

class Utilisateur(AbstractUser):
    ROLES = [
        ('client', 'Client'),
        ('technicien', 'Technicien'),
        ('administrateur', 'Administrateur'),
    ]
    
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=15, blank=True)
    adresse = models.TextField(blank=True)
    email = models.EmailField()
    role = models.CharField(max_length=20, choices=ROLES, default='client')
    
    def __str__(self):
        return f"{self.nom} {self.prenom} ({self.role})"
    
    def is_admin(self):
        return self.role == 'administrateur'
    
    def get_role_display(self):
        return dict(self.ROLES).get(self.role, self.role)

class Domaine(models.Model): 
    intitule = models.CharField(max_length=100)
    description = models.TextField()
    
    def __str__(self):
        return f"{self.intitule}"

class Demande(models.Model):
    STATUT = [
        ('en attente', 'En attente'),
        ('en cours', 'En cours'),
        ('terminée', 'Terminée'),
    ]
    
    client = models.ForeignKey(
        Utilisateur,
        on_delete=models.CASCADE,
        related_name='client_demandes',
        limit_choices_to={'role': 'client'}
    )
    
    technicien = models.ForeignKey(
        Utilisateur,
        on_delete=models.CASCADE,
        related_name='technicien_demandes', 
        limit_choices_to={'role': 'technicien'},
        null=True,
        blank=True
    )
    
    intitule = models.CharField(max_length=100)
    description = models.TextField()
    statut = models.CharField(max_length=20, choices=STATUT, default='en attente')
    datedemande = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f" {self.client} ({self.statut})"