# AWS Deployment Guide

This guide describes how to deploy the Sangrur Estate Backend to AWS using EC2, RDS, and S3.

## 1. Amazon S3 (Media Files)
S3 will store all uploaded images and documents.

1.  **Create Bucket:** 
    - Go to S3 Console -> Create Bucket.
    - Name: `sangrur-estate-media` (or your preferred name).
    - Uncheck "Block all public access" (if you want public URLs for images) OR keep it checked and use a CloudFront distribution (recommended for production).
2.  **IAM User:**
    - Create an IAM user with `AmazonS3FullAccess` (or custom policy for specific bucket).
    - Generate Access Key and Secret Key.
3.  **Environment Variables:**
    - Update `.env` on EC2 with:
      ```
      USE_AWS_S3=True
      AWS_ACCESS_KEY_ID=your_key
      AWS_SECRET_ACCESS_KEY=your_secret
      AWS_STORAGE_BUCKET_NAME=sangrur-estate-media
      AWS_S3_REGION_NAME=ap-south-1
      ```

## 2. Amazon RDS (Database)
RDS (PostgreSQL) is used for the production database.

1.  **Create Instance:**
    - Select PostgreSQL.
    - Tier: Free Tier (for testing) or Production.
    - Configure DB name, master username, and password.
2.  **Security Group:**
    - Ensure the RDS security group allows inbound traffic on port 5432 from the EC2 security group.
3.  **Environment Variables:**
    - `DATABASE_URL=postgres://username:password@rds-endpoint:5432/dbname`

## 3. Amazon EC2 (Application Server)
EC2 will run the Django application.

1.  **Launch Instance:**
    - Ubuntu 22.04 LTS is recommended.
    - Security Group: Allow HTTP (80), HTTPS (443), and SSH (22).
2.  **Setup Server:**
    ```bash
    sudo apt update
    sudo apt install python3-pip python3-venv git -y
    ```
3.  **Clone & Configure:**
    ```bash
    git clone <your-repo-url>
    cd SangrurEstateBackend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```
4.  **Gunicorn & Nginx:**
    - Use Gunicorn as the application server.
    - Use Nginx as a reverse proxy to handle requests and serve static files.

## 4. Gunicorn & Nginx Setup

### 4.1. Gunicorn Configuration
Gunicorn will run the Django application and listen on a Unix socket.

1.  **Create Socket:**
    `sudo nano /etc/systemd/system/gunicorn.socket` (See `deployment/gunicorn.socket`)
2.  **Create Service:**
    `sudo nano /etc/systemd/system/gunicorn.service` (See `deployment/gunicorn.service`)
    *Ensure `WorkingDirectory` and `ExecStart` match your project path.*
3.  **Start & Enable:**
    ```bash
    sudo systemctl start gunicorn.socket
    sudo systemctl enable gunicorn.socket
    ```

### 4.2. Nginx Configuration
Nginx acts as a reverse proxy and serves static/media files.

1.  **Create Config:**
    `sudo nano /etc/nginx/sites-available/sebackend` (See `deployment/nginx.conf`)
2.  **Enable Site:**
    ```bash
    sudo ln -s /etc/nginx/sites-available/sebackend /etc/nginx/sites-enabled
    sudo nginx -t
    sudo systemctl restart nginx
    ```

## 5. Deployment Checklist & Security

### 5.1. Static Files
Before restarting Nginx, collect all static files:
```bash
python3 manage.py collectstatic --noinput
```

### 5.2. Debugging `DATABASE_URL`
If you see `UnknownSchemeError: Scheme '://' is unknown`, ensure your `.env` has a valid `DATABASE_URL`.
*   **For RDS:** `DATABASE_URL=postgres://user:password@host:5432/dbname`
*   **For Local SQLite (Default):** Leave `DATABASE_URL` empty or comment it out in `.env`.
*   **Manual SQLite:** `DATABASE_URL=sqlite:////home/ubuntu/SEBackend/db.sqlite3` (Note the 4 slashes for absolute path).

### 5.3. Permissions
Ensure `www-data` has access to the project:
```bash
sudo chown -R :www-data /home/ubuntu/SEBackend
chmod -R 775 /home/ubuntu/SEBackend/media
```

### 5.4. Production Security
Ensure the following are set in your EC2 `.env`:
- `DEBUG=False`
- `ALLOWED_HOSTS=your-domain.com,your-ec2-ip`
- `SECRET_KEY=a-very-long-random-string`
- `SECURE_SSL_REDIRECT=True` (after setting up SSL via Certbot/Let's Encrypt)
