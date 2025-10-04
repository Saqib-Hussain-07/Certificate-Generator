# 🚀 Vercel Deployment Guide - Certificate Generation System

## 📋 Overview

This guide will help you deploy your Certificate Generation System to **Vercel** using **GitHub** integration. Vercel provides free hosting with automatic deployments from your GitHub repository.

---

## 🏗️ Architecture for Vercel

### ⚠️ **Important Limitations**
- **Serverless Environment**: Each request runs in an isolated function
- **Temporary File Storage**: Files in `/tmp` are deleted after each request
- **No Persistent Database**: SQLite files don't persist between requests
- **Function Timeout**: 60 seconds maximum execution time

### ✅ **Solutions Provided**
- Modified entry point (`vercel_app.py`) for serverless compatibility
- Temporary file handling for certificate generation
- Environment variable configuration for external services
- GitHub Actions for automated deployment

---

## 🚀 Step-by-Step Deployment

### **Step 1: Prepare Your GitHub Repository**

1. **Create a new GitHub repository**:
   ```bash
   # Create repo on GitHub, then clone it locally
   git clone https://github.com/yourusername/certificate-generator.git
   cd certificate-generator
   ```

2. **Copy your project files** to the repository:
   ```bash
   # Copy all files from your project directory
   # Make sure to include the new Vercel configuration files
   ```

3. **Commit and push**:
   ```bash
   git add .
   git commit -m "Initial commit - Certificate Generator for Vercel"
   git push origin main
   ```

### **Step 2: Set Up Vercel Account**

