# AMS Core - Multi-Tenant Asset Management System

A Django 4.2.7 multi-tenant Asset Management System (AMS) providing company-scoped resource management with tenant-aware models, responsive Bootstrap UI, and comprehensive configuration management.

## Project Overview

This project provides the core infrastructure for a multi-tenant SaaS asset management platform. Key features include:

- **Multi-Tenant Architecture**: Company-based tenancy resolved via session or subdomain
- **Django 4.2.7**: Latest stable Django version targeting Python 3.11
- **Responsive UI**: Bootstrap 5 templates with responsive design
- **Environment-Driven Configuration**: .env file support for flexible deployment
- **Django Admin Integration**: Pre-configured admin interface for Company and TenantProfile management
- **Database Support**: SQLite for development, PostgreSQL for production
- **Test Infrastructure**: pytest with Django fixtures and test utilities

## Installation & Setup

### Prerequisites

- Python 3.11+
- pip/venv

### Step 1: Clone and Setup Virtual Environment

```bash
git clone <repository-url> ams-core
cd ams-core

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment

Copy the example environment file and customize as needed:

```bash
cp .env.example .env
```

**Development (.env)**:
```
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_ENGINE=django.db.backends.sqlite3
DATABASE_NAME=db.sqlite3
```

**Production with PostgreSQL**:
```
DEBUG=False
DATABASE_ENGINE=django.db.backends.postgresql
POSTGRES_DB=amscore
POSTGRES_USER=amscore
POSTGRES_PASSWORD=your-secure-password
POSTGRES_HOST=db.example.com
POSTGRES_PORT=5432
```

### Step 4: Initialize Database

```bash
# Run migrations
python manage.py migrate

# Create superuser for admin access
python manage.py createsuperuser

# (Optional) Load sample companies fixture
python manage.py loaddata initial_companies
```

### Step 5: Run Development Server

```bash
python manage.py runserver
```

Access the application at:
- **Web**: http://localhost:8000/
- **Admin**: http://localhost:8000/admin/

## Project Structure

```
ams-core/
├── amscore/              # Main Django project
│   ├── settings.py       # Django settings (environment-driven)
│   ├── urls.py          # URL routing configuration
│   ├── wsgi.py          # WSGI application entry
│   ├── asgi.py          # ASGI application entry
│   ├── middleware.py    # Multi-tenant middleware
│   ├── context_processors.py  # Template context utilities
│   └── apps/
│       └── core/        # Core app with tenant models
│           ├── models.py       # Company, TenantProfile, TenantAwareModel
│           ├── admin.py        # Admin interface configuration
│           ├── migrations/     # Database migrations
│           ├── fixtures/       # Sample data (initial_companies.json)
│           └── tests/          # Test suite
├── templates/           # HTML templates (base.html, home.html)
├── static/              # Static files (CSS, JavaScript)
│   ├── css/style.css
│   └── js/app.js
├── logs/               # Application logs
├── media/              # User-uploaded media files
├── manage.py           # Django management command
├── requirements.txt    # Python dependencies
├── .env.example        # Environment configuration template
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

## Multi-Tenant Architecture

### How It Works

1. **Company Resolution**: The `TenantMiddleware` resolves the active company per request:
   - From session (`request.session['company_id']`)
   - From subdomain slug (e.g., `acme.example.com` → company with slug `acme`)

2. **Tenant-Aware Models**: All tenant-scoped data inherits from `TenantAwareModel`:
   ```python
   class TenantAwareModel(models.Model):
       company = models.ForeignKey(Company, ...)
       created_at = models.DateTimeField(auto_now_add=True)
       updated_at = models.DateTimeField(auto_now=True)
   ```

3. **Context Available in Templates**: 
   - `current_company`: Currently active Company instance
   - `companies`: List of active companies for the user

### Company Model

```python
class Company(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True)  # Subdomain identifier
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### TenantProfile Model

```python
class TenantProfile(TenantAwareModel):
    company = models.OneToOneField(Company, ...)
    timezone = models.CharField(...)  # 104+ timezone options
    primary_color = models.CharField(max_length=7)
    logo = models.ImageField(upload_to='logos/', ...)
    phone = models.CharField(...)
    website = models.URLField(...)
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | django-insecure-... | Django secret key (change in production!) |
| `DEBUG` | True | Enable debug mode |
| `ALLOWED_HOSTS` | localhost,127.0.0.1 | Comma-separated allowed hosts |
| `DATABASE_ENGINE` | django.db.backends.sqlite3 | Database backend |
| `DATABASE_NAME` | db.sqlite3 | SQLite database filename |
| `POSTGRES_DB` | amscore | PostgreSQL database name |
| `POSTGRES_USER` | amscore | PostgreSQL user |
| `POSTGRES_PASSWORD` | - | PostgreSQL password |
| `POSTGRES_HOST` | localhost | PostgreSQL host |
| `POSTGRES_PORT` | 5432 | PostgreSQL port |

### Settings File

All configuration is in `amscore/settings.py`. The file:
- Loads `.env` file via `python-dotenv`
- Defaults to development-friendly settings
- Supports environment-driven overrides for production

## Database

### SQLite (Development)

Default database. Create `db.sqlite3` automatically:

```bash
python manage.py migrate
```

