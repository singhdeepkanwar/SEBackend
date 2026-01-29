from rest_framework import serializers
from .models import Property, PropertyImage, VerificationDocument, Amenity, Favorite, Inquiry, Favorite

class AmenitySerializer(serializers.ModelSerializer):
    class Image:
        model = Amenity
        fields = ['id', 'name', 'icon_name']

class PropertyImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyImage
        fields = ['id', 'image', 'is_main']

class VerificationDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = VerificationDocument
        fields = ['id', 'file', 'document_type']

class PropertyCreateSerializer(serializers.ModelSerializer):
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(allow_empty_file=False),
        write_only=True, required=False
    )

    class Meta:
        model = Property
        fields = [
            'id', 'title', 'description', 'property_type', 'listing_type',
            'area', 'unit', 'price', 'bedrooms', 'bathrooms', 'amenities',
            'address', 'city', 'uploaded_images',
            # --- PROTECTED FIELDS ---
            'status', 'admin_notes', 'is_featured'
        ]
        # These fields CANNOT be set by the user via the API
        read_only_fields = ['status', 'admin_notes', 'is_featured']

    def create(self, validated_data):
        # 1. Pop the amenities data out of the dictionary first
        amenities_data = validated_data.pop('amenities', [])
        images_data = validated_data.pop('uploaded_images', [])

        # 2. Create the property object without amenities
        property_obj = Property.objects.create(**validated_data)

        # 3. Use .set() to assign the many-to-many relationship
        if amenities_data:
            property_obj.amenities.set(amenities_data)

        # 4. Handle your images as before
        for image in images_data:
            PropertyImage.objects.create(property=property_obj, image=image)

        return property_obj

class PropertyReadSerializer(serializers.ModelSerializer):
    images = PropertyImageSerializer(many=True, read_only=True)
    amenities = AmenitySerializer(many=True, read_only=True)
    price_per_unit = serializers.ReadOnlyField()
    is_favorite = serializers.SerializerMethodField()

    class Meta:
        model = Property
        fields = [
            'id', 'title', 'description', 'property_type', 'listing_type',
            'area', 'unit', 'price', 'price_per_unit', 'bedrooms', 
            'bathrooms', 'amenities', 'address', 'city', 'images', 
            'status', 'is_featured', 'is_favorite', 'created_at'
        ]

    def get_is_favorite(self, obj):
        # Checks if the logged-in user has liked this property
        user = self.context.get('request').user
        if user.is_authenticated:
            return Favorite.objects.filter(user=user, property=obj).exists()
        return False

class AdminPropertyVerifySerializer(serializers.ModelSerializer):
    """
    Used by your Admin team to Verify, Reject, or Add Internal Docs.
    """
    uploaded_documents = serializers.ListField(
        child=serializers.FileField(allow_empty_file=False),
        write_only=True, required=False
    )

    class Meta:
        model = Property
        fields = ['status', 'admin_notes', 'is_featured', 'uploaded_documents']

    def update(self, instance, validated_data):
        docs_data = validated_data.pop('uploaded_documents', [])
        
        # Update status and notes
        instance.status = validated_data.get('status', instance.status)
        instance.admin_notes = validated_data.get('admin_notes', instance.admin_notes)
        instance.is_featured = validated_data.get('is_featured', instance.is_featured)
        instance.save()

        # Handle Document Uploads (Admin side)
        for doc in docs_data:
            VerificationDocument.objects.create(property=instance, file=doc)
            
        return instance

class InquirySerializer(serializers.ModelSerializer):
    # We display the property title and ID for context
    property_details = serializers.ReadOnlyField(source='property.title')

    class Meta:
        model = Inquiry
        fields = [
            'id', 'property', 'property_details', 'status', 
            'admin_remarks', 'created_at'
        ]
        # Users can only send the property ID. 
        # Status and Remarks are for Admins only.
        read_only_fields = ['status', 'admin_remarks', 'created_at']

    def create(self, validated_data):
        # Automatically set the user to the logged-in user
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ['id', 'property', 'created_at']
        read_only_fields = ['created_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class DashboardSummarySerializer(serializers.Serializer):
    # Property Stats
    total_properties = serializers.IntegerField()
    pending_verification = serializers.IntegerField()
    live_listings = serializers.IntegerField()
    
    # Lead Stats
    new_inquiries = serializers.IntegerField()
    active_viewings = serializers.IntegerField()
    total_favorites = serializers.IntegerField()
    
    # Financial Snapshot (Calculated)
    total_inventory_value = serializers.DecimalField(max_digits=20, decimal_places=2)
    
    # Recent Activity Lists (Optional nested data)
    recent_inquiries = InquirySerializer(many=True, read_only=True)

    class Meta:
        fields = '__all__'