# StreamScale Frontend (React JSX)

A production-quality React frontend for the StreamScale distributed video transcoding system, built with **JavaScript (JSX)** instead of TypeScript.

## 🚀 Features

- **Modern Tech Stack**: React 18, JavaScript (JSX), Vite, TailwindCSS
- **Real-time Status Polling**: Automatic updates every 2.5 seconds using TanStack React Query
- **Drag & Drop Upload**: Intuitive file upload with validation
- **Progress Tracking**: Visual feedback for upload and transcoding progress
- **Multi-resolution Support**: Automatic transcoding to 360p, 720p, and 1080p
- **Responsive Design**: Works seamlessly on desktop and mobile
- **Error Handling**: Comprehensive error boundaries and network error handling
- **Toast Notifications**: User-friendly feedback for all actions
- **Loading States**: Skeleton screens and loading spinners
- **Dark Theme**: Beautiful dark mode interface with gradient accents

## 📋 Prerequisites

- Node.js 18+ 
- npm or yarn
- StreamScale backend running (FastAPI + Celery + Redis + MinIO)

## 🛠️ Installation

1. **Clone the repository** (or navigate to the frontend directory)

```bash
cd streamscale-frontend
```

2. **Install dependencies**

```bash
npm install
```

3. **Configure environment variables**

Create a `.env` file in the root directory:

```bash
VITE_API_BASE_URL=http://localhost:8000
```

4. **Start the development server**

```bash
npm run dev
```

The application will be available at `http://localhost:3000`

## 🏗️ Build for Production

```bash
npm run build
```

Build output will be in the `dist/` directory.

To preview the production build:

```bash
npm run preview
```

## 📁 Project Structure

```
streamscale-frontend/
├── src/
│   ├── components/          # Reusable UI components (JSX)
│   │   ├── ErrorBoundary.jsx
│   │   ├── Layout.jsx
│   │   ├── LoadingSpinner.jsx
│   │   ├── ProgressBar.jsx
│   │   ├── ResolutionCard.jsx
│   │   └── VideoDropzone.jsx
│   ├── pages/              # Page components (JSX)
│   │   ├── UploadPage.jsx
│   │   ├── StatusPage.jsx
│   │   └── ResultsPage.jsx
│   ├── hooks/              # Custom React hooks
│   │   └── useTaskStatus.js
│   ├── services/           # API services
│   │   └── api.js
│   ├── types/              # Constants and type definitions
│   │   └── index.js
│   ├── utils/              # Utility functions
│   │   └── helpers.js
│   ├── App.jsx             # Main app component
│   ├── main.jsx            # Entry point
│   └── index.css           # Global styles
├── public/                 # Static assets
├── index.html              # HTML template
├── package.json
├── vite.config.js
└── tailwind.config.js
```

## 🔌 API Integration

The frontend expects the following backend endpoints:

### Upload Video
```
POST /upload
Content-Type: multipart/form-data

Body: { file: File }

Response: { 
  task_id: string,
  message: string 
}
```

### Get Task Status
```
GET /status/{task_id}

Response: {
  task_id: string,
  state: 'PENDING' | 'STARTED' | 'PROGRESS' | 'SUCCESS' | 'FAILURE' | 'RETRY',
  progress?: number,
  stage?: string,
  message?: string,
  error?: string,
  result?: {
    original: string,
    transcoded: {
      '360p'?: string,
      '720p'?: string,
      '1080p'?: string
    }
  }
}
```

### Download Video
```
GET /download/{filename}

Response: Video file (binary)
```

### Cancel Task (Optional)
```
POST /cancel/{task_id}

Response: Success message
```

## 🎨 Customization

### Theme Colors

Edit `tailwind.config.js` to customize the color scheme:

```javascript
colors: {
  dark: {
    bg: '#0a0a0f',
    card: '#13131a',
    border: '#1f1f28',
    hover: '#1a1a23',
  },
  accent: {
    primary: '#6366f1',
    secondary: '#8b5cf6',
    success: '#10b981',
    warning: '#f59e0b',
    error: '#ef4444',
  }
}
```

### Polling Interval

Adjust the polling frequency in `src/hooks/useTaskStatus.js`:

```javascript
refetchInterval: (data) => {
  if (data?.state === 'SUCCESS' || data?.state === 'FAILURE') {
    return false;
  }
  return 2500; // Change this value (in milliseconds)
}
```

### File Upload Limits

Modify constraints in `src/types/index.js`:

```javascript
export const ALLOWED_FILE_TYPES = ['video/mp4', 'video/x-matroska', 'video/quicktime', 'video/webm'];
export const ALLOWED_EXTENSIONS = ['.mp4', '.mkv', '.mov', '.webm'];
export const MAX_FILE_SIZE = 2 * 1024 * 1024 * 1024; // 2GB
```

## 🧪 Error Handling

The application includes comprehensive error handling:

- **Error Boundaries**: Catch React component errors
- **Network Error Recovery**: Automatic retry with exponential backoff
- **Toast Notifications**: User-friendly error messages
- **Loading States**: Prevent user confusion during async operations
- **File Validation**: Client-side validation before upload

## 🔒 Security Considerations

This is an MVP without authentication. For production:

1. Add authentication (JWT, OAuth, etc.)
2. Implement rate limiting
3. Add CSRF protection
4. Validate file types server-side
5. Implement user quotas
6. Add request signing for downloads

## 📱 Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

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

## 🐛 Troubleshooting

### CORS Issues

If you encounter CORS errors, ensure your backend includes:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Upload Fails

- Check file size limits (default 2GB)
- Verify file type is supported
- Check backend logs for errors
- Ensure sufficient disk space

### Status Not Updating

- Verify backend is running
- Check network tab for failed requests
- Ensure task_id is valid
- Check Celery worker status

## 📄 License

This project is part of the StreamScale distributed video transcoding system.

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📞 Support

For issues or questions:
- Check existing GitHub issues
- Create a new issue with detailed information
- Include browser console logs and network requests

---

Built with ❤️ using React (JSX), Vite, and TailwindCSS