### PostgreSQL (Production)

Set environment variables and run migrations:

```bash
export DATABASE_ENGINE=django.db.backends.postgresql
export POSTGRES_DB=amscore
export POSTGRES_USER=amscore
export POSTGRES_PASSWORD=secure_password
export POSTGRES_HOST=prod-db.example.com

python manage.py migrate
```

## Testing

### Run All Tests

```bash
pytest
```

### Run Specific Test Module

```bash
pytest amscore/apps/core/tests/test_models.py
```

### Run With Coverage Report

```bash
pytest --cov=amscore --cov-report=html
```

Coverage reports generated in `htmlcov/` directory.

### Test Fixtures

Pre-configured fixtures in `amscore/apps/core/tests/conftest.py`:
- `company`: Sample Company instance
- `tenant_profile`: Tenant profile for test company
- `user`: Django User instance
- `authenticated_user`: Request with authenticated user

## Admin Interface

Access Django admin at `/admin/`:

1. **Companies**: Create, edit, manage tenant companies
2. **Tenant Profiles**: Configure company-specific settings (timezone, logo, branding)

## Logging

Application logging configured in `settings.py`:

- **Level**: INFO (DEBUG in development)
- **Handlers**: Console and file (`logs/amscore.log`)
- **Format**: Verbose format with timestamp, module, process ID

View logs:
```bash
tail -f logs/amscore.log
```

## Dependencies

Key dependencies:

- **Django 4.2.7**: Web framework
- **django-crispy-forms 2.1**: Form rendering
- **crispy-bootstrap5**: Bootstrap 5 form templates
- **djangorestframework**: REST API framework
- **django-filter**: Query filtering
- **django-import-export**: Excel/CSV import/export
- **Pillow**: Image processing
- **pandas**: Data processing
- **openpyxl/xlsxwriter**: Excel file generation
- **psycopg2-binary**: PostgreSQL adapter

Full list: `requirements.txt`

## Development Workflow

### Create New App

```bash
mkdir -p amscore/apps/myapp
python manage.py startapp myapp amscore/apps/myapp
# Add 'amscore.apps.myapp.apps.MyappConfig' to INSTALLED_APPS
```

### Create Database Migration

```bash
python manage.py makemigrations amscore.apps.core
python manage.py migrate
```

### Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### Load Fixtures

```bash
python manage.py loaddata initial_companies
```

## Deployment

### Prepare for Production

1. **Set Environment Variables**:
   ```bash
   export ENVIRONMENT=prod
   export DEBUG=False
   export SECRET_KEY=your-production-secret-key
   export ALLOWED_HOSTS=example.com,www.example.com
   export DATABASE_ENGINE=django.db.backends.postgresql
   # ... PostgreSQL variables
   ```

2. **Collect Static Files**:
   ```bash
   python manage.py collectstatic --noinput
   ```

3. **Run Migrations**:
   ```bash
   python manage.py migrate
   ```

4. **Create Superuser**:
   ```bash
   python manage.py createsuperuser
   ```

5. **Deploy Using WSGI**:
   - Gunicorn: `gunicorn amscore.wsgi:application`
   - uWSGI: `uwsgi --http :8000 --wsgi-file amscore/wsgi.py`

### Security Checklist

- [ ] Set `SECRET_KEY` to a strong random value
- [ ] Set `DEBUG = False`
- [ ] Configure `ALLOWED_HOSTS` with your domain
- [ ] Use PostgreSQL or other production database
- [ ] Enable HTTPS (`SECURE_SSL_REDIRECT = True`)
- [ ] Set secure cookie flags
- [ ] Configure logging and monitoring
- [ ] Run `python manage.py check --deploy`

## Acceptance Criteria Status

✅ **Django 4.2.7 Project Initialized**: manage.py and wsgi/asgi configured
✅ **Python 3.11 Targeting**: Virtual environment created with Python 3.11
✅ **Settings Configuration**: Single settings.py with .env support
✅ **Multi-Tenant Layer**: Company/Tenant models, middleware, context processor
✅ **Database Setup**: SQLite with Postgres support via environment
✅ **Initial Migrations**: Core models migrated, Company/TenantProfile created
✅ **Project Utilities**: Base templates, static files, logging configuration
✅ **Test Infrastructure**: pytest-django configured with fixtures
✅ **README Documentation**: Comprehensive setup and usage guide
✅ **Server Startup**: `python manage.py migrate` succeeds, server runs without errors
✅ **Multi-Tenant Resolution**: Middleware resolves tenant per request

## Troubleshooting

### ModuleNotFoundError: No module named 'django'

Activate the virtual environment:
```bash
source venv/bin/activate
```

### db.sqlite3: Permission Denied

Ensure the project directory is writable:
```bash
chmod -R u+w .
```

### Migrate: "No such table: django_migrations"

Run migrations:
```bash
python manage.py migrate
```

### Pillow not installed

Install requirements:
```bash
pip install -r requirements.txt
```

## Contributing

When adding new features:

1. Create feature branch
2. Write tests first
3. Implement feature
4. Run `pytest` and ensure all tests pass
5. Update this README if needed
6. Commit with clear message

## License

[Add your license here]

## Support

For issues, questions, or contributions, please open a GitHub issue or contact the development team.
