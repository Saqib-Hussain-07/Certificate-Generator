@echo off
echo 🚀 Certificate Generation System - Windows Deployment Script
echo ===========================================================

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not installed. Please install Docker Desktop first.
    pause
    exit /b 1
)

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose is not installed. Please install Docker Compose first.
    pause
    exit /b 1
)

echo ✅ Docker and Docker Compose found

REM Create .env file if it doesn't exist
if not exist .env (
    echo 📝 Creating .env file from template...
    copy .env.example .env
    echo ⚠️  Please edit .env file with your configuration before continuing
    echo    Especially update: SECRET_KEY, SMTP_* settings
    pause
)

REM Create necessary directories
echo 📁 Creating necessary directories...
if not exist certificates mkdir certificates
if not exist qr_codes mkdir qr_codes

REM Build and start the application
echo 🔨 Building Docker containers...
docker-compose build

echo 🚀 Starting the application...
docker-compose up -d

REM Wait a moment for the application to start
echo ⏳ Waiting for application to start...
timeout /t 15 /nobreak >nul

REM Health check
echo 🔍 Checking application health...
powershell -Command "try { Invoke-WebRequest -Uri http://localhost:8000 -UseBasicParsing -TimeoutSec 5 | Out-Null; Write-Host '✅ Application is running successfully!' } catch { Write-Host '❌ Application health check failed' }"

echo.
echo 🌐 Access your application at: http://localhost:8000
echo 📊 View logs with: docker-compose logs -f certificate-app  
echo 🛑 Stop application with: docker-compose down
echo.
echo 🎉 Deployment complete!
pause