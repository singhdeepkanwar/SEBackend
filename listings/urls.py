from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PropertyViewSet, InquiryViewSet
from .erp_views import ERPPropertyListView

router = DefaultRouter()
router.register(r'properties', PropertyViewSet)
router.register(r'inquiries', InquiryViewSet)

urlpatterns = [
    path('erp/properties/', ERPPropertyListView.as_view(), name='erp-properties-list'),
    path('', include(router.urls)),
]