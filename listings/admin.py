from django.contrib import admin
from .models import *
from django.utils.html import format_html
from django.forms import CheckboxSelectMultiple


class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1
    readonly_fields = ['thumbnail']

    def thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 100px; height: auto;" />', obj.image.url)
        return "No Image"

class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 3

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'property_type', 'status', 'price', 'is_featured')
    list_filter = ('status', 'property_type', 'city')
    search_fields = ('title', 'address', 'owner__phone')
    inlines = [PropertyImageInline]
    
    # This displays ManyToMany fields (amenities) as checkboxes
    formfield_overrides = {
        models.ManyToManyField: {'widget': CheckboxSelectMultiple},
    }
    
    # Actions to quickly verify properties from the list view
    actions = ['make_verified', 'make_sold']

    def make_verified(self, request, queryset):
        queryset.update(status='VERIFIED')
    make_verified.short_description = "Mark selected properties as Verified"

@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ('property', 'user', 'status', 'created_at')
    list_filter = ('status',)
    readonly_fields = ('created_at',)

admin.site.register(Amenity)
admin.site.register(Favorite)


