# SlideX - Frontend (JSX Version)

React + Vite frontend application for the SlideX with plain JavaScript (JSX).

## 🚀 Quick Start

### Prerequisites

- Node.js 18.x or higher
- npm or yarn

### Installation

```bash
cd FE_jsx
npm install
```

### Development Server

```bash
npm run dev
```

The application will be available at `http://localhost:3000`

### Build for Production

```bash
npm run build
```

The production-ready files will be in the `dist/` directory.

## 📁 Project Structure

```
FE_jsx/
├── src/
│   ├── components/
│   │   ├── Layout.jsx          # Main layout with navigation
│   │   └── SlidePreview.jsx    # Slide display component
│   ├── pages/
│   │   ├── Home.jsx            # Landing page
│   │   ├── Generate.jsx        # Presentation generation form
│   │   ├── Editor.jsx          # Presentation editor
│   │   └── History.jsx         # View generation history
│   ├── api.js                  # API service layer
│   ├── App.jsx                 # Main app component
│   ├── main.jsx                # Entry point
│   └── index.css               # Global styles
├── public/                     # Static assets
├── index.html                  # HTML template
├── vite.config.js              # Vite configuration
├── tailwind.config.js          # Tailwind CSS configuration
└── package.json                # Dependencies
```

## 🛠️ Technologies

- **React 18.2** - UI library
- **Vite 5.0** - Build tool (compatible with Node 18+)
- **React Router 6** - Client-side routing
- **Axios** - HTTP client
- **Tailwind CSS 3.3** - Utility-first CSS framework

## 🎨 Features

### Pages

1. **Home** (`/`)

   - Landing page with feature showcase
   - "How it works" section
   - Call-to-action buttons

2. **Generate** (`/generate`)

   - Topic input
   - Slide count slider (3-15 slides)
   - Theme selection (7 themes)
   - AI provider selection (Claude/Groq)
   - Brand color customization
   - File upload (PDF/DOCX)
   - Additional context textarea

3. **Editor** (`/editor/:pptId`)

   - Live slide preview
   - Inline editing for titles and bullets
   - Image replacement with suggestions
   - Pixabay image search
   - Download PPTX button
   - Speaker notes display

4. **History** (`/history`)
   - View past generations
   - Quick access to edit presentations
   - Delete presentations

### Components

#### Layout

- Navigation bar with active route highlighting
- Responsive design
- Footer with branding

#### SlidePreview

- Editable slide titles
- Editable bullet points
- Image display with replacement options
- Suggested images grid
- Speaker notes section

## 🔌 API Integration

All API calls are centralized in `src/api.js`:

```javascript
import { generatePPT, getPPTMetadata, downloadPPT } from "./api";

// Generate new presentation
const result = await generatePPT({
  topic: "AI in Healthcare",
  num_slides: 7,
  theme: "modern",
  ai_provider: "claude",
});

// Get presentation data
const presentation = await getPPTMetadata(pptId);

// Download PPTX file
const blob = await downloadPPT(pptId);
```

Available API functions:

- `generatePPT(data)` - Generate new presentation
- `getPPTMetadata(pptId)` - Get presentation metadata
- `downloadPPT(pptId)` - Download PPTX file
- `deletePPT(pptId)` - Delete presentation
- `updateSlide(pptId, slideIndex, slideData)` - Update slide content
- `replaceImage(data)` - Replace slide image
- `searchPixabayImages(query, page, perPage)` - Search Pixabay
- `uploadSource(file)` - Upload PDF/DOCX
- `checkRobots(url)` - Check robots.txt

## ⚙️ Configuration

### Vite Configuration

The Vite config includes a proxy to the backend API:

```javascript
// vite.config.js
export default defineConfig({
  server: {
    port: 3000,
    proxy: {
      "/api": {
        target: "http://localhost:5000",
        changeOrigin: true,
      },
    },
  },
});
```

### Tailwind Configuration

Tailwind is configured to scan all JSX files:

```javascript
// tailwind.config.js
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  // ...
};
```

## 🎨 Styling

This project uses Tailwind CSS for styling:

- **Utility-first approach** - Compose styles directly in JSX
- **Responsive design** - Mobile-first with `md:` and `lg:` breakpoints
- **Custom colors** - Blue theme with gray neutrals
- **Dark mode ready** - CSS variables for easy theme switching

Common classes:

```jsx
<button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
  Click me
</button>
```

## 🔧 Development Tips

### Adding a New Page

1. Create component in `src/pages/NewPage.jsx`:

```jsx
export default function NewPage() {
  return <div>New Page Content</div>;
}
```

2. Add route in `src/App.jsx`:

```jsx
<Route path="newpage" element={<NewPage />} />
```

3. Add navigation link in `src/components/Layout.jsx`

### Making API Calls

Use the centralized API functions:

```jsx
import { generatePPT } from "../api";

const handleGenerate = async () => {
  try {
    const result = await generatePPT(formData);
    // Handle success
  } catch (error) {
    // Handle error
    console.error(error.response?.data?.error);
  }
};
```

### State Management

This project uses React's built-in `useState` and `useEffect`:

```jsx
const [data, setData] = useState(null);
const [loading, setLoading] = useState(true);

useEffect(() => {
  loadData();
}, []);
```

## 🐛 Troubleshooting

### Port Already in Use

Change the port in `vite.config.js`:

```javascript
server: {
  port: 3001, // Change to different port
}
```

### CORS Errors

Ensure the backend is running on port 5000 and CORS is enabled in `BE/app.py`.

### Module Not Found

Install missing dependencies:

```bash
npm install
```

### Build Errors

Clear cache and reinstall:

```bash
rm -rf node_modules
rm package-lock.json
npm install
```

## 📦 Dependencies

### Production Dependencies

```json
{
  "react": "^18.2.0",
  "react-dom": "^18.2.0",
  "react-router-dom": "^6.20.0",
  "axios": "^1.6.2"
}
```

### Development Dependencies

```json
{
  "@vitejs/plugin-react": "^4.2.1",
  "vite": "^5.0.8",
  "autoprefixer": "^10.4.16",
  "postcss": "^8.4.32",
  "tailwindcss": "^3.3.6"
}
```

## 🚀 Deployment

### Build

```bash
npm run build
```

### Preview Production Build

```bash
npm run preview
```

### Deploy to Static Hosting

The `dist/` folder can be deployed to:

- Vercel
- Netlify
- GitHub Pages
- AWS S3 + CloudFront
- Any static hosting service

### Environment Variables

For production, update API proxy in `vite.config.js` or use environment variables:

```javascript
const apiUrl = import.meta.env.VITE_API_URL || "http://localhost:5000";
```

Create `.env.production`:

```
VITE_API_URL=https://your-backend-api.com
```

## 📝 Notes

- **No TypeScript** - This version uses plain JavaScript with JSX
- **Vite 5.0** - Compatible with Node.js 18.x and above
- **React 18.2** - Stable release with concurrent features
- **Tailwind CSS** - All styling done with utility classes
- **Axios** - For HTTP requests with automatic JSON parsing
- **React Router** - Client-side routing with nested layouts

## 🔗 Related Documentation

- [React Documentation](https://react.dev/)
- [Vite Documentation](https://vitejs.dev/)
- [Tailwind CSS](https://tailwindcss.com/)
- [React Router](https://reactrouter.com/)
- [Axios](https://axios-http.com/)

## ✨ Next Steps

1. Install dependencies: `npm install`
2. Start dev server: `npm run dev`
3. Ensure backend is running on port 5000
4. Visit `http://localhost:3000`
5. Generate your first presentation!

---

**Happy coding! 🚀**
