# =� Vercel MCP Configuration & Deployment Guide
**Template for Claude Code Agent - Complete Deployment Strategy**

## LLM PROMPT FOR VERCEL DEPLOYMENT

```
# COMPREHENSIVE VERCEL DEPLOYMENT PROMPT

You are tasked with configuring Vercel MCP integration and deploying a web application to the jpantsjoha Vercel account. Follow this complete deployment strategy:

## 1. PROJECT SETUP & CONFIGURATION

### A. Initial Project Structure
Create the following essential files in your project root:

**vercel.json** (SPA Configuration):
```json
{
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ],
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        },
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        },
        {
          "key": "Referrer-Policy",
          "value": "origin-when-cross-origin"
        }
      ]
    }
  ]
}
```

**package.json** (Required Scripts):
```json
{
  "name": "your-project-name",
  "version": "1.0.0",
  "scripts": {
    "dev": "vite --port 5173 --host",
    "build": "vite build",
    "preview": "vite preview --port 5173",
    "lint": "eslint .",
    "test": "vitest",
    "deploy": "npm run build && vercel --prod"
  },
  "dependencies": {
    "@vercel/speed-insights": "^1.2.0"
  }
}
```

### B. Environment Variables Setup
Create `.env.local` for development:
```env
# Development Environment
VITE_APP_ENV=development
VITE_API_BASE_URL=http://localhost:5173

# Add your specific environment variables here
```

Create `.env.production` for production (will be added to Vercel):
```env
# Production Environment  
VITE_APP_ENV=production
VITE_API_BASE_URL=https://your-app.vercel.app

# Add your production environment variables here
```

## 2. VERCEL ACCOUNT CONFIGURATION

### A. Account Details
- **Account**: jpantsjoha 
- **Email**: Use the GitHub-linked email
- **GitHub Integration**: Should be connected to jpantsjoha GitHub account

### B. Project Import Process
1. **Connect GitHub Repository**:
   - Go to https://vercel.com/dashboard
   - Click "Add New" � "Project"
   - Select GitHub repository from jpantsjoha account
   - Configure project settings

2. **Build Configuration**:
   ```
   Framework Preset: Vite
   Build Command: npm run build
   Output Directory: dist
   Install Command: npm install
   Development Command: npm run dev
   ```

3. **Environment Variables** (Add in Vercel Dashboard):
   ```
   VITE_APP_ENV=production
   VITE_API_BASE_URL=https://your-app.vercel.app
   [Add your specific variables]
   ```

## 3. DEPLOYMENT AUTOMATION

### A. GitHub Integration Setup
Ensure these files exist for automatic deployment:

**.github/workflows/vercel.yml** (Optional - Vercel auto-deploys):
```yaml
name: Deploy to Vercel
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
        with:
          node-version: '18'
      - run: npm ci
      - run: npm run build
      # Vercel handles deployment automatically
```

### B. Deployment Commands
```bash
# Install Vercel CLI globally
npm install -g vercel

# Login to jpantsjoha account
vercel login

# Link project to Vercel (first time only)
vercel link

# Deploy to preview
vercel

# Deploy to production
vercel --prod

# Check deployment status
vercel ls

# View logs
vercel logs [deployment-url]
```

## 4. PERFORMANCE & MONITORING SETUP

### A. Speed Insights Integration
Add to your main React component or index.html:
```javascript
import { SpeedInsights } from '@vercel/speed-insights/react'

function App() {
  return (
    <>
      {/* Your app content */}
      <SpeedInsights />
    </>
  )
}
```

### B. Analytics Configuration
```javascript
import { Analytics } from '@vercel/analytics/react'

function App() {
  return (
    <>
      {/* Your app content */}
      <Analytics />
    </>
  )
}
```

## 5. TESTING & VALIDATION

### A. Pre-Deployment Testing
```bash
# Test build locally
npm run build
npm run preview

# Verify build output
ls -la dist/

# Test deployment (preview)
vercel

# Test production deployment
vercel --prod
```

### B. Post-Deployment Validation
```bash
# Check deployment status
curl -I https://your-app.vercel.app

# Verify environment variables are working
# Test all major functionality
# Verify analytics are collecting data
```

## 6. DOMAIN CONFIGURATION (IF NEEDED)

### A. Custom Domain Setup
1. **In Vercel Dashboard**:
   - Go to Project Settings � Domains
   - Add custom domain
   - Follow DNS configuration instructions

2. **DNS Configuration**:
   ```
   Type: CNAME
   Name: www (or @)
   Value: your-app.vercel.app
   ```

### B. SSL Certificate
- Automatically provisioned by Vercel
- Supports automatic renewal
- Covers all domain variants

## 7. TROUBLESHOOTING COMMON ISSUES

### A. Build Failures
```bash
# Check build logs
vercel logs --build

# Common fixes:
# - Update Node.js version in package.json engines
# - Fix ESLint errors
# - Update dependencies
# - Check environment variables
```

### B. Runtime Errors
```bash
# Check runtime logs
vercel logs

# Common fixes:
# - Verify API endpoints are accessible
# - Check CORS configuration
# - Validate environment variables
# - Test database connections
```

### C. Performance Issues
```bash
# Analyze bundle size
npm run build
npx webpack-bundle-analyzer dist/

# Check Core Web Vitals in Vercel dashboard
# Optimize images and assets
# Enable compression and caching
```

## 8. ONGOING MAINTENANCE

### A. Regular Updates
```bash
# Update dependencies monthly
npm update

# Check for security vulnerabilities
npm audit
npm audit fix

