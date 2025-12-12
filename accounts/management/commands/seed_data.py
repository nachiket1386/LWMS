from django.core.management.base import BaseCommand
from django.db import transaction
from accounts.models import User
from companies.models import Company


class Command(BaseCommand):
    help = 'Seeds the database with initial data'

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding data...')

        companies_data = [
            {'name': 'Acme Corporation', 'slug': 'acme-corp'},
            {'name': 'Tech Solutions Inc', 'slug': 'tech-solutions'},
            {'name': 'Global Enterprises', 'slug': 'global-ent'},
        ]

        companies = {}
        for company_data in companies_data:
            company, created = Company.objects.get_or_create(
                slug=company_data['slug'],
                defaults={'name': company_data['name']}
            )
            companies[company_data['slug']] = company
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created company: {company.name}'))
            else:
                self.stdout.write(f'Company already exists: {company.name}')

        users_data = [
            {
                'username': 'root',
                'email': 'root@example.com',
                'password': 'rootpass123',
                'role': User.Role.ROOT,
                'company': None,
                'first_name': 'Root',
                'last_name': 'User',
            },
            {
                'username': 'admin1',
                'email': 'admin1@acme.com',
                'password': 'admin123',
                'role': User.Role.ADMIN,
                'company': companies['acme-corp'],
                'first_name': 'Admin',
                'last_name': 'One',
            },
            {
                'username': 'admin2',
                'email': 'admin2@techsolutions.com',
                'password': 'admin123',
                'role': User.Role.ADMIN,
                'company': companies['tech-solutions'],
                'first_name': 'Admin',
                'last_name': 'Two',
            },
            {
                'username': 'user1',
                'email': 'user1@acme.com',
                'password': 'user123',
                'role': User.Role.USER1,
                'company': companies['acme-corp'],
                'first_name': 'User',
                'last_name': 'One',
            },
            {
                'username': 'user2',
                'email': 'user2@techsolutions.com',
                'password': 'user123',
                'role': User.Role.USER1,
                'company': companies['tech-solutions'],
                'first_name': 'User',
                'last_name': 'Two',
            },
            {
                'username': 'user3',
                'email': 'user3@global.com',
                'password': 'user123',
                'role': User.Role.USER1,
                'company': companies['global-ent'],
                'first_name': 'User',
                'last_name': 'Three',
            },
        ]

        for user_data in users_data:
            if not User.objects.filter(username=user_data['username']).exists():
                user = User.objects.create_user(
                    username=user_data['username'],
                    email=user_data['email'],
                    password=user_data['password'],
                    role=user_data['role'],
                    company=user_data['company'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                )
                self.stdout.write(self.style.SUCCESS(
                    f'Created user: {user.username} ({user.get_role_display()})'
                ))
            else:
                self.stdout.write(f'User already exists: {user_data["username"]}')

        self.stdout.write(self.style.SUCCESS('Data seeding completed!'))
