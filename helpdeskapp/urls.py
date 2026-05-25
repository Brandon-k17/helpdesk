from django.urls import path

from .views import (
    add_demande, add_domaine, add_user,
    connexion_view, dashboard_admin_view, delete_demande,
    delete_domaine, delete_user, deconnexion_view,
    detail_demande, detail_utilisateur, home_view,
    inscription_view, liste_demande, liste_domaines,
    list_utilisateur, update_demande, update_domaine,
    update_user, weather_api,
)

urlpatterns = [
    # DOMAINES
    path('domaine/', liste_domaines, name='list_domaines'),
    path('domaine/add/', add_domaine, name='add_domaine'),
    path('domaine/update/<int:id>/', update_domaine, name='update_domaine'),
    path('domaine/delete/<int:id>/', delete_domaine, name='delete_domaine'),

    # UTILISATEURS
    path('utilisateurs/', list_utilisateur, name='list_utilisateur'),
    path('utilisateurs/add/', add_user, name='add_user'),
    path('utilisateurs/<int:pk>/', detail_utilisateur, name='utilisateur_detail'),
    path('utilisateurs/<int:pk>/update/', update_user, name='update_user'),
    path('utilisateurs/<int:pk>/delete/', delete_user, name='delete_user'),

    # DEMANDES
    path('demande/', liste_demande, name='list_demande'),
    path('demande/add/', add_demande, name='add_demande'),
    path('demande/<int:pk>/update/', update_demande, name='update_demande'),
    path('demande/<int:pk>/delete/', delete_demande, name='delete_demande'),
    path('demande/<int:pk>/', detail_demande, name='detail_demande'),

    # ACCOUNTS
    path('', home_view, name='home'),
    path('accounts/register/', inscription_view, name='register'),
    path('accounts/login/', connexion_view, name='login'),
    path('accounts/logout/', deconnexion_view, name='logout'),
    path('dashboard-admin/', dashboard_admin_view, name='dashboard_admin'),

    # API
    path('api/weather/', weather_api, name='weather_api'),
]
