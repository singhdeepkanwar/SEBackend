🏠 Real Estate App: Backend Documentation
1. Overview
A secure, OTP-first authentication system built with Django, Django Rest Framework (DRF), and SimpleJWT. The system prioritizes user conversion by verifying phone numbers before requiring profile data (Option B flow).

2. Core Architecture
The backend is designed to be stateless and resilient. It handles the transition from an anonymous visitor to a verified user through a secure handshake.

Key Logic Flow:

Initiation: User provides phone number via /send-otp/.

Verification: User provides OTP via /verify-otp/.

Branching:

Existing User: Returns standard JWT Access/Refresh tokens (Login).

New User: Returns a short-lived registration_token (Signup Gate).

Finalization: New user submits profile using the registration_token via /register/.

3. Database Schema
User Model

Extends AbstractBaseUser.

phone: (Unique) Primary login identifier.

full_name: User's display name.

email: User's contact email.

address: Physical address for real estate profiling.

city: Primary location.

is_profile_complete: Boolean to track if registration is finished.

OTPSession Model

Gatekeeper for the SMS flow.

session_id: UUID (Primary identifier passed to the frontend).

phone: Target phone number.

otp_code: 4-digit code.

attempts: Counter (Session invalidates after 3 failed tries).

is_verified: Boolean to prevent session reuse after success.

created_at: Timestamp for expiry (5-minute TTL).

4. API Specification
[POST] /api/auth/send-otp/

Purpose: Initiates the authentication process.

Input: { "phone": "+1234567890" }

Output: 200 OK with { "session_id": "uuid-string" }

[POST] /api/auth/verify-otp/

Purpose: Validates the OTP code.

Input: { "session_id": "uuid", "otp_code": "1234" }

Response (Existing User):

JSON
{ 
  "status": "LOGIN", 
  "access": "jwt_access_token", 
  "refresh": "jwt_refresh_token",
  "is_profile_complete": true 
}
Response (New User):

JSON
{ 
  "status": "SIGNUP", 
  "registration_token": "temporary_jwt_token" 
}
[POST] /api/auth/register/

Purpose: Finalizes profile creation for new users.

Security: Requires registration_token in Authorization: Bearer <token> header.

Input: { "full_name": "...", "email": "...", "address": "...", "city": "..." }

Output: 201 Created with full Access/Refresh tokens.

5. Security & Maintenance
Feature	Implementation
Throttling	ScopedRateThrottle (3/min for sending, 5/min for verifying).
Anti-Brute Force	Session invalidates after 3 failed attempts.
Atomicity	transaction.atomic() used during User creation.
Token Scoping	registration_token carries a custom purpose: registration claim.
Cleanup	Management command cleanup_otp purges sessions older than 24 hours.
6. Development Config
settings.py

Python
AUTH_USER_MODEL = 'accounts.User'

# CORS
CORS_ALLOW_ALL_ORIGINS = True
ALLOWED_HOSTS = ['*']

# DRF Throttling
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_RATES': {
        'otp_send': '3/min',
        'otp_verify': '5/min',
        'user': '1000/day',
        'anon': '100/day',
    }
}
Run Command

Bash
python manage.py runserver 0.0.0.0:8000


# DOC 2
📑 Managed Brokerage: Backend Technical Documentation
1. System Architecture
The backend is built on Django and Django Rest Framework (DRF) using a Stateless JWT Authentication system. It follows a "Gated Content" model where listings must be verified by an Admin before becoming public.

2. Database Schema (Core Models)
A. Accounts App (Identity)

User: Custom model using phone as the USERNAME_FIELD. Includes profile fields (full_name, email, city).

OTPSession: Temporary storage for 4-digit codes linked to a session_id.

B. Listings App (Business Logic)

Property: The central model. Includes status (PENDING, VERIFIED, SOLD, REJECTED), property_type (LAND, PG, HOUSE, etc.), and area/unit.

PropertyImage: Multiple images per property with an is_main flag for the cover photo.

VerificationDocument: [Admin Only] Private storage for title deeds/legal docs.

Inquiry: The "Lead" model. Connects a Buyer to a Property. Tracks broker status (CONTACTED, VIEWING, etc.).

Favorite: The "Warm Lead" model. Tracks user interest.

Amenity: Global list of features (e.g., Wifi, Parking, Security).

3. API Endpoints: Authentication
Endpoint	Method	Payload	Description
/api/auth/send-otp/	POST	{"phone": "+91..."}	Sends SMS/Console OTP. Returns session_id.
/api/auth/verify-otp/	POST	{"session_id": "...", "otp_code": "..."}	Returns registration_token (New) or JWT (Existing).
/api/auth/register/	POST	{"full_name": "...", "email": "..."}	Uses registration_token in Header to create User.
/api/auth/logout/	POST	{"refresh": "..."}	Blacklists the refresh token.
4. API Endpoints: Property Management
A. Submit a Listing (User/Owner)

Endpoint: /api/properties/

Method: POST (Requires Authorization: Bearer <Access_Token>)

Payload (form-data):

JSON
{
  "title": "3BHK Luxury Flat",
  "description": "Near city center",
  "property_type": "APARTMENT", // LAND, PLOT, PG, HOUSE, COMMERCIAL
  "listing_type": "SALE", // SALE or RENT
  "area": 1500.00,
  "unit": "SQFT", // SQFT, SQYD, ACRE, MARLA
  "price": 7500000,
  "bedrooms": 3, // Optional
  "bathrooms": 2, // Optional
  "city": "Sangrur",
  "address": "Street 5, Phase 1",
  "amenities": [1, 4, 5], // IDs of amenities
  "uploaded_images": [file1, file2] // Multi-file upload
}
Note: Created with status="PENDING". User cannot change this.

B. Browse Listings (Public)

Endpoint: /api/properties/

Method: GET

Filters: ?city=Sangrur&price__gte=1000000&property_type=LAND

Search: ?search=Luxury+Villa

Response: Only returns VERIFIED properties.

5. API Endpoints: Lead & Brokerage Logic
C. Express Interest (Inquiry)

Endpoint: /api/inquiries/

Method: POST

Payload: {"property": "UUID_HERE"}

Action: Triggers a Django Signal that sends an immediate email alert to the Admin.

D. Favorite (Soft Lead)

Endpoint: /api/properties/{id}/toggle_favorite/

Method: POST

Result: {"status": "favorited"} or {"status": "unfavorited"}.

6. Admin Control Features (The Broker's Dashboard)
These endpoints are restricted to is_staff=True.

E. Verify Property (Gating)

Endpoint: /api/properties/{id}/verify_property/

Method: POST

Payload:

JSON
{
  "status": "VERIFIED", // or REJECTED
  "admin_notes": "Docs checked, phone verified",
  "is_featured": true, // Pushes to top of app
  "uploaded_documents": [file] // Internal legal docs
}
F. Lead Management

Endpoint: /api/inquiries/{id}/update_lead_status/

Method: PATCH

Payload: {"status": "VIEWING", "admin_remarks": "User visiting on Sunday"}

G. Admin Summary (Business Intelligence)

Endpoint: /api/properties/admin_dashboard/

Method: GET

Data Returned:

Count of Pending vs Verified properties.

Total number of New leads.

Total Inventory Value: Combined price of all verified listings.

Recent Inquiries list.

7. Security & Business Rules
Statelessness: No session storage on server. Everything relies on JWT.

Stateless Registration: The registration_token ensures a user can't skip phone verification and jump to registration.

Middleman Protection: Owners never see Inquirer details. Only Admins can see the Inquiry list.

Automatic Notifications: Django Signals ensure no lead is missed by emailing the broker instantly.