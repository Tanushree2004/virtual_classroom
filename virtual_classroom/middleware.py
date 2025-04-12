from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import get_user_model
from django.db import connection
from .routers import MultiTenantRouter
from django.conf import settings

User = get_user_model()

class TenantMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            institution = request.user.institution
            if institution and institution.database_name in settings.DATABASES:
                MultiTenantRouter.set_tenant_db(institution.database_name)
            else:
                MultiTenantRouter.set_tenant_db('default')
