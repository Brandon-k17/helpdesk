from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch, MagicMock
from django.core.cache import cache

from .models import Utilisateur, Domaine, Demande
from .forms import InscriptionForm, DomaineForm, DemandeForm
from .services import WeatherService


# -------------------------------------------------------
#  Helpers
# -------------------------------------------------------

def make_client(**kwargs):
    defaults = dict(username='client1', nom='Dupont', prenom='Jean',
                    email='client@test.com', role='client')
    defaults.update(kwargs)
    u = Utilisateur(**defaults)
    u.set_password('testpass123')
    u.save()
    return u

def make_technicien(**kwargs):
    defaults = dict(username='tech1', nom='Martin', prenom='Paul',
                    email='tech@test.com', role='technicien')
    defaults.update(kwargs)
    u = Utilisateur(**defaults)
    u.set_password('testpass123')
    u.save()
    return u

def make_admin(**kwargs):
    defaults = dict(username='admin1', nom='Admin', prenom='Super',
                    email='admin@test.com', role='administrateur')
    defaults.update(kwargs)
    u = Utilisateur(**defaults)
    u.set_password('testpass123')
    u.save()
    return u


# -------------------------------------------------------
#  Model Tests
# -------------------------------------------------------

class UtilisateurModelTest(TestCase):

    def test_str(self):
        u = make_client()
        self.assertEqual(str(u), 'Dupont Jean (client)')

    def test_is_admin_false_for_client(self):
        u = make_client()
        self.assertFalse(u.is_admin())

    def test_is_admin_true_for_admin(self):
        u = make_admin()
        self.assertTrue(u.is_admin())

    def test_get_role_display(self):
        u = make_client()
        self.assertEqual(u.get_role_display(), 'Client')

        u.role = 'technicien'
        self.assertEqual(u.get_role_display(), 'Technicien')

        u.role = 'administrateur'
        self.assertEqual(u.get_role_display(), 'Administrateur')

    def test_default_role_is_client(self):
        u = Utilisateur(username='newuser', nom='A', prenom='B', email='a@b.com')
        u.set_password('pass')
        u.save()
        self.assertEqual(u.role, 'client')


class DomaineModelTest(TestCase):

    def test_str(self):
        d = Domaine.objects.create(intitule='Réseau', description='Problèmes réseau')
        self.assertEqual(str(d), 'Réseau')

    def test_create_domaine(self):
        d = Domaine.objects.create(intitule='Matériel', description='Pannes matérielles')
        self.assertEqual(Domaine.objects.count(), 1)
        self.assertEqual(d.intitule, 'Matériel')


class DemandeModelTest(TestCase):

    def setUp(self):
        self.client_user = make_client()
        self.tech = make_technicien()

    def test_create_demande(self):
        d = Demande.objects.create(
            intitule='Problème réseau',
            description='Pas de connexion',
            client=self.client_user,
            technicien=self.tech
        )
        self.assertEqual(d.statut, 'en attente')
        self.assertEqual(d.intitule, 'Problème réseau')

    def test_technicien_optional(self):
        d = Demande.objects.create(
            intitule='Problème imprimante',
            description='Imprimante hors service',
            client=self.client_user
        )
        self.assertIsNone(d.technicien)

    def test_str(self):
        d = Demande.objects.create(
            intitule='Test',
            description='Desc',
            client=self.client_user
        )
        self.assertIn('en attente', str(d))

    def test_delete_cascade(self):
        Demande.objects.create(
            intitule='Test cascade',
            description='Desc',
            client=self.client_user
        )
        self.client_user.delete()
        self.assertEqual(Demande.objects.count(), 0)


# -------------------------------------------------------
#  Form Tests
# -------------------------------------------------------

