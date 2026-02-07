import requests
import random
import io
from PIL import Image

def generate_tiny_image(color):
    file = io.BytesIO()
    image = Image.new('RGB', (100, 100), color)
    image.save(file, 'JPEG')
    file.name = f'test_image_{color[0]}_{color[1]}_{color[2]}.jpg'
    file.seek(0)
    return file

def test_bulk_creation():
    url = "https://backend.sangrurestate.com/api/properties/"
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzcwMjEzMzg5LCJpYXQiOjE3NzAyMDk3ODksImp0aSI6ImFlMmI4YTZkZWM5NjRiNjNiNDgwMmEyOThjZTVjZjZlIiwidXNlcl9pZCI6IjEifQ.0s6kYXntxsqPCbWGvfq03iQ-RQFD4jj9-pNQp3mUgIY"
    headers = {"Authorization": f"Bearer {token}"}

    property_types = ['LAND', 'PLOT', 'PG', 'APARTMENT', 'HOUSE', 'COMMERCIAL']
    listing_types = ['RENT', 'SALE']
    units = ['SQFT', 'SQYD', 'SQMTR', 'ACRE', 'MARLA', 'KANAL']
    cities = ['Sangrur', 'Patiala', 'Ludhiana', 'Chandigarh', 'Barnala']

    print(f"Starting bulk creation of 100 properties...")

    for i in range(1, 101):
        data = {
            "title": f"Test Property {i} - {random.choice(['Luxury', 'Cozy', 'Spacious'])} {random.choice(['Villa', 'Plot', 'Flat'])}",
            "description": f"This is a dummy test property number {i}. It has multiple images and random specs for testing the server capacity.",
            "property_type": random.choice(property_types),
            "listing_type": random.choice(listing_types),
            "area": random.randint(50, 5000),
            "unit": random.choice(units),
            "price": random.randint(500000, 50000000),
            "address": f"Street {random.randint(1, 100)}, Phase {random.randint(1, 10)}",
            "city": random.choice(cities),
            "bedrooms": random.randint(1, 6),
            "bathrooms": random.randint(1, 4),
        }

        # Generate 2-3 images
        num_images = random.randint(2, 3)
        files = []
        for j in range(num_images):
            # Alternate colors to see diversity
            color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            files.append(('uploaded_images', generate_tiny_image(color)))

        try:
            response = requests.post(url, data=data, files=files, headers=headers)
            if response.status_code == 201:
                print(f"[{i}/100] Created: {data['title']}")
            else:
                print(f"[{i}/100] FAILED: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"[{i}/100] ERROR: {e}")

if __name__ == "__main__":
    test_bulk_creation()
