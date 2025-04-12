from threading import local
from django.conf import settings
from django.db import connections
from dashboard.models import Institution


_db_context = local()

class MultiTenantRouter:
    def db_for_read(self, model, **hints):
        return self.get_tenant_db()

    def db_for_write(self, model, **hints):
        return self.get_tenant_db()

    def allow_relation(self, obj1, obj2, **hints):
        return obj1._state.db == obj2._state.db

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return db == 'default'

    def get_tenant_db(self):
        return getattr(_db_context, 'tenant_db', 'default')

    @staticmethod
    def set_tenant_db(database_name):
        _db_context.tenant_db = database_name


# 🔹 Dynamically Load Tenant Databases AFTER Django is Fully Loaded
def load_tenant_databases():
    try:
        institutions = Institution.objects.all()
        for institution in institutions:
            settings.DATABASES[institution.database_name] = {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': institution.database_name,
                'USER': 'your_user',
                'PASSWORD': 'your_password',
                'HOST': 'localhost',
                'PORT': '5432',
            }
    except Exception as e:
        print(f"Error loading tenant databases: {e}")
        