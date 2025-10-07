# 🚀 Deployment Guide - UPDATED FOR RENDER

This guide will help you deploy the Shiritori Method Game to various cloud platforms.

## � Recent Fixes Applied

✅ **FIXED: "gunicorn: command not found" error**
- Added `gunicorn==21.2.0` to `requirements.txt`
- Updated `render.yaml` and `Procfile` with correct start command

✅ **FIXED: Port binding issues**
- App now uses `PORT` environment variable (required by Render)
- Fallback to `FLASK_PORT` then `5000` for local development

✅ **FIXED: Environment variable handling**
- Added `python-dotenv` support for local development
- Proper production environment detection

## �📋 Pre-deployment Checklist

- [x] All code committed to Git repository
- [x] Dependencies listed in `requirements.txt` (including gunicorn)
- [x] Environment variables documented
- [x] README.md updated
- [x] Game tested locally
- [x] Health check endpoint available

## 🌐 Render Deployment (Recommended)

### Step 1: Prepare Repository
```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

### Step 2: Create Render Service
1. Go to [Render.com](https://render.com)
2. Create account or sign in
3. Click "New +" → "Web Service"
4. Connect your GitHub repository
5. Configure service settings:
   - **Name**: `shiritori-method-game`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
   - **Plan**: Free (or paid for better performance)

### Step 3: Set Environment Variables
In Render dashboard, add these environment variables:
```
GEMINI_API_KEY=your_actual_api_key_here
FLASK_ENV=production
FLASK_HOST=0.0.0.0
FLASK_PORT=10000
```

### Step 4: Deploy
- Click "Create Web Service"
- Wait for build and deployment (usually 2-5 minutes)
- Your game will be live at: `https://your-app-name.onrender.com`

## 🟢 Heroku Deployment

### Step 1: Install Heroku CLI
Download from [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)

### Step 2: Create Heroku App
```bash
heroku login
heroku create shiritori-method-game
```

### Step 3: Set Environment Variables
```bash
heroku config:set GEMINI_API_KEY=your_api_key_here
heroku config:set FLASK_ENV=production
```

### Step 4: Deploy
```bash
git push heroku main
```

## 🚄 Railway Deployment

### Step 1: Connect Repository
1. Go to [Railway.app](https://railway.app)
2. Sign in with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository

### Step 2: Configure Environment
Add environment variables in Railway dashboard:
```
GEMINI_API_KEY=your_api_key_here
FLASK_ENV=production
```

### Step 3: Deploy
Railway will automatically detect Python and deploy your app.

## ☁️ Google Cloud Platform

### Step 1: Install gcloud CLI
Follow [GCP CLI installation](https://cloud.google.com/sdk/docs/install)

### Step 2: Create app.yaml
```yaml
runtime: python39

env_variables:
  GEMINI_API_KEY: "your_api_key_here"
  FLASK_ENV: "production"

automatic_scaling:
  min_instances: 1
  max_instances: 10
```

### Step 3: Deploy
```bash
gcloud app deploy
```

## 🔧 Environment Variables Reference

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `GEMINI_API_KEY` | Optional | Google Gemini API key for AI features | `AIzaSy...` |
| `FLASK_ENV` | No | Flask environment mode | `production` |
| `FLASK_HOST` | No | Host to bind the server | `0.0.0.0` |
| `FLASK_PORT` | No | Port to run the server | `5000` |

## 🎯 Getting Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated key
5. Add it to your deployment environment variables

**Note**: The game works without the API key but with limited AI features.

## 🐛 Common Deployment Issues

### Build Failures
- **Issue**: Dependencies not installing
- **Solution**: Check `requirements.txt` format and Python version compatibility

### Runtime Errors
- **Issue**: App crashes on startup
- **Solution**: Check logs for missing environment variables or import errors

### AI Features Not Working
- **Issue**: Gemini API not responding
- **Solution**: Verify API key is correctly set and has proper permissions

### Port Binding Issues
- **Issue**: App not accessible on deployed URL
- **Solution**: Ensure app binds to `0.0.0.0` and uses environment port

## 📊 Monitoring Your Deployment

### Render
- View logs in Render dashboard
- Monitor performance metrics
- Set up custom domains

### Heroku
```bash
heroku logs --tail
heroku ps:scale web=1
```

### Health Check
All platforms can use: `https://your-app-url.com/health`

## 🔒 Security Best Practices

1. **Never commit API keys** to version control
2. **Use environment variables** for all secrets
3. **Enable HTTPS** (usually automatic on cloud platforms)
4. **Monitor API usage** to prevent abuse
5. **Set up rate limiting** for production use

## 📈 Performance Optimization

### For Production
- Set `FLASK_ENV=production`
- Use a production WSGI server (consider Gunicorn)
- Enable caching for static files
- Monitor memory usage

### Scaling Options
- **Render**: Upgrade to paid plan for better performance
- **Heroku**: Scale dynos: `heroku ps:scale web=2`
- **Railway**: Automatic scaling available
- **GCP**: Configure auto-scaling in `app.yaml`

## 🎮 Post-Deployment Testing

1. **Basic Functionality**
   - [ ] Game loads without errors
   - [ ] Both game modes work
   - [ ] Scores save properly
   - [ ] Mobile responsiveness

2. **AI Features** (if API key provided)
   - [ ] Random topic generation
   - [ ] Word validation
   - [ ] AI word responses

3. **Performance**
   - [ ] Fast loading times
   - [ ] Smooth animations
   - [ ] No memory leaks

## 🆘 Support

If you encounter issues during deployment:

1. Check the platform-specific documentation
2. Review application logs
3. Verify environment variables
4. Test locally first
5. Create an issue in the repository

## 🎉 Success!

Once deployed, your Shiritori Method Game will be accessible worldwide. Share the URL with friends and enjoy playing!

---

**Happy Gaming! 🎮✨**