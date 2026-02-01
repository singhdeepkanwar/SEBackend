import os
import django
from django.core.files.uploadedfile import SimpleUploadedFile
from io import BytesIO
from PIL import Image

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from listings.models import Property, PropertyImage
from listings.serializers import PropertyCreateSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

def create_test_image():
    file_obj = BytesIO()
    image = Image.new('RGB', (100, 100), color='red')
    image.save(file_obj, 'png')
    file_obj.seek(0)
    return SimpleUploadedFile("test_image.png", file_obj.read(), content_type="image/png")

def test_image_update():
    # 1. Setup - Get or create a property
    user, _ = User.objects.get_or_create(phone='1234567890')
    prop, created = Property.objects.get_or_create(
        owner=user,
        title="Test Property for Image Update",
        defaults={
            'description': "Testing image additions and deletions",
            'property_type': 'HOUSE',
            'listing_type': 'SALE',
            'area': 1000,
            'price': 5000000,
            'address': "Test Address",
            'city': "Test City"
        }
    )
    
    # Add an initial image
    initial_img = PropertyImage.objects.create(property=prop, image=create_test_image())
    print(f"Created property with initial image ID: {initial_img.id}")
    
    # 2. Test PATCH - Add one, delete one
    new_img_file = create_test_image()
    data = {
        'uploaded_images': [new_img_file],
        'deleted_image_ids': [initial_img.id]
    }
    
    serializer = PropertyCreateSerializer(prop, data=data, partial=True)
    if serializer.is_valid():
        updated_prop = serializer.save()
        print("Serializer saved successfully.")
    else:
        print(f"Serializer errors: {serializer.errors}")
        return

    # 3. Verification
    images = PropertyImage.objects.filter(property=updated_prop)
    image_ids = list(images.values_list('id', flat=True))
    
    print(f"Final images IDs: {image_ids}")
    
    success = True
    if initial_img.id in image_ids:
        print("FAILURE: Deleted image still present.")
        success = False
    
    if len(image_ids) != 1:
         print(f"FAILURE: Expected 1 image, found {len(image_ids)}.")
         success = False
    
    if success:
        print("SUCCESS: Image addition and deletion verified.")

if __name__ == "__main__":
    test_image_update()
