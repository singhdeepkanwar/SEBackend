from rest_framework import serializers
from .models import Property

class ERPPropertySerializer(serializers.ModelSerializer):
    """
    Simplified, flat serializer for ERP consumption.
    """
    owner_phone = serializers.ReadOnlyField(source='owner.phone')
    full_address = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Property
        fields = [
            'id', 'title', 'price', 'status', 'property_type', 'listing_type',
            'area', 'unit', 'owner_phone', 'full_address', 'image_url',
            'created_at', 'updated_at'
        ]

    def get_full_address(self, obj):
        return f"{obj.address}, {obj.city}"

    def get_image_url(self, obj):
        # Return the main image or the first one available
        main_img = obj.images.filter(is_main=True).first()
        if not main_img:
            main_img = obj.images.first()
        
        if main_img and main_img.image:
            return main_img.image.url
        return None
