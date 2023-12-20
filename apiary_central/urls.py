from django.urls import path
from django.urls.conf import include
from rest_framework_nested import routers
from . import views


# Main router for JWT authenticated API routes
api_router = routers.DefaultRouter()
api_router.register('apiaries', views.ApiaryViewSet, basename='apiaries')
# Additional JWT authenticated routes...

# Data Collection router for API key authenticated routes
datacollection_router = routers.DefaultRouter()
datacollection_router.register('apiaryhubs', views.ApiaryHubViewSet, basename='apiaryhubs')
datacollection_router.register('sensors', views.SensorViewSet, basename='sensors')
datacollection_router.register('deviceerrorreports', views.DeviceErrorReportViewSet, basename='deviceerrorreports')
# Additional data collection routes...

# Nested router for apiaries under JWT authenticated API
apiaries_router = routers.NestedDefaultRouter(api_router, 'apiaries', lookup='apiary')
apiaries_router.register('hives', views.HiveViewSet, basename='apiary-hives')

# URLConf
urlpatterns = [
    # JWT Authenticated API routes
    path('', include(api_router.urls)),
    path('', include(apiaries_router.urls)),

    # API Key Authenticated Data Collection routes
    path('datacollection/', include(datacollection_router.urls)),
    path('datatransmission/', views.DataTransmissionViewSet.as_view(), name='datacollection-datatransmission'),
    path('datatransmissionlogs/', views.DataTransmissionLogViewSet.as_view(), name='datacollection-datatransmissionlogs'),
]
