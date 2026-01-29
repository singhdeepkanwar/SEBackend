# listings/managers.py or logic in ViewSet
from listings.models import Property

def get_queryset(self):
    return Property.objects.filter(status='VERIFIED')