from django.urls import path
from django.urls.conf import include
from rest_framework_nested import routers
from . import views


# Your routers definition
router = routers.DefaultRouter()
router.register('apiaries', views.ApiaryViewSet, basename='apiaries')
router.register('datacollection', views.DataCollectionViewSet, basename='datacollection')
# router.register('apiayhubdataupload', views.ApiaryHubDataUploadViewSet, basename='apiaryhubdataupload')

apiaries_router = routers.NestedDefaultRouter(router, 'apiaries', lookup='apiary')
apiaries_router.register('hives', views.HiveViewSet, basename='apiary-hives')

# datacollection_router = routers.NestedDefaultRouter(router, 'datacollection', lookup='datacollection')
# datacollection_router.register('apiayhubdataupload', views.ApiaryHubDataUploadViewSet, basename='apiaryhubdataupload')


# Instead of using the nested router for datacollection, manually define the URL
datacollection_apiayhubdataupload_list = views.ApiaryHubDataUploadViewSet.as_view({
    'get': 'list',  # Assuming you have a list action
    'post': 'create',  # Assuming you have a create action
})

datacollection_apiayhubdataupload_detail = views.ApiaryHubDataUploadViewSet.as_view({
    'get': 'retrieve',  # Assuming you have a retrieve action
    'put': 'update',  # Assuming you have an update action
    'patch': 'partial_update',  # Assuming you have a partial_update action
    'delete': 'destroy',  # Assuming you have a destroy action
})


# Instead of using the nested router for datacollection, manually define the URL
datacollection_apiaryhubs_list = views.ApiaryHubViewSet.as_view({
    'get': 'list',  # Assuming you have a list action
    'post': 'create',  # Assuming you have a create action
})

datacollection_apiaryhubs_detail = views.ApiaryHubViewSet.as_view({
    'get': 'retrieve',  # Assuming you have a retrieve action
    'put': 'update',  # Assuming you have an update action
    'patch': 'partial_update',  # Assuming you have a partial_update action
    'delete': 'destroy',  # Assuming you have a destroy action
})
# Instead of using the nested router for datacollection, manually define the URL
datacollection_sensors_list = views.SensorViewSet.as_view({
    'get': 'list',  # Assuming you have a list action
    'post': 'create',  # Assuming you have a create action
})

datacollection_sensors_detail = views.SensorViewSet.as_view({
    'get': 'retrieve',  # Assuming you have a retrieve action
    'put': 'update',  # Assuming you have an update action
    'patch': 'partial_update',  # Assuming you have a partial_update action
    'delete': 'destroy',  # Assuming you have a destroy action
})

# URLConf
urlpatterns = [
    path('', include(router.urls)),
    path('apiaries/', include(apiaries_router.urls)),
    path('datacollection/apiaryhubs/', datacollection_apiaryhubs_list, name='datacollection-apiaryhubs-list'),
    path('datacollection/apiaryhubs/<int:pk>/', datacollection_apiaryhubs_detail, name='datacollection-apiaryhubs-detail'),
    path('datacollection/sensors/', datacollection_sensors_list, name='datacollection-sensors-list'),
    path('datacollection/sensors/<int:pk>/', datacollection_sensors_detail, name='datacollection-sensors-detail'),
    path('datacollection/apiayhubdataupload/', datacollection_apiayhubdataupload_list, name='datacollection-apiayhubdataupload-list'),
    path('datacollection/apiayhubdataupload/<int:pk>/', datacollection_apiayhubdataupload_detail, name='datacollection-apiayhubdataupload-detail'),

]

# /api/apiaries/
# /api/apiaries/6/
# /api/apiaries/6/hives/
# /api/apiaries/6/hives/11

# /api/sensors/
# /api/sensors/f3d4f904-2b32-4f62-b65f-9e2aa61aa7e4/
# /api/sensors/f3d4f904-2b32-4f62-b65f-9e2aa61aa7e4/sensordata

# /api/sensordataupload/ 