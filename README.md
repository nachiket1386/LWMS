# Tenant Auth RBAC System

A Django-based multi-tenant authentication and role-based access control (RBAC) system with user impersonation capabilities.

## Features

- **Custom User Model** extending AbstractUser with:
  - Unique email requirement
  - Role choices: ROOT, ADMIN, USER1
  - FK/M2M relationships to Company for tenant scoping
  
- **Authentication Flows**:
  - Login/logout views
  - Password reset functionality
  - Session timeout handling
  - Django messages for user feedback
  - ROOT user impersonation with secure tenant context switching

- **RBAC Utilities**:
  - Decorators for per-role permissions (`@root_required`, `@admin_required`, `@user1_required`)
  - Class-based view mixins for role enforcement
  - Middleware for cross-tenant data access blocking

- **User Management UI**:
  - List/search/filter users
  - Create/edit/deactivate accounts
  - Assign roles
  - Reset passwords
  - ROOT-only impersonation actions

- **REST API**:
  - DRF serializers and viewsets
  - API endpoints for user management
  - Token-based authentication support

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Seed initial data:
```bash
python manage.py seed_data
```

6. Run the development server:
```bash
python manage.py runserver
```

## Default Users

After seeding, the following users are available:

| Username | Password | Role | Company |
|----------|----------|------|---------|
| root | rootpass123 | ROOT | - |
| admin1 | admin123 | ADMIN | Acme Corporation |
| admin2 | admin123 | ADMIN | Tech Solutions Inc |
| user1 | user123 | USER1 | Acme Corporation |
| user2 | user123 | USER1 | Tech Solutions Inc |
| user3 | user123 | USER1 | Global Enterprises |

## URLs

- Admin Panel: `/admin/`
- Login: `/accounts/login/`
- Dashboard: `/accounts/dashboard/`
- User Management: `/accounts/users/`
- API: `/api/users/` and `/api/companies/`

## Role Permissions

### ROOT
- Full system access
- Can impersonate any user (except other ROOT users)
- Can assume tenant context
- Manages all users across all companies

### ADMIN
- Manages users within their company
- Can create/edit/deactivate users
- Can reset passwords
- Cannot impersonate users

### USER1
- Basic user access
- Can view dashboard
- Limited to own tenant data

## Tenant Isolation

- Admins can only see and manage users from their own company
- ROOT users see all data across all tenants
- Middleware enforces tenant context for non-ROOT users
- Cross-tenant data access is blocked by default

## Testing

Run the test suite:
```bash
python manage.py test accounts
```

Tests cover:
- User model functionality
- Authentication flows
- Role-based access control
- Tenant isolation
- Impersonation functionality

## API Usage

Example API calls using curl:

```bash
# Login (get session)
curl -X POST http://localhost:8000/accounts/login/ \
  -d "username=root&password=rootpass123"

# List users
curl http://localhost:8000/api/users/

# Create user
curl -X POST http://localhost:8000/api/users/ \
  -H "Content-Type: application/json" \
  -d '{"username":"newuser","email":"newuser@example.com","password":"pass123","role":"USER1","company":1}'

# Reset user password
curl -X POST http://localhost:8000/api/users/1/reset_password/ \
  -H "Content-Type: application/json" \
  -d '{"new_password":"newpass123","confirm_password":"newpass123"}'
```

## Security Features

- Session timeout after 1 hour
- Password validation
- CSRF protection
- Unique email constraint
- Secure password hashing
- Permission checks at view and API levels

## Project Structure

```
.
├── accounts/               # User authentication & RBAC app
│   ├── decorators.py      # Permission decorators
│   ├── mixins.py          # Class-based view mixins
│   ├── middleware.py      # Tenant isolation middleware
│   ├── models.py          # Custom User model
│   ├── views.py           # Authentication & user management views
│   ├── api_views.py       # REST API views
│   ├── serializers.py     # DRF serializers
│   ├── permissions.py     # API permissions
│   ├── forms.py           # Django forms
│   └── tests.py           # Test suite
├── companies/             # Company/tenant management
│   └── models.py          # Company model
├── config/                # Django settings
│   ├── settings.py
│   └── urls.py
└── templates/             # HTML templates
    ├── base.html
    └── accounts/
        ├── login.html
        ├── dashboard.html
        ├── user_list.html
        └── ...
```

## License

MIT License
