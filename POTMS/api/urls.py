from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet, VendorViewSet, MasterItemViewSet

router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'vendors', VendorViewSet)
router.register(r'master-items', MasterItemViewSet, basename='masteritem')  

urlpatterns = router.urls