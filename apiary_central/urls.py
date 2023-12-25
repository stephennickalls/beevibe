from django.urls import path
from django.urls.conf import include
from rest_framework_nested import routers
from . import views

# Main router for JWT authenticated API routes
api_router = routers.DefaultRouter()
api_router.register('apiaries', views.ApiaryViewSet, basename='apiaries')

# Data Collection router for API key authenticated routes
datacollection_router = routers.DefaultRouter()
datacollection_router.register('hubconfig', views.ApiaryHubConfViewSet, basename='hubconfig')
datacollection_router.register('apiaryhubs', views.ApiaryHubViewSet, basename='apiaryhubs')
datacollection_router.register('sensors', views.SensorViewSet, basename='sensors')
datacollection_router.register('deviceerrorreports', views.DeviceErrorReportViewSet, basename='deviceerrorreports')

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

    # Custom path for ApiaryHub detail view using api_key
    path('datacollection/apiaryhubs/<uuid:api_key>/', views.ApiaryHubViewSet.as_view({
        'get': 'retrieve', 
        'put': 'update', 
        'patch': 'partial_update', 
        'delete': 'destroy'
    }), name='datacollection-apiaryhubs-detail'),

        # Custom path for ApiaryHub detail view using api_key
    path('datacollection/deviceerrorreports/<uuid:api_key>/', views.DeviceErrorReportViewSet.as_view({
        'get': 'retrieve', 
        'put': 'update', 
        'patch': 'partial_update', 
        'delete': 'destroy'
    }), name='datacollection-deviceerrorreports-detail'),
    

    path('datacollection/datatransmission/', views.DataTransmissionViewSet.as_view(), name='datacollection-datatransmission'),
    path('datacollection/datatransmissionlogs/', views.DataTransmissionLogViewSet.as_view(), name='datacollection-datatransmissionlogs'),
]