class InscriptionFormTest(TestCase):

    def _valid_data(self, **overrides):
        data = {
            'username': 'newuser',
            'nom': 'Durand',
            'prenom': 'Marie',
            'email': 'marie@test.com',
            'telephone': '0600000000',
            'adresse': '1 rue de la Paix',
            'password1': 'Str0ngPass!',
            'password2': 'Str0ngPass!',
        }
        data.update(overrides)
        return data

    def test_valid_form(self):
        form = InscriptionForm(data=self._valid_data())
        self.assertTrue(form.is_valid(), form.errors)

    def test_password_mismatch(self):
        form = InscriptionForm(data=self._valid_data(password2='WrongPass!'))
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_missing_required_fields(self):
        form = InscriptionForm(data=self._valid_data(username='', nom=''))
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        self.assertIn('nom', form.errors)

    def test_save_sets_role_client(self):
        form = InscriptionForm(data=self._valid_data())
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.role, 'client')

    def test_duplicate_username(self):
        make_client(username='existinguser')
        form = InscriptionForm(data=self._valid_data(username='existinguser'))
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)


class DomaineFormTest(TestCase):

    def test_valid_form(self):
        form = DomaineForm(data={'intitule': 'Réseau', 'description': 'Problèmes réseau'})
        self.assertTrue(form.is_valid())

    def test_missing_intitule(self):
        form = DomaineForm(data={'intitule': '', 'description': 'Desc'})
        self.assertFalse(form.is_valid())
        self.assertIn('intitule', form.errors)


class DemandeFormTest(TestCase):

    def setUp(self):
        self.client_user = make_client()
        self.tech = make_technicien()

    def test_valid_form_without_technicien(self):
        form = DemandeForm(data={
            'intitule': 'Problème réseau',
            'description': 'Pas de connexion',
            'client': self.client_user.pk,
            'technicien': ''
        })
        self.assertTrue(form.is_valid(), form.errors)

    def test_valid_form_with_technicien(self):
        form = DemandeForm(data={
            'intitule': 'Problème réseau',
            'description': 'Pas de connexion',
            'client': self.client_user.pk,
            'technicien': self.tech.pk
        })
        self.assertTrue(form.is_valid(), form.errors)

    def test_client_queryset_only_clients(self):
        form = DemandeForm()
        qs = form.fields['client'].queryset
        self.assertTrue(all(u.role == 'client' for u in qs))

    def test_technicien_queryset_only_techniciens(self):
        form = DemandeForm()
        qs = form.fields['technicien'].queryset
        self.assertTrue(all(u.role == 'technicien' for u in qs))


# -------------------------------------------------------
#  View Tests
# -------------------------------------------------------

