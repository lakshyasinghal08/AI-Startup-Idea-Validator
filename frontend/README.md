# AI-Startup-Idea-Validator - Frontend

Modern, component-driven client application built with **React 19**, **Vite**, **Tailwind CSS**, and **React Router DOM**.

---

## 📁 Project Structure

```
frontend/
├── public/                 # Static assets (favicons, manifest)
├── src/
│   ├── api/                # Axios instance & domain API clients
│   ├── assets/             # Brand logos and images
│   ├── components/
│   │   └── common/         # Atomic UI primitives (Header, Footer, Button, Card)
│   ├── context/            # React Context for global application state
│   ├── hooks/              # Custom reusable hooks (useIdeaValidation)
│   ├── layouts/            # Page shell layouts (MainLayout)
│   ├── pages/              # Routed views (Home, Validator, Reports, 404)
│   ├── styles/             # Tailwind CSS entry points
│   ├── utils/              # Helper utilities and industry constants
│   ├── App.jsx             # Top-level route tree
│   └── main.jsx            # React 19 entry point
├── index.html              # HTML shell
├── package.json            # NPM project manifest
├── vite.config.js          # Vite build and proxy configuration
├── tailwind.config.js      # Tailwind styling configuration
└── README.md
```

---

## 🚀 Getting Started

### 1. Install Dependencies
```bash
npm install
```

### 2. Start Development Server
```bash
npm run dev
```
The application will run on [http://localhost:5173](http://localhost:5173).

### 3. Production Build
```bash
npm run build
```
The optimized production bundle will be output to `frontend/dist/`.

---

## 🌐 Deployment (Vercel)

The frontend is ready for automated zero-configuration continuous deployment on **Vercel**:
- **Framework Preset**: Vite
- **Root Directory**: `frontend`
- **Build Command**: `npm run build`
- **Output Directory**: `dist`
- **Environment Variables**:
  - `VITE_API_BASE_URL`: URL of your deployed Render backend (e.g. `https://ai-startup-idea-validator.onrender.com/api/v1`)
