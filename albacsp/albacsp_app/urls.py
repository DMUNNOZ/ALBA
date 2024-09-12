
from django.urls import include, path
from rest_framework import routers
from rest_framework.documentation import include_docs_urls
from . import views

router = routers.DefaultRouter()
router.register(r"home", views.HomeView, "home")
router.register(r"devices", views.DeviceView, "devices")
router.register(r"apps", views.AppView, "apps")
router.register(r"powers", views.PowerView, "powers")
router.register(r"connectivities", views.ConnectivityView, "connectivities")
router.register(r"vulnerabilities", views.VulnerabilityView, "vulnerabilities")
router.register(r"cwes", views.CWEView, "cws")
router.register(r"connections", views.ConnectionView, "connections")
router.register(r"connectionvulnerabilities", views.ConnectionVulnerabilityView, "connectionvulnerabilities")


urlpatterns=[
  path("api/", include(router.urls)),
  path('docs/', include_docs_urls(title='API')),
  #path('api/impact/mins/',views.ImpactMinView.as_view(), name='impactmin'),
  path('api/connection/max/',views.ConnectionsMaxView.as_view(), name='connectionmax'),
  path('api/app/min/',views.AppMinConfigView.as_view(), name='appminconfig'),
  path('api/connectivity/max/',views.ConnectivityMaxConfigView.as_view(), name='connectivitymaxconfig'),
  path('api/impact/min/',views.ImpactMinConfigView.as_view(), name='impactminconfig'),
  path('api/cwe/min/',views.CWEMinConfigView.as_view(), name='cweminconfig'),
  path('api/sustainability/max/',views.SustainabilityMaxConfigView.as_view(), name='sustainabilitymaxconfig'),
  path('api/config/',views.ConfigView.as_view(), name='config'),

]
