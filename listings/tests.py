from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Property, Amenity
from decimal import Decimal

User = get_user_model()

class PropertyTests(APITestCase):

    def setUp(self):
        # Create user
        self.user = User.objects.create_user(phone="9876543210", password="password")
        self.client.force_authenticate(user=self.user)
        
        # Create Amenity
        self.amenity = Amenity.objects.create(name="WiFi", icon_name="wifi")

        # Sample Property Data
        self.property_data = {
            "title": "Luxury Apartment",
            "description": "A very nice place",
            "property_type": "APARTMENT",
            "listing_type": "SALE",
            "area": 1500.00,
            "unit": "SQFT",
            "price": 5000000.00,
            "address": "123 Main St",
            "city": "Metropolis",
            "amenities": [self.amenity.id]
        }

    def test_create_property(self):
        """
        Test creating a property listing.
        """
        url = '/api/properties/' # Assuming standard router path
        response = self.client.post(url, self.property_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Property.objects.count(), 1)
        self.assertEqual(Property.objects.get().title, "Luxury Apartment")

    def test_create_property_unauthenticated(self):
        """
        Test that unauthenticated users cannot create properties.
        """
        self.client.logout()
        url = '/api/properties/'
        response = self.client.post(url, self.property_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_properties(self):
        """
        Test listing properties.
        """
        # Create a property first
        Property.objects.create(
            owner=self.user,
            **{k:v for k,v in self.property_data.items() if k != 'amenities'}, # simple create
            status='VERIFIED'
        )
        
        url = '/api/properties/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check if list is not empty (format depends on pagination)
        # Assuming default pagination
        if 'results' in response.data:
             self.assertTrue(len(response.data['results']) >= 1)
        else:
             self.assertTrue(len(response.data) >= 1)

    def test_retrieve_property(self):
        """
        Test retrieving a single property.
        """
        prop = Property.objects.create(
            owner=self.user,
            **{k:v for k,v in self.property_data.items() if k != 'amenities'},
            status='VERIFIED'
        )
        
        url = f'/api/properties/{prop.id}/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "Luxury Apartment")


class InquiryTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(phone="1111111111", password="password")
        self.inquirer = User.objects.create_user(phone="2222222222", password="password")
        
        self.prop = Property.objects.create(
            owner=self.owner,
            title="Test Property",
            description="Desc",
            property_type="HOUSE",
            listing_type="RENT",
            area=100,
            price=1000,
            address="Addr",
            city="City"
        )
        
        self.client.force_authenticate(user=self.inquirer)

    def test_create_inquiry(self):
        """
        Test creating an inquiry for a property.
        """
        url = '/api/inquiries/'
        data = {
            "property": self.prop.id,
            # User is inferred from auth usually, or passed explicitly? 
            # ViewSet usually takes user from request.user
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.prop.inquiries.count(), 1)
        self.assertEqual(self.prop.inquiries.first().user, self.inquirer)
