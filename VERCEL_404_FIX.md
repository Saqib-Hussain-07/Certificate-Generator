# 🔧 Vercel 404 Error - Fix Guide

## 📋 Problem Description
You're getting a `404: NOT_FOUND` error on Vercel because the original configuration wasn't properly set up for Flask applications in serverless functions.

## ✅ Solution Applied

I've restructured your project to work with Vercel's serverless architecture:

### 📁 New File Structure
```
your-project/
├── api/
│   ├── index.py              # Main Flask app entry point
│   └── certificate_generator.py  # Vercel-compatible generator
├── templates/                # Your HTML templates (unchanged)
├── vercel.json              # Fixed Vercel configuration
└── requirements-vercel.txt   # Dependencies for Vercel
```

### 🔧 Key Changes Made

1. **Fixed `vercel.json`**:
   - Simplified routing configuration
   - Uses rewrites instead of complex routing
   - Points all requests to `/api/index`

2. **Created `/api/index.py`**:
   - Proper Flask app entry point for Vercel
   - Handles all your routes
   - Uses temporary file storage (`/tmp`)
   - Vercel-compatible database setup

3. **Created `/api/certificate_generator.py`**:
   - Modified for serverless environment
   - Uses `/tmp` directory for file storage
   - Handles database initialization properly

## 🚀 How to Deploy the Fix

### Method 1: Push to GitHub (Automatic)
```bash
# Commit the new files
git add .
git commit -m "Fix: Restructure for Vercel serverless compatibility"
git push origin main

# Vercel will automatically redeploy
```

### Method 2: Manual Vercel Deploy
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy from your project directory
vercel --prod
```

## ⚙️ Environment Variables to Set

In your Vercel dashboard, make sure you have:

```bash
SECRET_KEY=your-random-secret-key-here
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-gmail-app-password
```

## 🧪 Testing After Fix

1. **Visit your Vercel URL**: `https://your-project.vercel.app`
2. **Test main page**: Should load without 404 error
3. **Test certificate generation**: Try creating a certificate
4. **Check Vercel logs**: View function execution logs in dashboard

## 🔍 Why This Fixes the 404 Error

### ❌ **Previous Issue**:
- Vercel couldn't find the Flask app entry point
- Routing configuration was too complex
- Flask app wasn't properly wrapped for serverless

### ✅ **Current Solution**:
- Clean `/api/index.py` entry point
- Simple routing with rewrites
- Proper Flask app export for Vercel
- Temporary file system handling

## 📊 Vercel Function Limitations Handled

1. **File Storage**: Uses `/tmp` directory (temporary but works)
2. **Database**: SQLite in `/tmp` (resets on each deployment)
3. **Execution Time**: Optimized for 60-second timeout
4. **Memory**: Efficient resource usage

## 🎯 Next Steps After Fix

1. **Verify deployment works**
2. **Test all functionality**
3. **Consider external database** for data persistence
4. **Set up file storage service** for permanent certificate storage

## 🐛 If Still Getting 404

1. **Check Vercel dashboard logs**:
   - Go to your project in Vercel
   - Click on "Functions" tab
   - View execution logs

2. **Verify file structure**:
   ```bash
   ls api/
   # Should show: index.py, certificate_generator.py
   ```

3. **Check vercel.json syntax**:
   - Must be valid JSON
   - Simple rewrite rule only

4. **Environment variables**:
   - Make sure they're set in Vercel dashboard
   - No syntax errors in variable names

## 📞 Additional Debugging

If you're still having issues:

1. **Check build logs** in Vercel deployment page
2. **Verify Python dependencies** in requirements-vercel.txt
3. **Test locally** with `vercel dev`
4. **Check function timeout** (should be under 60 seconds)

---

**🎉 After applying these fixes, your Certificate Generator should work perfectly on Vercel!**