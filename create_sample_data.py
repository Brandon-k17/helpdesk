import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'helpdesk_project.settings')
django.setup()

from helpdeskapp.models import Utilisateur, Domaine, Demande

print("Création de données d'exemple...")

# Récupérer les utilisateurs créés
admin = Utilisateur.objects.get(username='admin')
technicien = Utilisateur.objects.get(username='technicien')

# Créer quelques clients de test
client1, created = Utilisateur.objects.get_or_create(
    username='client1',
    defaults={
        'nom': 'Moreau',
        'prenom': 'Marie',
        'email': 'marie.moreau@entreprise.com',
        'telephone': '01.11.22.33.44',
        'adresse': '789 Rue du Client, 33000 Bordeaux',
        'role': 'client'
    }
)
if created:
    client1.set_password('client123')
    client1.save()

client2, created = Utilisateur.objects.get_or_create(
    username='client2',
    defaults={
        'nom': 'Bernard',
        'prenom': 'Pierre',
        'email': 'pierre.bernard@entreprise.com',
        'telephone': '01.55.66.77.88',
        'adresse': '321 Boulevard du Commerce, 13000 Marseille',
        'role': 'client'
    }
)
if created:
    client2.set_password('client123')
    client2.save()

# Créer des domaines
domaines_data = [
    {'intitule': 'Informatique', 'description': 'Problèmes liés aux ordinateurs, logiciels et réseaux'},
    {'intitule': 'Téléphonie', 'description': 'Support pour les téléphones fixes et mobiles'},
    {'intitule': 'Imprimantes', 'description': 'Maintenance et dépannage des imprimantes'},
    {'intitule': 'Réseau', 'description': 'Connectivité internet et réseau local'},
    {'intitule': 'Sécurité', 'description': 'Antivirus, pare-feu et sécurité informatique'}
]

for domaine_data in domaines_data:
    domaine, created = Domaine.objects.get_or_create(
        intitule=domaine_data['intitule'],
        defaults={'description': domaine_data['description']}
    )
    if created:
        print(f"✅ Domaine créé: {domaine.intitule}")

# Créer des demandes d'exemple
demandes_data = [
    {
        'intitule': 'Problème de connexion internet',
        'description': 'Impossible de se connecter à internet depuis ce matin. Le voyant de la box clignote en rouge.',
        'client': client1,
        'technicien': technicien,
        'statut': 'en cours'
    },
    {
        'intitule': 'Imprimante ne fonctionne plus',
        'description': 'L\'imprimante HP du bureau 205 ne répond plus. Message d\'erreur "Bourrage papier" mais pas de papier coincé.',
        'client': client2,
        'technicien': technicien,
        'statut': 'en attente'
    },
    {
        'intitule': 'Installation nouveau logiciel',
        'description': 'Besoin d\'installer le logiciel de comptabilité sur 3 postes. Licence déjà achetée.',
        'client': client1,
        'technicien': None,
        'statut': 'en attente'
    },
    {
        'intitule': 'Mot de passe oublié',
        'description': 'Impossible de me connecter à ma session Windows. Mot de passe oublié après les vacances.',
        'client': client2,
        'technicien': technicien,
        'statut': 'terminée'
    },
    {
        'intitule': 'Écran noir au démarrage',
        'description': 'L\'ordinateur s\'allume mais l\'écran reste noir. Voyant d\'alimentation allumé.',
        'client': client1,
        'technicien': None,
        'statut': 'en attente'
    }
]

for demande_data in demandes_data:
    demande, created = Demande.objects.get_or_create(
        intitule=demande_data['intitule'],
        defaults={
            'description': demande_data['description'],
            'client': demande_data['client'],
            'technicien': demande_data['technicien'],
            'statut': demande_data['statut']
        }
    )
    if created:
        print(f"✅ Demande créée: {demande.intitule}")

print("\n" + "="*60)
print("📊 DONNÉES D'EXEMPLE CRÉÉES")
print("="*60)

print(f"\n👥 UTILISATEURS TOTAUX: {Utilisateur.objects.count()}")
print(f"   - Administrateurs: {Utilisateur.objects.filter(role='administrateur').count()}")
print(f"   - Techniciens: {Utilisateur.objects.filter(role='technicien').count()}")
print(f"   - Clients: {Utilisateur.objects.filter(role='client').count()}")

print(f"\n📁 DOMAINES: {Domaine.objects.count()}")
for domaine in Domaine.objects.all():
    print(f"   - {domaine.intitule}")

print(f"\n🎫 DEMANDES: {Demande.objects.count()}")
print(f"   - En attente: {Demande.objects.filter(statut='en attente').count()}")
print(f"   - En cours: {Demande.objects.filter(statut='en cours').count()}")
print(f"   - Terminées: {Demande.objects.filter(statut='terminée').count()}")

print("\n🎯 COMPTES CLIENTS SUPPLÉMENTAIRES:")
print("   client1 / client123 (Marie Moreau)")
print("   client2 / client123 (Pierre Bernard)")

print("\n" + "="*60)