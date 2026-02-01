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

def create_test_image(name="test.png", color='red'):
    file_obj = BytesIO()
    image = Image.new('RGB', (100, 100), color=color)
    image.save(file_obj, 'png')
    file_obj.seek(0)
    return SimpleUploadedFile(name, file_obj.read(), content_type="image/png")

def test_full_flow():
    print("--- Starting Full Flow Verification ---")
    
    # 1. Login / Setup User
    user, _ = User.objects.get_or_create(phone='9876543210', defaults={'first_name': 'Test', 'last_name': 'User'})
    print(f"1. User setup complete: {user.phone}")

    # 2. Create New Property with Image
    print("\n2. Creating new property with 1 image...")
    img1 = create_test_image(name="img1.png", color='blue')
    
    create_data = {
        'title': "Brand New Villa",
        'description': "Freshly created via serializer",
        'property_type': 'HOUSE',
        'listing_type': 'SALE',
        'area': 2500,
        'price': 15000000,
        'address': "123 Test Lane",
        'city': "Sangrur",
        'uploaded_images': [img1] 
    }
    
    # We simulate the View's perform_create by passing owner to save()
    create_serializer = PropertyCreateSerializer(data=create_data)
    if create_serializer.is_valid():
        prop = create_serializer.save(owner=user)
        print(f"   Property created: ID {prop.id} - {prop.title}")
    else:
        print(f"   CREATION FAILED: {create_serializer.errors}")
        return

    # Verify initial state
    initial_images = list(prop.images.all())
    print(f"   Initial Images count: {len(initial_images)}")
    if len(initial_images) != 1:
        print("   FAILURE: Expected 1 image.")
        return
    img_to_delete = initial_images[0]
    print(f"   Image to delete later: ID {img_to_delete.id}")


    # 3. Update Property (Delete Old, Add New)
    print("\n3. Updating property: Deleting old image, Adding new green image...")
    
    img2 = create_test_image(name="img2.png", color='green')
    
    update_data = {
        'title': "Updated Villa Title",
        'delete_images': [img_to_delete.id],
        'uploaded_images': [img2]
    }
    
    update_serializer = PropertyCreateSerializer(prop, data=update_data, partial=True)
    if update_serializer.is_valid():
        updated_prop = update_serializer.save()
        print("   Update successful.")
    else:
        print(f"   UPDATE FAILED: {update_serializer.errors}")
        return

    # 4. Final Verification
    print("\n4. Verifying Final State...")
    final_images = list(updated_prop.images.all())
    final_ids = [img.id for img in final_images]
    
    print(f"   Final Images IDs: {final_ids}")
    
    # Check deletion
    if img_to_delete.id in final_ids:
        print(f"   FAILURE: Old image {img_to_delete.id} was NOT deleted.")
    else:
        print(f"   SUCCESS: Old image {img_to_delete.id} was deleted.")
        
    # Check addition
    # We expect 1 image total (deleted 1, added 1) and ID should be different
    if len(final_images) == 1 and final_images[0].id != img_to_delete.id:
         print(f"   SUCCESS: New image added (ID {final_images[0].id}).")
    else:
         print(f"   FAILURE: Expected 1 new image, found {len(final_images)}.")

    # Check update fields
    if updated_prop.title == "Updated Villa Title":
        print("   SUCCESS: Title updated.")
    else:
        print("   FAILURE: Title not updated.")

if __name__ == "__main__":
    test_full_flow()
