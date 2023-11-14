from django.urls import path
from django.urls.conf import include
from rest_framework_nested import routers
from . import views


# Your routers definition
router = routers.DefaultRouter()
router.register('apiaries', views.ApiaryViewSet, basename='apiaries')
router.register('datacollection', views.DataCollectionViewSet, basename='datacollection')

apiaries_router = routers.NestedDefaultRouter(router, 'apiaries', lookup='apiary')
apiaries_router.register('hives', views.HiveViewSet, basename='apiary-hives')


datacollection_datatransmission_list = views.DataTransmissionViewSet.as_view({
    'get': 'list',  
    'post': 'create',  
})

datacollection_datatransmission_detail = views.DataTransmissionViewSet.as_view({
    'get': 'retrieve',  
    'put': 'update',  
    'patch': 'partial_update',  
    'delete': 'destroy',  
})


# Instead of using the nested router for datacollection, manually define the URL
datacollection_apiaryhubs_list = views.ApiaryHubViewSet.as_view({
    'get': 'list',  
    'post': 'create',  
})

datacollection_apiaryhubs_detail = views.ApiaryHubViewSet.as_view({
    'get': 'retrieve', 
    'put': 'update', 
    'patch': 'partial_update',  
    'delete': 'destroy',  
})
# Instead of using the nested router for datacollection, manually define the URL
datacollection_sensors_list = views.SensorViewSet.as_view({
    'get': 'list',  
    'post': 'create',  
})

datacollection_sensors_detail = views.SensorViewSet.as_view({
    'get': 'retrieve',  
    'put': 'update',  
    'patch': 'partial_update',  
    'delete': 'destroy',  
})

# URLConf
urlpatterns = [
    path('', include(router.urls)),
    path('', include(apiaries_router.urls)),
    path('datacollection/apiaryhubs/', datacollection_apiaryhubs_list, name='datacollection-apiaryhubs-list'),
    path('datacollection/apiaryhubs/<uuid:api_key>/', datacollection_apiaryhubs_detail, name='datacollection-apiaryhubs-detail'),
    path('datacollection/sensors/', datacollection_sensors_list, name='datacollection-sensors-list'),
    path('datacollection/sensors/<uuid:pk>/', datacollection_sensors_detail, name='datacollection-sensors-detail'),
    path('datacollection/datatransmission/', datacollection_datatransmission_list, name='datacollection-datatransmission-list'),
    path('datacollection/datatransmission/<int:pk>/', datacollection_datatransmission_detail, name='datacollection-datatransmission-detail'),

]

# /api/apiaries/
# /api/apiaries/6/
# /api/apiaries/6/hives/
# /api/apiaries/6/hives/11

# /api/sensors/
# /api/sensors/f3d4f904-2b32-4f62-b65f-9e2aa61aa7e4/
# /api/sensors/f3d4f904-2b32-4f62-b65f-9e2aa61aa7e4/sensordata

# /api/sensordataupload/ 