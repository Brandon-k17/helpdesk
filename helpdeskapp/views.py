from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .forms import InscriptionForm, ConnexionForm, DomaineForm, DemandeForm
from .models import Utilisateur
from .models import Domaine, Utilisateur, Demande
from .forms import DomaineForm, DemandeForm
from .services import WeatherService


# ---------------------------
#       DOMAINES
# ---------------------------

def liste_domaines(request):
    domaines = Domaine.objects.all().order_by('id')
    return render(request, 'domaine/list.html', {'domaines': domaines})


def add_domaine(request):
    form = DomaineForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Le domaine a été ajouté avec succès.')
            return redirect('list_domaines')
        messages.error(request, 'Erreur lors de l\'ajout du domaine.')
    return render(request, 'domaine/form.html', {'form': form})


def update_domaine(request, id):
    domaine = get_object_or_404(Domaine, id=id)
    form = DomaineForm(request.POST or None, instance=domaine)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Le domaine a été modifié avec succès.')
            return redirect('list_domaines')
        messages.error(request, 'Erreur lors de la modification du domaine.')

    return render(request, 'domaine/form.html', {'form': form})


def delete_domaine(request, id):
    domaine = get_object_or_404(Domaine, id=id)

    if request.method == 'POST':
        domaine.delete()
        messages.success(request, 'Le domaine a été supprimé avec succès.')
        return redirect('list_domaines')

    return render(request, 'domaine/delete_confirm.html', {'domaine': domaine})


# ---------------------------
#       UTILISATEURS
# ---------------------------

def list_utilisateur(request):
    utilisateurs = Utilisateur.objects.all().order_by('-id')
    paginator = Paginator(utilisateurs, 10)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'utilisateurs/user_list.html', {
        'page_obj': page_obj,
        'utilisateurs': page_obj.object_list
    })


def detail_utilisateur(request, pk):
    utilisateur = get_object_or_404(Utilisateur, pk=pk)
    return render(request, 'utilisateurs/user_detail.html', {'utilisateur': utilisateur})


def add_user(request):
    if request.method == 'POST':
        nom = request.POST.get('nom')
        prenom = request.POST.get('prenom')
        telephone = request.POST.get('telephone')
        adresse = request.POST.get('adresse')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')

        if not all([nom, prenom, telephone, email, password, role]):
            messages.error(request, 'Veuillez remplir tous les champs obligatoires.')
            return render(request, 'utilisateurs/user_form.html', {'roles': Utilisateur.ROLES})

        try:
            utilisateur = Utilisateur.objects.create(
                nom=nom,
                prenom=prenom,
                telephone=telephone,
                adresse=adresse,
                email=email,
                password=password,
                role=role
            )
            messages.success(request, f'Utilisateur {utilisateur.nom} {utilisateur.prenom} créé avec succès !')
            return redirect('list_utilisateur')

        except Exception as e:
            messages.error(request, f'Erreur lors de la création : {str(e)}')

    return render(request, 'utilisateurs/user_form.html', {'roles': Utilisateur.ROLES})


def update_user(request, pk):
    utilisateur = get_object_or_404(Utilisateur, pk=pk)

    if request.method == 'POST':
        utilisateur.nom = request.POST.get('nom')
        utilisateur.prenom = request.POST.get('prenom')
        utilisateur.telephone = request.POST.get('telephone')
        utilisateur.adresse = request.POST.get('adresse')
        utilisateur.email = request.POST.get('email')

        password = request.POST.get('password')
        if password:
            utilisateur.password = password

        utilisateur.role = request.POST.get('role')

        try:
            utilisateur.save()
            messages.success(request, f'Utilisateur {utilisateur.nom} {utilisateur.prenom} modifié avec succès.')
            return redirect('utilisateur_detail', pk=utilisateur.pk)
        except Exception as e:
            messages.error(request, f'Erreur lors de la modification : {str(e)}')

    return render(request, 'utilisateurs/user_form.html', {
        'utilisateur': utilisateur,
        'roles': Utilisateur.ROLES,
        'is_update': True
    })