1. **Sign up for Vercel**:
   - Go to [vercel.com](https://vercel.com)
   - Sign up with your GitHub account
   - This automatically connects Vercel to your GitHub

2. **Install Vercel CLI** (optional, for local testing):
   ```bash
   npm install -g vercel
   vercel login
   ```

### **Step 3: Deploy to Vercel**

#### **Option A: Automatic Deployment (Recommended)**

1. **Import Project**:
   - Go to your Vercel dashboard
   - Click "New Project"
   - Import your GitHub repository
   - Vercel will automatically detect it as a Python project

2. **Configure Build Settings**:
   - **Framework Preset**: Other
   - **Root Directory**: `./` (default)
   - **Build Command**: Leave empty (Vercel handles Python automatically)
   - **Output Directory**: Leave empty
   - **Install Command**: `pip install -r requirements-vercel.txt`

3. **Set Environment Variables**:
   ```bash
   SECRET_KEY=your-super-secret-key-change-this
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your-email@gmail.com
   SMTP_PASSWORD=your-gmail-app-password
   # Optional: Twilio for WhatsApp
   TWILIO_ACCOUNT_SID=your-twilio-sid
   TWILIO_AUTH_TOKEN=your-twilio-token
   TWILIO_PHONE_NUMBER=+1234567890
   ```

4. **Deploy**:
   - Click "Deploy"
   - Vercel will build and deploy your app
   - You'll get a live URL like: `https://your-app.vercel.app`

#### **Option B: GitHub Actions Deployment**

1. **Set up GitHub Secrets**:
   - Go to your GitHub repository
   - Settings → Secrets and Variables → Actions
   - Add these secrets:
     ```
     VERCEL_TOKEN=your-vercel-token
     VERCEL_ORG_ID=your-org-id
     VERCEL_PROJECT_ID=your-project-id
     ```

2. **Get Vercel Credentials**:
   ```bash
   # Install Vercel CLI
   npm install -g vercel
   
   # Login and get credentials
   vercel login
   vercel link  # Link to your project
   
   # Get tokens from .vercel/project.json
   cat .vercel/project.json
   ```

3. **Push to trigger deployment**:
   ```bash
   git push origin main
   # GitHub Actions will automatically deploy to Vercel
   ```

---

## ⚙️ Configuration Files Created

| File | Purpose |
|------|---------|
| `vercel.json` | Vercel deployment configuration |
| `vercel_app.py` | Serverless-compatible Flask entry point |
| `requirements-vercel.txt` | Simplified dependencies for Vercel |
| `vercel_generator.py` | Modified certificate generator for serverless |
| `.vercelignore` | Files to exclude from deployment |
| `.github/workflows/deploy.yml` | GitHub Actions for automated deployment |

---

## 🔧 Environment Variables Setup

### **Required Variables**:
```bash
SECRET_KEY=generate-a-random-32-character-string
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-gmail-app-password
```

### **Optional Variables**:
```bash
# For WhatsApp integration
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_PHONE_NUMBER=+1234567890

# For external database (recommended for production)
DATABASE_URL=postgresql://user:password@host:port/database
```

### **How to Set Environment Variables in Vercel**:
1. Go to your Vercel project dashboard
2. Settings → Environment Variables
3. Add each variable with name and value
4. Select environments: Production, Preview, Development
5. Save changes

---

## 📊 Features & Limitations on Vercel

### ✅ **What Works**:
- Certificate generation (PDF + QR codes)
- Email sending via SMTP
- WhatsApp sending via Twilio
- Web interface with all forms
- Single and bulk certificate generation
- Certificate verification

### ⚠️ **Limitations**:
- **File Persistence**: Generated files don't persist between requests
- **Database**: SQLite data is temporary (use external database for production)
- **Execution Time**: 60-second timeout per request
- **File Size**: Limited by Vercel's function payload limits

### 🔧 **Recommended Solutions**:
1. **External Database**: Use PostgreSQL, MongoDB, or similar
2. **File Storage**: Use AWS S3, Cloudinary, or similar for persistent files
3. **Background Jobs**: Use Vercel Edge Functions or external services for long-running tasks

---

## 🔍 Testing Your Deployment

### **Local Testing**:
```bash
# Test with Vercel CLI
vercel dev

# Test the serverless function
curl http://localhost:3000/
```

### **Production Testing**:
1. **Visit your Vercel URL**: `https://your-app.vercel.app`
2. **Test certificate generation**: Try creating a single certificate
3. **Test email sending**: Use the bulk send feature
4. **Check logs**: View function logs in Vercel dashboard

---

## 🐛 Troubleshooting

### **Common Issues**:

#### **1. Build Fails**
```bash
# Check requirements-vercel.txt has correct dependencies
# Ensure vercel.json is properly formatted
```

#### **2. Function Timeout**
```bash
# Reduce batch size for bulk operations
# Optimize PDF generation process
# Consider external processing for large batches
```

#### **3. Database Issues**
```bash
# Set up external PostgreSQL database
# Update DATABASE_URL environment variable
```

#### **4. File Storage Issues**
```bash
# Files in /tmp are temporary
# Implement external storage (S3, Cloudinary)
# Or send files directly via email without saving
```

### **Debugging Steps**:
1. **Check Vercel Function logs** in dashboard
2. **Test locally** with `vercel dev`
3. **Verify environment variables** are set correctly
4. **Check build logs** for dependency issues

---

## 🚀 Production Optimization

### **For High Traffic**:
1. **External Database**: PostgreSQL on Railway, Supabase, or Neon
2. **File Storage**: AWS S3 or Cloudinary for certificates
3. **Caching**: Redis for session/temporary data
4. **CDN**: Vercel automatically provides CDN

### **Cost Considerations**:
- **Vercel Free Tier**: 100GB bandwidth, 6,000 function executions
- **Pro Plan**: $20/month for higher limits
- **External services**: Database and storage costs

---

## 📞 Support & Next Steps

### **If You Need Help**:
1. Check Vercel documentation: [vercel.com/docs](https://vercel.com/docs)
2. Review function logs in Vercel dashboard
3. Test locally with `vercel dev`
4. Check GitHub Actions logs for deployment issues

### **Recommended Next Steps**:
1. **Set up external database** for data persistence
2. **Configure custom domain** in Vercel settings
3. **Set up monitoring** and error tracking
4. **Implement file storage service** for certificate persistence

---

## 🎯 Deployment Checklist

- [ ] GitHub repository created and code pushed
- [ ] Vercel account connected to GitHub
- [ ] Environment variables configured in Vercel
- [ ] Gmail app password created for SMTP
- [ ] Project deployed and accessible via Vercel URL
- [ ] Certificate generation tested
- [ ] Email sending tested
- [ ] Custom domain configured (optional)
- [ ] External database set up (recommended)
- [ ] File storage service configured (recommended)

---

**🎉 Your Certificate Generation System is now live on Vercel!**

Access your app at: `https://your-project-name.vercel.app`