# Monitor Vercel dashboard for:
# - Deployment failures
# - Performance metrics
# - Usage limits
```

### B. Monitoring Commands
```bash
# Check deployment status
vercel ls

# Monitor real-time logs
vercel logs --follow

# Check function performance
vercel inspect [deployment-url]
```

## 9. SPECIFIC JPANTSJOHA ACCOUNT SETTINGS

### A. Account Limits (Hobby Plan)
- **Bandwidth**: 100GB/month
- **Serverless Functions**: 100GB-hours
- **Build Minutes**: Unlimited
- **Deployments**: Unlimited

### B. Upgrade Triggers
Monitor these metrics and upgrade to Pro when:
- Bandwidth usage > 80GB/month
- Need custom domains
- Require team collaboration
- Need advanced analytics

### C. Security Configuration
```bash
# Enable deployment protection for production
# Add team members with appropriate permissions
# Configure webhook notifications for deployments
# Set up environment variable access controls
```

## 10. SUCCESS CRITERIA

### A. Deployment Success Indicators
- [ ] Application loads at https://your-app.vercel.app
- [ ] All environment variables are working
- [ ] Build completes without errors
- [ ] Analytics are collecting data
- [ ] Performance metrics are good (Lighthouse > 90)

### B. Ongoing Health Metrics
- [ ] Uptime > 99.9%
- [ ] Build time < 2 minutes
- [ ] Page load time < 3 seconds
- [ ] Error rate < 1%

## 11. EMERGENCY PROCEDURES

### A. Rollback Process
```bash
# Rollback to previous deployment
vercel rollback [previous-deployment-url]

# Or via dashboard:
# 1. Go to Deployments tab
# 2. Find previous working deployment
# 3. Click "Promote to Production"
```

### B. Emergency Contacts
- **Vercel Support**: support@vercel.com
- **GitHub Issues**: For code-related problems
- **Account Issues**: Use Vercel dashboard help chat

## END OF PROMPT

Use this comprehensive guide to deploy any web application to the jpantsjoha Vercel account. Adapt environment variables and project-specific settings as needed.
```

## ACCOUNT-SPECIFIC CONFIGURATION

### Vercel Account Details (jpantsjoha)
- **Account Type**: Hobby (can upgrade to Pro)
- **GitHub Integration**:  Connected
- **Domain Management**: Available
- **Team Settings**: Individual account

### Current Projects on Account
Based on Mintin Studio setup, the following patterns work well:
- **Framework**: React 18 + Vite + TypeScript
- **Build Command**: `npm run build`
- **Output Directory**: `dist`
- **Environment Variables**: Use VITE_ prefix for client-side vars

### Recommended Environment Variables Structure
```env
# Core Application
VITE_APP_NAME=YourAppName
VITE_APP_VERSION=1.0.0
VITE_APP_ENV=production

# API Configuration  
VITE_API_BASE_URL=https://your-app.vercel.app
VITE_API_VERSION=v1

# Third-party Services
VITE_ANALYTICS_ID=your-analytics-id
VITE_SENTRY_DSN=your-sentry-dsn

# Feature Flags
VITE_ENABLE_ANALYTICS=true
VITE_ENABLE_MONITORING=true
```

### Quick Deploy Commands
```bash
# One-time setup
npm install -g vercel
vercel login
vercel link

# Regular deployment
npm run build && vercel --prod

# Emergency rollback
vercel rollback [previous-url]

# Monitor deployment
vercel logs --follow
```

### Performance Optimization Checklist
- [ ] **Bundle Size**: Keep under 3MB total
- [ ] **Code Splitting**: Implement route-based splitting
- [ ] **Image Optimization**: Use Vercel Image Optimization
- [ ] **Caching**: Configure appropriate cache headers
- [ ] **CDN**: Leverage Vercel's global CDN
- [ ] **Compression**: Enable gzip/brotli compression

### Security Best Practices
```json
{
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {"key": "X-Frame-Options", "value": "DENY"},
        {"key": "X-Content-Type-Options", "value": "nosniff"},
        {"key": "Referrer-Policy", "value": "origin-when-cross-origin"},
        {"key": "Permissions-Policy", "value": "camera=(), microphone=(), geolocation=()"}
      ]
    }
  ]
}
```

### Cost Management
- **Monitor Usage**: Check Vercel dashboard weekly
- **Optimize Assets**: Compress images and minimize JS/CSS
- **Function Limits**: Keep serverless functions under 10s execution
- **Bandwidth Alerts**: Set up notifications at 80GB usage

### Integration with Development Workflow
```bash
# Development
npm run dev          # Local development server

# Testing  
npm run build        # Test production build
npm run preview      # Preview build locally

# Deployment
vercel               # Deploy to preview
vercel --prod        # Deploy to production

# Monitoring
vercel logs          # Check deployment logs
vercel inspect       # Analyze performance
```

---

## TEMPLATE USAGE INSTRUCTIONS

This document serves as a complete template for deploying any web application to the jpantsjoha Vercel account. When using this template:

1. **Copy the LLM prompt section** (everything between the code blocks)
2. **Customize environment variables** for your specific project
3. **Update project name and URLs** throughout the template  
4. **Add any project-specific build requirements**
5. **Configure domain settings** if using custom domains

The template is designed to be comprehensive yet adaptable for different types of web applications while maintaining the specific configuration patterns that work well with the jpantsjoha account setup.

---

**Created**: July 29, 2025  
**Last Updated**: July 29, 2025  
**Status**: Ready for Production Use  
**Version**: 1.0  
**Account**: jpantsjoha  
**Template Type**: Complete LLM Deployment Prompt