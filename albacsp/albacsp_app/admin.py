from django.contrib import admin
from .models import *

admin.site.register(Home)
admin.site.register(Device)
admin.site.register(App)
admin.site.register(Power)
admin.site.register(Connectivity)
admin.site.register(Vulnerability)
admin.site.register(CWE)
admin.site.register(Connection)
admin.site.register(ConnectionVulnerability)