def delete_user(request, pk):
    utilisateur = get_object_or_404(Utilisateur, pk=pk)

    if request.method == 'POST':
        nom_complet = f"{utilisateur.nom} {utilisateur.prenom}"
        utilisateur.delete()
        messages.success(request, f'Utilisateur {nom_complet} supprimé avec succès !')
        return redirect('list_utilisateur')

    return render(request, 'utilisateurs/user_delete.html', {'utilisateur': utilisateur})


# ---------------------------
#       DEMANDES
# ---------------------------

def liste_demande(request):
    demandes = Demande.objects.all().order_by('-id')
    return render(request, 'demande/liste_demande.html', {'demandes': demandes})


def detail_demande(request, pk):
    demande = get_object_or_404(Demande, pk=pk)
    return render(request, 'demande/detail_demande.html', {'demande': demande})


def add_demande(request):
    if request.method == 'POST':
        form = DemandeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Demande créée avec succès.")
            return redirect('list_demande')
        else:
            messages.error(request, "Erreur lors de la création de la demande.")
    else:
        form = DemandeForm()
    
    return render(request, 'demande/form_demande.html', {
        'form': form,
        'titre': 'Nouvelle demande'
    })


def update_demande(request, pk):
    demande = get_object_or_404(Demande, pk=pk)
    
    if request.method == 'POST':
        form = DemandeForm(request.POST, instance=demande)
        if form.is_valid():
            form.save()
            messages.success(request, "Demande mise à jour avec succès.")
            return redirect('detail_demande', pk=demande.pk)
        else:
            messages.error(request, "Erreur lors de la mise à jour de la demande.")
    else:
        form = DemandeForm(instance=demande)
    
    return render(request, 'demande/form_demande.html', {
        'form': form,
        'demande': demande,
        'titre': 'Modifier la demande',
        'is_update': True
    })


def delete_demande(request, pk):
    demande = get_object_or_404(Demande, pk=pk)

    if request.method == 'POST':
        demande.delete()
        messages.success(request, 'Demande supprimée avec succès.')
        return redirect('list_demande')

    return render(request, 'demande/delete_demande.html', {'demande': demande})


# ---------------------------
#       ACCOUNTS
# ---------------------------

def inscription_view(request):
    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Inscription réussie ! Bienvenue.')
            return redirect('home')
        else:
            messages.error(request, 'Erreur lors de l\'inscription. Veuillez corriger les erreurs.')
    else:
        form = InscriptionForm()
    return render(request, 'accounts/register.html', {'form': form})


def connexion_view(request):
    if request.method == 'POST':
        form = ConnexionForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Bienvenue {user.prenom} !')
                return redirect('home')
        else:
            messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
    else:
        form = ConnexionForm()
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def deconnexion_view(request):
    logout(request)
    messages.info(request, 'Vous avez été déconnecté.')
    return redirect('login')


@login_required
def home_view(request):
    city = request.GET.get('city', 'Paris')
    weather_service = WeatherService()
    weather_data = weather_service.get_weather(city)
    return render(request, 'home.html', {'weather': weather_data, 'current_city': city})


def is_admin(user):
    return user.is_authenticated and user.is_admin()


@user_passes_test(is_admin)
def dashboard_admin_view(request):
    users = Utilisateur.objects.all()
    stats = {
        'total_users': users.count(),
        'clients': users.filter(role='client').count(),
        'techniciens': users.filter(role='technicien').count(),
        'admins': users.filter(role='admin').count(),
    }
    return render(request, 'dashboard_admin.html', {'users': users, 'stats': stats})


# Weather API endpoint
@login_required
def weather_api(request):
    """API endpoint for weather data"""
    from django.http import JsonResponse
    
    city = request.GET.get('city', 'Paris')
    weather_service = WeatherService()
    weather_data = weather_service.get_weather(city)
    
    if weather_data:
        return JsonResponse({'success': True, 'data': weather_data})
    else:
        return JsonResponse({'success': False, 'error': 'Unable to fetch weather data'})
