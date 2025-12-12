from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from companies.models import Company

User = get_user_model()


class UserModelTest(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='Test Company', slug='test-company')

    def test_create_root_user(self):
        user = User.objects.create_user(
            username='root',
            email='root@test.com',
            password='testpass123',
            role=User.Role.ROOT
        )
        self.assertEqual(user.role, User.Role.ROOT)
        self.assertTrue(user.is_root())
        self.assertFalse(user.is_admin())
        self.assertFalse(user.is_user1())
        self.assertTrue(user.can_impersonate())

    def test_create_admin_user(self):
        user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123',
            role=User.Role.ADMIN,
            company=self.company
        )
        self.assertEqual(user.role, User.Role.ADMIN)
        self.assertFalse(user.is_root())
        self.assertTrue(user.is_admin())
        self.assertFalse(user.is_user1())
        self.assertFalse(user.can_impersonate())

    def test_create_user1(self):
        user = User.objects.create_user(
            username='user1',
            email='user1@test.com',
            password='testpass123',
            role=User.Role.USER1,
            company=self.company
        )
        self.assertEqual(user.role, User.Role.USER1)
        self.assertFalse(user.is_root())
        self.assertFalse(user.is_admin())
        self.assertTrue(user.is_user1())
        self.assertFalse(user.can_impersonate())

    def test_unique_email(self):
        User.objects.create_user(
            username='user1',
            email='test@test.com',
            password='testpass123'
        )
        with self.assertRaises(Exception):
            User.objects.create_user(
                username='user2',
                email='test@test.com',
                password='testpass123'
            )

    def test_has_access_to_company(self):
        company2 = Company.objects.create(name='Company 2', slug='company-2')
        
        root_user = User.objects.create_user(
            username='root',
            email='root@test.com',
            password='testpass123',
            role=User.Role.ROOT
        )
        
        admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123',
            role=User.Role.ADMIN,
            company=self.company
        )
        
        self.assertTrue(root_user.has_access_to_company(self.company))
        self.assertTrue(root_user.has_access_to_company(company2))
        
        self.assertTrue(admin_user.has_access_to_company(self.company))
        self.assertFalse(admin_user.has_access_to_company(company2))


class AuthenticationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.company = Company.objects.create(name='Test Company', slug='test-company')
        
        self.root_user = User.objects.create_user(
            username='root',
            email='root@test.com',
            password='testpass123',
            role=User.Role.ROOT
        )
        
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123',
            role=User.Role.ADMIN,
            company=self.company
        )
        
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@test.com',
            password='testpass123',
            role=User.Role.USER1,
            company=self.company
        )

    def test_login_view(self):
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)

    def test_login_successful(self):
        response = self.client.post(reverse('accounts:login'), {
            'username': 'root',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)

    def test_login_failed(self):
        response = self.client.post(reverse('accounts:login'), {
            'username': 'root',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('accounts:dashboard'))
        self.assertEqual(response.status_code, 302)

    def test_dashboard_access_after_login(self):
        self.client.login(username='root', password='testpass123')
        response = self.client.get(reverse('accounts:dashboard'))
        self.assertEqual(response.status_code, 200)


class RBACTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.company = Company.objects.create(name='Test Company', slug='test-company')
        
        self.root_user = User.objects.create_user(
            username='root',
            email='root@test.com',
            password='testpass123',
            role=User.Role.ROOT
        )
        
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123',
            role=User.Role.ADMIN,
            company=self.company
        )
        
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@test.com',
            password='testpass123',
            role=User.Role.USER1,
            company=self.company
        )

    def test_root_can_access_user_list(self):
        self.client.login(username='root', password='testpass123')
        response = self.client.get(reverse('accounts:user_list'))
        self.assertEqual(response.status_code, 200)

    def test_admin_can_access_user_list(self):
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(reverse('accounts:user_list'))
        self.assertEqual(response.status_code, 200)

    def test_user1_cannot_access_user_list(self):
        self.client.login(username='user1', password='testpass123')
        response = self.client.get(reverse('accounts:user_list'))
        self.assertEqual(response.status_code, 403)

    def test_root_can_create_user(self):
        self.client.login(username='root', password='testpass123')
        response = self.client.get(reverse('accounts:user_create'))
        self.assertEqual(response.status_code, 200)

    def test_user1_cannot_create_user(self):
        self.client.login(username='user1', password='testpass123')
        response = self.client.get(reverse('accounts:user_create'))
        self.assertEqual(response.status_code, 403)


class TenantIsolationTest(TestCase):
    def setUp(self):
        self.client = Client()
        
        self.company1 = Company.objects.create(name='Company 1', slug='company-1')
        self.company2 = Company.objects.create(name='Company 2', slug='company-2')
        
        self.root_user = User.objects.create_user(
            username='root',
            email='root@test.com',
            password='testpass123',
            role=User.Role.ROOT
        )
        
        self.admin1 = User.objects.create_user(
            username='admin1',
            email='admin1@test.com',
            password='testpass123',
            role=User.Role.ADMIN,
            company=self.company1
        )
        
        self.admin2 = User.objects.create_user(
            username='admin2',
            email='admin2@test.com',
            password='testpass123',
            role=User.Role.ADMIN,
            company=self.company2
        )

    def test_admin_sees_only_own_company_users(self):
        self.client.login(username='admin1', password='testpass123')
        response = self.client.get(reverse('accounts:user_list'))
        self.assertEqual(response.status_code, 200)
        
        users = response.context['users']
        for user in users:
            if user.company:
                self.assertEqual(user.company, self.company1)

    def test_root_sees_all_users(self):
        self.client.login(username='root', password='testpass123')
        response = self.client.get(reverse('accounts:user_list'))
        self.assertEqual(response.status_code, 200)
        
        users = response.context['users']
        user_companies = [user.company for user in users if user.company]
        self.assertIn(self.company1, user_companies)
        self.assertIn(self.company2, user_companies)


class ImpersonationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.company = Company.objects.create(name='Test Company', slug='test-company')
        
        self.root_user = User.objects.create_user(
            username='root',
            email='root@test.com',
            password='testpass123',
            role=User.Role.ROOT
        )
        
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@test.com',
            password='testpass123',
            role=User.Role.USER1,
            company=self.company
        )

    def test_root_can_impersonate(self):
        self.client.login(username='root', password='testpass123')
        response = self.client.get(reverse('accounts:impersonate_user', kwargs={'user_id': self.user1.id}))
        self.assertEqual(response.status_code, 302)

    def test_user1_cannot_impersonate(self):
        self.client.login(username='user1', password='testpass123')
        response = self.client.get(reverse('accounts:impersonate_user', kwargs={'user_id': self.root_user.id}))
        self.assertEqual(response.status_code, 403)
