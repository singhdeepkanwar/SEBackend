from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PropertyViewSet, InquiryViewSet, AmenityViewSet, PreListingCreateView
from .erp_views import ERPPropertyListView

router = DefaultRouter()
router.register(r'properties', PropertyViewSet)
router.register(r'inquiries', InquiryViewSet)
router.register(r'amenities', AmenityViewSet)

urlpatterns = [
    path('erp/properties/', ERPPropertyListView.as_view(), name='erp-properties-list'),
    path('pre-listings/', PreListingCreateView.as_view(), name='pre-listing-create'),
    path('', include(router.urls)),
]