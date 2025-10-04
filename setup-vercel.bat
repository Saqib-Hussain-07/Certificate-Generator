@echo off
echo 🚀 Setting up Certificate Generator for Vercel Deployment
echo =======================================================

REM Check if git is initialized
if not exist ".git" (
    echo 📝 Initializing Git repository...
    git init
    echo ⚠️  Remember to create a GitHub repository and add it as remote:
    echo    git remote add origin https://github.com/yourusername/certificate-generator.git
) else (
    echo ✅ Git repository already initialized
)

REM Create .gitignore if it doesn't exist
if not exist ".gitignore" (
    echo 📝 Creating .gitignore file...
    (
        echo # Environment variables
        echo .env
        echo .env.local
        echo .env.production
        echo.
        echo # Python
        echo __pycache__/
        echo *.pyc
        echo *.pyo
        echo *.pyd
        echo .Python
        echo *.so
        echo.
        echo # Local development files
        echo certificates/
        echo qr_codes/
        echo certificates.db*
        echo.
        echo # Vercel
        echo .vercel
        echo.
        echo # OS files
        echo .DS_Store
        echo Thumbs.db
        echo.
        echo # IDE files
        echo .vscode/
        echo .idea/
    ) > .gitignore
    echo ✅ .gitignore created
) else (
    echo ✅ .gitignore already exists
)

REM Check for required files
echo 🔍 Checking Vercel configuration files...

if exist "vercel.json" (
    echo ✅ vercel.json exists
) else (
    echo ❌ vercel.json missing
)

if exist "vercel_app.py" (
    echo ✅ vercel_app.py exists
) else (
    echo ❌ vercel_app.py missing
)

if exist "requirements-vercel.txt" (
    echo ✅ requirements-vercel.txt exists
) else (
    echo ❌ requirements-vercel.txt missing
)

if exist ".vercelignore" (
    echo ✅ .vercelignore exists
) else (
    echo ❌ .vercelignore missing
)

echo.
echo 📋 Next Steps for Vercel Deployment:
echo ====================================
echo.
echo 1. 🔧 Configure Environment Variables:
echo    - Copy .env.example to .env
echo    - Update with your actual credentials
echo    - Set these same variables in Vercel dashboard
echo.
echo 2. 📤 Push to GitHub:
echo    - Create repository on GitHub
echo    - git remote add origin https://github.com/yourusername/repo-name.git
echo    - git add .
echo    - git commit -m "Deploy Certificate Generator to Vercel"
echo    - git push -u origin main
echo.
echo 3. 🚀 Deploy on Vercel:
echo    - Go to vercel.com and sign in with GitHub
echo    - Import your repository
echo    - Configure environment variables
echo    - Deploy!
echo.
echo 4. 📖 Read the full guide:
echo    - Check VERCEL_DEPLOYMENT.md for detailed instructions
echo.
echo 🎉 Setup complete! Ready for Vercel deployment.
pause