@patch('helpdeskapp.views.WeatherService')
class AuthViewTest(TestCase):

    def setUp(self):
        self.http_client = Client()
        self.user = make_client()

    def test_register_page_get(self, _):
        response = self.http_client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register.html')

    def test_register_creates_user(self, _):
        response = self.http_client.post(reverse('register'), {
            'username': 'newuser',
            'nom': 'Durand',
            'prenom': 'Marie',
            'email': 'marie@test.com',
            'telephone': '0600000000',
            'adresse': '1 rue de la Paix',
            'password1': 'Str0ngPass!',
            'password2': 'Str0ngPass!',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Utilisateur.objects.filter(username='newuser').exists())

    def test_login_page_get(self, _):
        response = self.http_client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')

    def test_login_valid_credentials(self, _):
        response = self.http_client.post(reverse('login'), {
            'username': 'client1',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))

    def test_login_invalid_credentials(self, _):
        response = self.http_client.post(reverse('login'), {
            'username': 'client1',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)

    def test_home_requires_login(self, _):
        response = self.http_client.get(reverse('home'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('home')}")

    def test_home_accessible_when_logged_in(self, mock_weather_cls):
        mock_weather_cls.return_value.get_weather.return_value = None
        self.http_client.login(username='client1', password='testpass123')
        response = self.http_client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_logout(self, _):
        self.http_client.login(username='client1', password='testpass123')
        response = self.http_client.get(reverse('logout'))
        self.assertRedirects(response, reverse('login'))


@patch('helpdeskapp.views.WeatherService')
class DemandeViewTest(TestCase):

    def setUp(self):
        self.http_client = Client()
        self.client_user = make_client()
        self.tech = make_technicien()
        self.http_client.login(username='client1', password='testpass123')

    def test_liste_demande(self, _):
        response = self.http_client.get(reverse('list_demande'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'demande/liste_demande.html')

    def test_add_demande(self, _):
        response = self.http_client.post(reverse('add_demande'), {
            'intitule': 'Problème réseau',
            'description': 'Pas de connexion internet',
            'client': self.client_user.pk,
            'technicien': ''
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Demande.objects.count(), 1)

    def test_detail_demande(self, _):
        demande = Demande.objects.create(
            intitule='Test',
            description='Desc',
            client=self.client_user
        )
        response = self.http_client.get(reverse('detail_demande', args=[demande.pk]))
        self.assertEqual(response.status_code, 200)

    def test_delete_demande(self, _):
        demande = Demande.objects.create(
            intitule='Test',
            description='Desc',
            client=self.client_user
        )
        response = self.http_client.post(reverse('delete_demande', args=[demande.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Demande.objects.count(), 0)


@patch('helpdeskapp.views.WeatherService')
class UtilisateurViewTest(TestCase):

    def setUp(self):
        self.http_client = Client()
        self.admin = make_admin()
        self.user = make_client()
        self.http_client.login(username='admin1', password='testpass123')

    def test_list_utilisateur(self, _):
        response = self.http_client.get(reverse('list_utilisateur'))
        self.assertEqual(response.status_code, 200)

    def test_detail_utilisateur(self, _):
        response = self.http_client.get(reverse('utilisateur_detail', args=[self.user.pk]))
        self.assertEqual(response.status_code, 200)

    def test_add_user_get(self, _):
        response = self.http_client.get(reverse('add_user'))
        self.assertEqual(response.status_code, 200)

    def test_add_user_post(self, _):
        response = self.http_client.post(reverse('add_user'), {
            'nom': 'Nouveau', 'prenom': 'User',
            'telephone': '0600000001', 'adresse': '1 rue test',
            'email': 'new@test.com', 'password': 'pass123',
            'role': 'client'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Utilisateur.objects.filter(email='new@test.com').exists())

    def test_add_user_missing_fields(self, _):
        response = self.http_client.post(reverse('add_user'), {
            'nom': '', 'prenom': '', 'telephone': '',
            'email': '', 'password': '', 'role': ''
        })
        self.assertEqual(response.status_code, 200)

    def test_update_user_get(self, _):
        response = self.http_client.get(reverse('update_user', args=[self.user.pk]))
        self.assertEqual(response.status_code, 200)

    def test_update_user_post(self, _):
        response = self.http_client.post(reverse('update_user', args=[self.user.pk]), {
            'nom': 'Modifié', 'prenom': 'Prenom',
            'telephone': '0600000002', 'adresse': '2 rue test',
            'email': 'modifie@test.com', 'role': 'client', 'password': ''
        })
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.nom, 'Modifié')

    def test_delete_user_get(self, _):
        response = self.http_client.get(reverse('delete_user', args=[self.user.pk]))
        self.assertEqual(response.status_code, 200)

    def test_delete_user_post(self, _):
        response = self.http_client.post(reverse('delete_user', args=[self.user.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Utilisateur.objects.filter(pk=self.user.pk).exists())


@patch('helpdeskapp.views.WeatherService')
class DemandeUpdateViewTest(TestCase):

    def setUp(self):
        self.http_client = Client()
        self.client_user = make_client()
        self.tech = make_technicien()
        self.http_client.login(username='client1', password='testpass123')
        self.demande = Demande.objects.create(
            intitule='Test', description='Desc', client=self.client_user
        )

    def test_update_demande_get(self, _):
        response = self.http_client.get(reverse('update_demande', args=[self.demande.pk]))
        self.assertEqual(response.status_code, 200)

    def test_update_demande_post(self, _):
        response = self.http_client.post(reverse('update_demande', args=[self.demande.pk]), {
            'intitule': 'Modifié', 'description': 'Nouvelle desc',
            'client': self.client_user.pk, 'technicien': self.tech.pk
        })
        self.assertEqual(response.status_code, 302)
        self.demande.refresh_from_db()
        self.assertEqual(self.demande.intitule, 'Modifié')


@patch('helpdeskapp.views.WeatherService')
class WeatherApiViewTest(TestCase):

    def setUp(self):
        self.http_client = Client()
        self.user = make_client()
        self.http_client.login(username='client1', password='testpass123')

    def test_weather_api_success(self, mock_weather_cls):
        mock_weather_cls.return_value.get_weather.return_value = {
            'city': 'Paris', 'temperature': 15
        }
        response = self.http_client.get(reverse('weather_api') + '?city=Paris')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])

    def test_weather_api_failure(self, mock_weather_cls):
        mock_weather_cls.return_value.get_weather.return_value = None
        response = self.http_client.get(reverse('weather_api'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data['success'])

    def setUp(self):
        self.http_client = Client()
        self.user = make_client()
        self.http_client.login(username='client1', password='testpass123')

    def test_liste_domaines(self, _):
        response = self.http_client.get(reverse('list_domaines'))
        self.assertEqual(response.status_code, 200)

    def test_add_domaine(self, _):
        response = self.http_client.post(reverse('add_domaine'), {
            'intitule': 'Réseau',
            'description': 'Problèmes réseau'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Domaine.objects.filter(intitule='Réseau').exists())

    def test_update_domaine(self, _):
        domaine = Domaine.objects.create(intitule='Réseau', description='Desc')
        response = self.http_client.post(
            reverse('update_domaine', args=[domaine.pk]),
            {'intitule': 'Réseau modifié', 'description': 'Nouvelle desc'}
        )
        self.assertEqual(response.status_code, 302)
        domaine.refresh_from_db()
        self.assertEqual(domaine.intitule, 'Réseau modifié')

    def test_delete_domaine(self, _):
        domaine = Domaine.objects.create(intitule='Réseau', description='Desc')
        response = self.http_client.post(reverse('delete_domaine', args=[domaine.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Domaine.objects.count(), 0)


# -------------------------------------------------------
#  WeatherService Tests
# -------------------------------------------------------

class WeatherServiceTest(TestCase):

    def setUp(self):
        cache.clear()

    def _make_service(self):
        """Return a WeatherService with the placeholder key so cache is never cleared."""
        service = WeatherService()
        service.api_key = '8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c'
        return service

    def _mock_response(self, status_code=200):
        mock_resp = MagicMock()
        mock_resp.status_code = status_code
        mock_resp.json.return_value = {
            'name': 'Paris',
            'sys': {'country': 'FR'},
            'main': {
                'temp': 12.5,
                'feels_like': 10.0,
                'humidity': 80,
                'pressure': 1015
            },
            'weather': [{'description': 'ciel dégagé', 'icon': '01d'}],
            'wind': {'speed': 4.5}
        }
        return mock_resp

    @patch('helpdeskapp.services.requests.get')
    def test_get_weather_success(self, mock_get):
        mock_get.return_value = self._mock_response(200)
        data = self._make_service().get_weather('Paris')

        self.assertIsNotNone(data)
        self.assertEqual(data['city'], 'Paris')
        self.assertEqual(data['country'], 'FR')
        self.assertEqual(data['temperature'], 12)  # banker's rounding: round(12.5) == 12
        self.assertEqual(data['humidity'], 80)
        self.assertNotIn('demo', data)

    @patch('helpdeskapp.services.requests.get')
    def test_get_weather_invalid_api_key_returns_demo(self, mock_get):
        mock_get.return_value = self._mock_response(401)
        data = self._make_service().get_weather('Paris')

        self.assertIsNotNone(data)
        self.assertTrue(data.get('demo'))
        self.assertTrue(data.get('api_pending'))

    @patch('helpdeskapp.services.requests.get')
    def test_get_weather_server_error_returns_none(self, mock_get):
        mock_get.return_value = self._mock_response(500)
        data = self._make_service().get_weather('Paris')
        self.assertIsNone(data)

    @patch('helpdeskapp.services.requests.get')
    def test_get_weather_caches_result(self, mock_get):
        mock_get.return_value = self._mock_response(200)
        service = self._make_service()

        service.get_weather('Paris')
        service.get_weather('Paris')

        # Second call should hit cache, not the API
        self.assertEqual(mock_get.call_count, 1)

    @patch('helpdeskapp.services.requests.get')
    def test_get_weather_network_error_returns_none(self, mock_get):
        mock_get.side_effect = Exception('Connection error')
        data = self._make_service().get_weather('Paris')
        self.assertIsNone(data)

    def test_get_weather_icon_url(self):
        url = WeatherService().get_weather_icon_url('01d')
        self.assertEqual(url, 'http://openweathermap.org/img/wn/01d@2x.png')
