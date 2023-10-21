from django.urls import path
from django.urls.conf import include
from rest_framework_nested import routers
from . import views

router = routers.DefaultRouter()
router.register('apiaries', views.ApiaryViewSet, basename='apiaries')
apiaries_router = routers.NestedDefaultRouter(router, 'apiaries', lookup='apiary')
apiaries_router.register('hives', views.HiveViewSet, basename='apiary-hives')

router.register('sensors', views.SensorViewSet, basename='sensors')
sensors_router = routers.NestedDefaultRouter(router, 'sensors', lookup='sensor')
sensors_router.register('sensordata', views.SensorDataViewSet, basename='sensor-sensordata')

router.register('sensordataupload', views.SensorDataUploadViewSet, basename='sensordataupload')



# URLConf
urlpatterns = router.urls  + apiaries_router.urls + sensors_router.urls 


# /api/apiaries/
# /api/apiaries/6/
# /api/apiaries/6/hives/
# /api/apiaries/6/hives/11

# /api/sensors/
# /api/sensors/f3d4f904-2b32-4f62-b65f-9e2aa61aa7e4/
# /api/sensors/f3d4f904-2b32-4f62-b65f-9e2aa61aa7e4/sensordata

# /api/sensordataupload/ 