from django.db.models import Sum, Count
from rest_framework import viewsets, permissions, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Property, Inquiry, Favorite, Amenity, PreListing
from .serializers import (
    PropertyReadSerializer, PropertyCreateSerializer,
    AdminPropertyVerifySerializer, DashboardSummarySerializer,
    InquirySerializer, FavoriteSerializer, AmenitySerializer,
    PreListingSerializer,
)
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.parsers import MultiPartParser, FormParser

class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    parser_classes = (MultiPartParser, FormParser) 
    filterset_fields = {
        'price': ['gte', 'lte'],  # Allows ?price__gte=1000&price__lte=5000
        'city': ['exact', 'icontains'],
        'property_type': ['exact'],
        'listing_type': ['exact'],
        'area': ['gte', 'lte'],
    }
    # 3. Tell Django which fields can be used for ordering
    
    # 4. Set the default ordering (server-side backup)
    # Allows a general search bar for title and description
    search_fields = ['title', 'description', 'address']
    permission_classes = [IsAuthenticatedOrReadOnly]
    def get_serializer_class(self):
        if self.action == 'verify_property':
            return AdminPropertyVerifySerializer
        if self.action in ['create', 'update', 'partial_update']:
            return PropertyCreateSerializer
        return PropertyReadSerializer
    
    def get_queryset(self):
        # Admins see everything; Users see only VERIFIED listings
        if self.request.user.is_staff:
            return Property.objects.all()
        return Property.objects.filter(status='VERIFIED')
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_properties(self, request):
        # Filter properties where the seller is the current logged-in user
        user_properties = self.queryset.filter(owner=request.user)
        serializer = self.get_serializer(user_properties, many=True)
        return Response(serializer.data)
    ordering_fields = ['id', 'price']
    ordering = ['-id']
    # --- CUSTOM ACTIONS ---

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def verify_property(self, request, pk=None):
        """Action for your team to approve/reject a listing."""
        property_obj = self.get_object()
        serializer = AdminPropertyVerifySerializer(property_obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAdminUser])
    def admin_dashboard(self, request):
        """The 'Summary' view for your internal team."""
        data = {
            'total_properties': Property.objects.count(),
            'pending_verification': Property.objects.filter(status='PENDING').count(),
            'live_listings': Property.objects.filter(status='VERIFIED').count(),
            'new_inquiries': Inquiry.objects.filter(status='NEW').count(),
            'active_viewings': Inquiry.objects.filter(status='VIEWING').count(),
            'total_favorites': Favorite.objects.count(),
            'total_inventory_value': Property.objects.filter(status='VERIFIED').aggregate(Sum('price'))['price__sum'] or 0,
            'recent_inquiries': Inquiry.objects.order_by('-created_at')[:5]
        }
        serializer = DashboardSummarySerializer(data)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def toggle_favorite(self, request, pk=None):
        """Allows users to like/unlike a property."""
        property_obj = self.get_object()
        favorite, created = Favorite.objects.get_or_create(user=request.user, property=property_obj)
        
        if not created:
            favorite.delete()
            return Response({'status': 'unfavorited'})
        return Response({'status': 'favorited'})

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def favorites(self, request):
        """Returns properties favorited by the current user."""
        user_favorites = Favorite.objects.filter(user=request.user).values_list('property_id', flat=True)
        properties = Property.objects.filter(id__in=user_favorites)
        serializer = self.get_serializer(properties, many=True)
        return Response(serializer.data)

class InquiryViewSet(viewsets.ModelViewSet):
    queryset = Inquiry.objects.all()
    serializer_class = InquirySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Admins see all leads to act as middlemen; Users see their own interests
        if self.request.user.is_staff:
            return Inquiry.objects.all().order_by('-created_at')
        return Inquiry.objects.filter(user=self.request.user)

    @action(detail=True, methods=['patch'], permission_classes=[permissions.IsAdminUser])
    def update_lead_status(self, request, pk=None):
        """Admin updates the status after talking to the inquirer."""
        inquiry = self.get_object()
        new_status = request.data.get('status')
        remarks = request.data.get('admin_remarks')
        
        if new_status:
            inquiry.status = new_status
        if remarks:
            inquiry.admin_remarks = remarks
        
        inquiry.save()
        return Response({'status': 'Lead updated successfully'})

class AmenityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Amenity.objects.all()
    serializer_class = AmenitySerializer
    permission_classes = [permissions.AllowAny]


class PreListingCreateView(generics.CreateAPIView):
    """
    Public endpoint — no auth required.
    POST /api/pre-listings/  →  saves owner + property interest before launch.
    """
    queryset = PreListing.objects.all()
    serializer_class = PreListingSerializer
    permission_classes = [permissions.AllowAny]