import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'helpdesk_project.settings')
django.setup()

from helpdeskapp.models import Utilisateur
from django.contrib.auth.hashers import make_password

print("Création des utilisateurs de test...")

# Créer un administrateur
admin_user, created = Utilisateur.objects.get_or_create(
    username='admin',
    defaults={
        'nom': 'Dupont',
        'prenom': 'Jean',
        'email': 'admin@helpdesk.com',
        'telephone': '01.23.45.67.89',
        'adresse': '123 Rue de l\'Administration, 75001 Paris',
        'role': 'administrateur',
        'is_staff': True,
        'is_superuser': True,
        'is_active': True
    }
)

if created:
    admin_user.set_password('admin123')
    admin_user.save()
    print("✅ Administrateur créé avec succès!")
else:
    print("ℹ️ Administrateur existe déjà, mise à jour du mot de passe...")
    admin_user.set_password('admin123')
    admin_user.save()

# Créer un technicien
tech_user, created = Utilisateur.objects.get_or_create(
    username='technicien',
    defaults={
        'nom': 'Martin',
        'prenom': 'Sophie',
        'email': 'technicien@helpdesk.com',
        'telephone': '01.98.76.54.32',
        'adresse': '456 Avenue de la Technique, 69000 Lyon',
        'role': 'technicien',
        'is_staff': False,
        'is_superuser': False,
        'is_active': True
    }
)

if created:
    tech_user.set_password('tech123')
    tech_user.save()
    print("✅ Technicien créé avec succès!")
else:
    print("ℹ️ Technicien existe déjà, mise à jour du mot de passe...")
    tech_user.set_password('tech123')
    tech_user.save()

print("\n" + "="*60)
print("🎯 COMPTES DE TEST CRÉÉS")
print("="*60)

print("\n👨‍💼 ADMINISTRATEUR:")
print(f"   Nom d'utilisateur: admin")
print(f"   Mot de passe: admin123")
print(f"   Nom complet: Jean Dupont")
print(f"   Email: admin@helpdesk.com")
print(f"   Téléphone: 01.23.45.67.89")
print(f"   Rôle: Administrateur")
print(f"   Accès: Toutes les fonctionnalités")

print("\n🔧 TECHNICIEN:")
print(f"   Nom d'utilisateur: technicien")
print(f"   Mot de passe: tech123")
print(f"   Nom complet: Sophie Martin")
print(f"   Email: technicien@helpdesk.com")
print(f"   Téléphone: 01.98.76.54.32")
print(f"   Rôle: Technicien")
print(f"   Accès: Gestion des demandes")

print("\n🌐 CONNEXION:")
print(f"   URL: http://127.0.0.1:8000/accounts/login/")
print(f"   Utilisez les identifiants ci-dessus pour vous connecter")

print("\n📋 FONCTIONNALITÉS À TESTER:")
print("   Admin peut:")
print("   - Gérer tous les utilisateurs")
print("   - Créer/modifier/supprimer des domaines")
print("   - Voir toutes les demandes")
print("   - Accéder au dashboard admin")
print("")
print("   Technicien peut:")
print("   - Voir les demandes qui lui sont assignées")
print("   - Modifier le statut des demandes")
print("   - Créer de nouvelles demandes")

print("\n" + "="*60)