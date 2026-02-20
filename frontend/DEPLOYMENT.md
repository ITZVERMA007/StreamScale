# StreamScale Frontend - Deployment Guide

## 🚀 Quick Start

### Development Mode

```bash
# Install dependencies
npm install

# Create .env file
echo "VITE_API_BASE_URL=http://localhost:8000" > .env

# Start development server
npm run dev
```

Visit `http://localhost:3000`

### Production Build

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

## 🐳 Docker Deployment

### Build Docker Image

```bash
docker build -t streamscale-frontend:latest .
```

### Run Container

```bash
docker run -d \
  -p 3000:80 \
  --name streamscale-frontend \
  streamscale-frontend:latest
```

### Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f frontend

# Stop services
docker-compose down
```

## ☁️ Cloud Deployment

### Vercel

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Deploy:
```bash
vercel
```

3. Set environment variables in Vercel dashboard:
   - `VITE_API_BASE_URL` → Your backend API URL

### Netlify

1. Install Netlify CLI:
```bash
npm i -g netlify-cli
```

2. Build and deploy:
```bash
npm run build
netlify deploy --prod --dir=dist
```

3. Configure environment variables in Netlify dashboard

### AWS S3 + CloudFront

1. Build the application:
```bash
npm run build
```

2. Upload to S3:
```bash
aws s3 sync dist/ s3://your-bucket-name --delete
```

3. Invalidate CloudFront cache:
```bash
aws cloudfront create-invalidation \
  --distribution-id YOUR_DIST_ID \
  --paths "/*"
```

### Google Cloud Platform

1. Build the application:
```bash
npm run build
```

2. Deploy to Cloud Run:
```bash
gcloud run deploy streamscale-frontend \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```bash
# Backend API URL
VITE_API_BASE_URL=http://localhost:8000

# For production, use your actual backend URL
# VITE_API_BASE_URL=https://api.streamscale.com
```

### Backend CORS Configuration

Ensure your FastAPI backend allows requests from your frontend domain:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://your-frontend-domain.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 📊 Monitoring & Analytics

### Add Google Analytics

Edit `index.html`:

```html
<head>
  <!-- ... existing tags ... -->
  
  <!-- Google Analytics -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', 'GA_MEASUREMENT_ID');
  </script>
</head>
```

### Add Sentry Error Tracking

```bash
npm install @sentry/react
```

Update `src/main.tsx`:

```typescript
import * as Sentry from "@sentry/react";

Sentry.init({
  dsn: "YOUR_SENTRY_DSN",
  environment: import.meta.env.MODE,
  tracesSampleRate: 1.0,
});
```

## 🔐 Security Best Practices

### 1. Content Security Policy

Add to `nginx.conf`:

```nginx
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:;" always;
```

### 2. Rate Limiting

Add rate limiting to nginx:

```nginx
limit_req_zone $binary_remote_addr zone=upload_limit:10m rate=10r/m;

location /api/upload {
    limit_req zone=upload_limit burst=5;
    # ... rest of config
}
```

### 3. HTTPS Only

Force HTTPS in production:

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    # ... rest of config
}
```

## 🎯 Performance Optimization

### 1. Enable Brotli Compression

```nginx
brotli on;
brotli_types text/plain text/css application/json application/javascript text/xml application/xml;
```

### 2. Optimize Images

Use WebP format and lazy loading:

```typescript
<img 
  loading="lazy" 
  src="image.webp" 
  alt="Description"
/>
```

### 3. Code Splitting

```typescript
import { lazy, Suspense } from 'react';

const UploadPage = lazy(() => import('./pages/UploadPage'));
const StatusPage = lazy(() => import('./pages/StatusPage'));
const ResultsPage = lazy(() => import('./pages/ResultsPage'));

// Wrap with Suspense
<Suspense fallback={<LoadingSpinner />}>
  <UploadPage />
</Suspense>
```

## 🧪 Testing

### Unit Tests (Optional Setup)

```bash
npm install -D vitest @testing-library/react @testing-library/jest-dom
```

### E2E Tests (Optional Setup)

```bash
npm install -D playwright @playwright/test
```

## 📈 Scaling

### CDN Integration

Use a CDN for static assets:

1. Build with public path:
```javascript
// vite.config.ts
export default defineConfig({
  base: 'https://cdn.yourdomain.com/',
});
```

2. Upload `dist/assets/` to your CDN

### Load Balancing

Use nginx upstream for multiple backend instances:

```nginx
upstream backend {
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}

location /api {
    proxy_pass http://backend;
}
```

## 🐛 Troubleshooting

### Build Fails

```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

### CORS Issues

- Verify backend CORS configuration
- Check browser console for specific errors
- Ensure API URL is correct in `.env`

### Upload Timeout

Increase nginx timeout:

```nginx
proxy_connect_timeout 300s;
proxy_send_timeout 300s;
proxy_read_timeout 300s;
```

### Memory Issues

Increase Node memory for builds:

```bash
NODE_OPTIONS="--max-old-space-size=4096" npm run build
```

## 📞 Support

For issues:
1. Check logs: `docker-compose logs -f frontend`
2. Review browser console
3. Check network tab in DevTools
4. Verify backend connectivity

---
