import os
import requests
import django
from django.conf import settings

# Setup Django to access settings if needed, or just use requests directly
# We'll use requests to simulate an external ERP system
BASE_URL = "http://127.0.0.1:8000/api/erp/properties/"
API_KEY = "your-secure-random-api-key-here" # Matches what we added to .env

def test_erp_endpoint():
    print("--- Testing ERP Endpoint ---")
    
    # 1. Test without Key (Should Fail)
    print("\n1. Requesting WITHOUT API Key...")
    try:
        response = requests.get(BASE_URL)
        print(f"   Status Code: {response.status_code}")
        if response.status_code in [401, 403]:
            print("   SUCCESS: Access Denied as expected.")
        else:
            print("   FAILURE: Access was NOT denied.")
    except Exception as e:
        print(f"   Error: {e}")

    # 2. Test with WRONG Key (Should Fail)
    print("\n2. Requesting with WRONG API Key...")
    try:
        headers = {'X-ERP-API-Key': 'wrong-key'}
        response = requests.get(BASE_URL, headers=headers)
        print(f"   Status Code: {response.status_code}")
        if response.status_code in [401, 403]:
             print("   SUCCESS: Access Denied as expected.")
        else:
             print("   FAILURE: Access was NOT denied.")
    except Exception as e:
        print(f"   Error: {e}")

    # 3. Test with CORRECT Key (Should Success)
    print("\n3. Requesting with CORRECT API Key...")
    try:
        headers = {'X-ERP-API-Key': API_KEY}
        response = requests.get(BASE_URL, headers=headers)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            # Handle pagination if default pagination is on, otherwise it might be a list
            results = data.get('results', data) if isinstance(data, dict) else data
            
            print(f"   SUCCESS: Data retrieved. Found {len(results)} properties.")
            if results:
                print(f"   Sample: {results[0]['title']} - Price: {results[0]['price']}")
                if 'owner_phone' in results[0]:
                    print(f"   Verified Owner Phone field is present: {results[0]['owner_phone']}")
                else:
                    print("   WARNING: Owner Phone field missing.")
        else:
            print(f"   FAILURE: {response.text}")

    except Exception as e:
        print(f"   Error: {e}")
        # Hint: Is the server running?
        print("   (Ensure the Django server is running on localhost:8000)")

if __name__ == "__main__":
    test_erp_endpoint()
