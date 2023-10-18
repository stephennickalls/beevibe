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

# URLConf
urlpatterns = router.urls  + apiaries_router.urls + sensors_router.urls