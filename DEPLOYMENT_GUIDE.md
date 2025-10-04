# 🚀 Certificate Generation System - Deployment Guide

## Table of Contents
1. [Local Development](#local-development)
2. [Docker Deployment](#docker-deployment)
3. [Cloud Deployment](#cloud-deployment)
4. [Production Considerations](#production-considerations)
5. [Environment Configuration](#environment-configuration)
6. [Troubleshooting](#troubleshooting)

---

## 🏠 Local Development

### Prerequisites
- Python 3.11 or higher
- pip (Python package manager)

### Quick Start
```bash
# 1. Clone/navigate to the project directory
cd "Certificate Generation"

# 2. Create virtual environment (recommended)
python -m venv venv

# 3. Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run the application
python enhanced_web.py
```

The application will be available at `http://localhost:5000`

---

## 🐳 Docker Deployment (Recommended)

### Prerequisites
- Docker
- Docker Compose

### Quick Docker Deployment
```bash
# 1. Build and run with Docker Compose
docker-compose up --build

# 2. Access the application
# http://localhost:8000
```

### Custom Docker Build
```bash
# Build the image
docker build -t certificate-generator .

# Run the container
docker run -p 8000:8000 -v $(pwd)/certificates:/app/certificates certificate-generator
```

---

## ☁️ Cloud Deployment

### 1. **Heroku Deployment**

#### Prerequisites
- Heroku CLI installed
- Git repository

#### Steps:
```bash
# 1. Create Heroku app
heroku create your-certificate-app

# 2. Set environment variables
heroku config:set SECRET_KEY="your-secret-key"
heroku config:set SMTP_SERVER="smtp.gmail.com"
heroku config:set SMTP_USER="your-email@gmail.com"
heroku config:set SMTP_PASSWORD="your-app-password"

# 3. Create Procfile
echo "web: gunicorn wsgi:app" > Procfile

# 4. Deploy
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

### 2. **DigitalOcean Droplet**

#### Prerequisites
- DigitalOcean account
- SSH access to your droplet

#### Steps:
```bash
# 1. Connect to your droplet
ssh root@your-server-ip

# 2. Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# 3. Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 4. Clone your repository
git clone https://github.com/yourusername/certificate-generator.git
cd certificate-generator

# 5. Configure environment
cp .env.example .env
nano .env  # Edit configuration

# 6. Deploy
docker-compose up -d
```

### 3. **AWS EC2 Deployment**

#### Prerequisites
- AWS account
- EC2 instance running

#### Steps:
```bash
# 1. Connect to EC2 instance
ssh -i your-key.pem ec2-user@your-ec2-ip

# 2. Install Docker (Amazon Linux)
sudo yum update -y
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ec2-user

# 3. Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 4. Deploy application
git clone your-repository
cd certificate-generator
cp .env.example .env
# Edit .env file with your configuration
docker-compose up -d
```

### 4. **Google Cloud Platform (GCP)**

#### Using Cloud Run:
```bash
# 1. Build and push to Container Registry
gcloud builds submit --tag gcr.io/your-project-id/certificate-generator

# 2. Deploy to Cloud Run
gcloud run deploy certificate-generator \
    --image gcr.io/your-project-id/certificate-generator \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 1Gi \
    --cpu 1 \
    --timeout 300
```

---

## 🔧 Production Considerations

### 1. **Security**
- Change the `SECRET_KEY` in production
- Use environment variables for sensitive data
- Enable HTTPS/SSL certificates
- Configure firewall rules
- Regular security updates

### 2. **Performance**
- Use a reverse proxy (Nginx) for static files
- Configure proper caching headers
- Monitor resource usage
- Consider using a CDN for file delivery

### 3. **Monitoring**
```bash
# View container logs
docker-compose logs -f certificate-app

# Monitor system resources
docker stats

# Health check
curl http://localhost:8000/
```

### 4. **Backup Strategy**
```bash
# Backup database and files
docker-compose exec certificate-app tar -czf backup.tar.gz certificates.db certificates/ qr_codes/

# Restore backup
docker-compose exec certificate-app tar -xzf backup.tar.gz
```

---

## 🔐 Environment Configuration

### Required Environment Variables:
```bash
# Application
SECRET_KEY=your-secret-key
FLASK_ENV=production
PORT=8000

# Email (for certificate sending)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Optional: Twilio (for WhatsApp)
TWILIO_ACCOUNT_SID=your-sid
TWILIO_AUTH_TOKEN=your-token
TWILIO_PHONE_NUMBER=+1234567890
```

### Gmail App Password Setup:
1. Enable 2-Factor Authentication on your Gmail account
2. Go to Google Account settings > Security > App passwords
3. Generate an app password for "Mail"
4. Use this password in `SMTP_PASSWORD`

---

## 🔍 Troubleshooting

### Common Issues:

#### 1. **Port Already in Use**
```bash
# Find process using port
netstat -ano | findstr :8000
# Kill process (Windows)
taskkill /PID <process_id> /F
```

#### 2. **Docker Build Fails**
```bash
# Clean Docker cache
docker system prune -a
docker-compose build --no-cache
```

#### 3. **Database Issues**
```bash
# Reset database (WARNING: Deletes all data)
rm certificates.db
python enhanced_web.py  # Will recreate database
```

#### 4. **PDF Generation Fails**
```bash
# Install missing dependencies
pip install pillow reportlab qrcode[pil]
```

#### 5. **Email Sending Fails**
- Check Gmail app password setup
- Verify SMTP settings
- Check firewall/network restrictions

### Logs and Debugging:
```bash
# View application logs
docker-compose logs certificate-app

# Interactive debugging
docker-compose exec certificate-app python

# Check file permissions
ls -la certificates/ qr_codes/
```

---

## 📊 Performance Monitoring

### Basic Monitoring:
```bash
# Resource usage
docker stats

# Application health
curl -f http://localhost:8000/ || echo "Service Down"

# Log monitoring
tail -f logs/application.log
```

### Advanced Monitoring (Optional):
- Use tools like Prometheus + Grafana
- Set up log aggregation with ELK stack
- Configure uptime monitoring services

---

## 🆙 Updates and Maintenance

### Updating the Application:
```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose up --build -d

# Database migration (if needed)
docker-compose exec certificate-app python migrate_database.py
```

### Regular Maintenance:
- Monitor disk space for generated certificates
- Clean up old certificates periodically
- Update dependencies for security patches
- Backup database regularly

---

## 🎯 Production Checklist

Before going live, ensure:

- [ ] Environment variables configured
- [ ] Secret key changed from default
- [ ] Email SMTP settings tested
- [ ] SSL/HTTPS configured (for production domains)
- [ ] Firewall rules configured
- [ ] Backup strategy implemented
- [ ] Monitoring setup
- [ ] Domain name configured (if applicable)
- [ ] Health checks working
- [ ] Load testing completed (if expecting high traffic)

---

## 📞 Support

For deployment issues:
1. Check the logs: `docker-compose logs certificate-app`
2. Verify environment configuration
3. Test individual components (email, PDF generation)
4. Review this troubleshooting guide

---

**🎉 Your Certificate Generation System is ready for deployment!**