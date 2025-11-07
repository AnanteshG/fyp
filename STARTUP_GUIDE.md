# Project Startup Guide

## Prerequisites

- Python 3.9+ installed
- Node.js 16+ installed
- Firebase credentials configured (service-key.json in BE folder)

## Step 1: Start the Backend Server

**Terminal 1 (Backend):**

```powershell
cd c:\Users\Lenovo\Desktop\fyp\BE
python app.py
```

Expected output:

```
[timestamp] INFO: Logging configured
[timestamp] INFO: Starting server on port 5000
[timestamp] WARNING: * Debugger is active!
[timestamp] INFO: * Debugger PIN: xxx-xxx-xxx
```

The backend should be running on `http://localhost:5000`

---

## Step 2: Start the Frontend Development Server

**Terminal 2 (Frontend):**

```powershell
cd c:\Users\Lenovo\Desktop\fyp\FE_jsx
npm run dev
```

Expected output:

```
VITE v5.x.x  ready in xxx ms

➜  Local:   http://localhost:3000/
➜  press h + enter to show help
```

The frontend will be available at `http://localhost:3000`

---

## Architecture

```
Frontend (Vite + React)     Backend (Flask)
Port: 3000                   Port: 5000
     |
     |-- /api/v1/* -------> (Proxied via Vite)
     |
  axios requests with auth headers
```

### Proxy Configuration

- Frontend URL: `http://localhost:3000`
- Backend URL: `http://localhost:5000`
- Vite proxies `/api` requests to backend
- All API calls go through `apiClient` with automatic auth token injection

---

## Troubleshooting

### Error: `read ECONNRESET` on Frontend

**Cause:** Backend server is not running
**Solution:** Start backend server in Terminal 1 (see Step 1)

### Error: `Module not found: firebase`

**Cause:** Frontend dependencies not installed
**Solution:**

```powershell
cd c:\Users\Lenovo\Desktop\fyp\FE_jsx
npm install
```

### Error: `ModuleNotFoundError: No module named 'firebase_admin'`

**Cause:** Backend dependencies not installed
**Solution:**

```powershell
cd c:\Users\Lenovo\Desktop\fyp\BE
pip install -r requirements.txt
```

### Error: `invalid_grant: Bad Request` (Firebase)

**Cause:** Service account credentials expired or invalid
**Solution:** Regenerate service-key.json from Firebase Console:

1. Go to Firebase Console > Project Settings
2. Service Accounts tab > Generate New Private Key
3. Save as `BE/service-key.json`

---

## API Endpoints

All endpoints require authentication (Bearer token) except where noted.

### Generation Endpoints

- `POST /api/v1/generate` - Generate new presentation
- `GET /api/v1/ppt/{pptId}` - Get presentation metadata
- `PATCH /api/v1/ppt/{pptId}/slide/{index}` - Update slide
- `POST /api/v1/replace-image` - Replace image on slide

### History & User

- `GET /api/v1/history` - Get user's presentation history
- `GET /api/v1/user/info` - Get current user info

### Utilities

- `GET /api/v1/pixabay/search` - Search Pixabay images
- `GET /api/v1/robots-check` - Check robots.txt compliance
- `POST /api/v1/upload-source` - Upload source document

---

## Environment Variables

### Backend (.env)

```
GROQ_API_KEY=your_groq_key
PIXABAY_API_KEY=your_pixabay_key
FLASK_ENV=development
CORS_ORIGINS=*
```

### Firebase (service-key.json)

Located in `BE/service-key.json` - contains:

- Project ID: `fy-project-518d9`
- Storage Bucket: `fy-project-518d9.appspot.com`
- Service Account Email

### Frontend (src/firebase/config.js)

```javascript
const firebaseConfig = {
  apiKey: "YOUR_API_KEY",
  authDomain: "fy-project-518d9.firebaseapp.com",
  projectId: "fy-project-518d9",
  storageBucket: "fy-project-518d9.appspot.com",
  messagingSenderId: "YOUR_SENDER_ID",
  appId: "YOUR_APP_ID",
};
```

Get these values from Firebase Console > Project Settings > Your Apps

---

## Common Workflows

### Creating a New Presentation

1. Click "Generate" on homepage
2. Enter topic and configure options
3. Click "Generate Presentation"
4. Wait for AI to generate content (30-60 seconds)
5. View/edit in Editor

### Editing a Presentation

1. Go to "History" page
2. Click "Edit" on a presentation
3. Click slide title or bullets to edit
4. Click "🔄 Change" to replace images
5. Click "Download" to export as PPTX

### Viewing History

1. Click "History" in navigation
2. View all your presentations with thumbnails
3. Click "Edit" to modify or "Delete" to remove

---

## Development Notes

- Hot reload enabled on both frontend and backend
- Firebase Firestore stores all presentation data
- Firebase Storage hosts images with public URLs
- Client-side PPT generation using PptxGenJS
- Authentication via Firebase Auth (email/password & Google Sign-In)

---

## Need Help?

Check these files for implementation details:

- Backend: `BE/api/generate.py`, `BE/services/firebase_service.py`
- Frontend: `FE_jsx/src/pages/Generate.jsx`, `FE_jsx/src/contexts/AuthContext.jsx`
- Documentation: `FIREBASE_IMPLEMENTATION_README.md`
