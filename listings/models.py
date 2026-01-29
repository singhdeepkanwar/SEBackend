import uuid
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator

class Amenity(models.Model):
    name = models.CharField(max_length=50, unique=True)
    icon_name = models.CharField(max_length=50, blank=True, help_text="MaterialCommunityIcons name for React Native")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Amenities"

class Property(models.Model):
    # --- Choices ---
    PROPERTY_TYPE_CHOICES = [
        ('LAND', 'Land'), ('PLOT', 'Plot'), ('PG', 'PG/Hostel'),
        ('APARTMENT', 'Apartment'), ('HOUSE', 'House'), ('COMMERCIAL', 'Commercial'),
    ]

    UNIT_CHOICES = [
        ('SQFT', 'Sq. Ft.'), ('SQYD', 'Sq. Yards/GAJ'),('SQMTR','Sq. Mtr.'), ('ACRE', 'Acres'), ('MARLA', 'Marla'), ('KANAL','Kanal'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pending Verification'),
        ('VERIFIED', 'Verified & Live'),
        ('UNDERINQ','Under Inqiry'),
        ('SOLD', 'Sold/Closed'),
        ('REJECTED', 'Rejected'),
    ]

    # --- Core Info ---
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='listings')
    title = models.CharField(max_length=255)
    description = models.TextField()
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPE_CHOICES)
    listing_type = models.CharField(max_length=10, choices=[('RENT', 'Rent'), ('SALE', 'Sale')])
    
    # --- Dimensions & Pricing ---
    area = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0.1)])
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='SQYD')
    price = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(1)])
    
    # --- Detailed Specs (Optional based on type) ---
    bedrooms = models.PositiveIntegerField(null=True, blank=True)
    bathrooms = models.PositiveIntegerField(null=True, blank=True)
    amenities = models.ManyToManyField(Amenity, blank=True)

    # --- Location ---
    address = models.CharField(max_length=500)
    city = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    # --- Brokerage & Verification Logic ---
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    is_featured = models.BooleanField(default=False)
    admin_notes = models.TextField(blank=True, null=True, help_text="Internal notes for verification team")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.get_property_type_display()})"

class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='properties/gallery/%Y/%m/')
    is_main = models.BooleanField(default=False)

class VerificationDocument(models.Model):
    """
    Documents uploaded by owners for admin eyes only.
    """
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='documents')
    file = models.FileField(upload_to='properties/verification/%Y/')
    document_type = models.CharField(max_length=100, help_text="e.g. Possession Letter, Title Deed")

class Inquiry(models.Model):
    """
    The Lead Management System.
    """
    INQUIRY_STATUS = [
        ('NEW', 'New Lead'),
        ('CONTACTED', 'Broker Contacted'),
        ('VIEWING', 'Viewing Scheduled'),
        ('CLOSED_WON', 'Deal Closed'),
        ('CLOSED_LOST', 'Deal Not Done'),
    ]

    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='inquiries')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='my_inquiries')
    status = models.CharField(max_length=20, choices=INQUIRY_STATUS, default='NEW')
    admin_remarks = models.TextField(blank=True, null=True, help_text="Notes on the discussion with inquirer")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Inquiries"

class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='favorites'
    )
    property = models.ForeignKey(
        Property, 
        on_delete=models.CASCADE, 
        related_name='favorited_by'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Prevent duplicate favorites
        unique_together = ('user', 'property')
        verbose_name = "Favorite"
        verbose_name_plural = "Favorites"

    def __str__(self):
        return f"{self.user.phone} liked {self.property.title}"