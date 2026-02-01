from rest_framework import generics
from .models import Property
from .erp_serializers import ERPPropertySerializer
from accounts.permissions import HasERPAccess

class ERPPropertyListView(generics.ListAPIView):
    """
    Read-only endpoint for ERP system to fetch property data.
    Secured by API Key.
    """
    queryset = Property.objects.all().order_by('-updated_at')
    serializer_class = ERPPropertySerializer
    permission_classes = [HasERPAccess]
    
    def get_queryset(self):
        qs = super().get_queryset()
        
        # Incremental Sync Filter
        updated_after = self.request.query_params.get('updated_after')
        if updated_after:
            qs = qs.filter(updated_at__gte=updated_after)
            
        # Status Filter
        status_param = self.request.query_params.get('status')
        if status_param:
            qs = qs.filter(status__iexact=status_param)
            
        return qs
