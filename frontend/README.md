# AI-Startup-Idea-Validator - Frontend

Minimal, professional, component-driven client application built with **React 19**, **Vite**, **Tailwind CSS**, and **React Router DOM**.

---

## 📁 Project Structure

```
frontend/
├── public/                 # Static assets (favicons, manifest)
├── src/
│   ├── api/                # Axios instance & domain API clients (client.js, ideaApi.js)
│   ├── assets/             # Brand logos
│   ├── components/
│   │   └── common/         # Atomic UI primitives (Header, Footer, Button, Card)
│   ├── context/            # Lightweight application state
│   ├── hooks/              # Custom reusable hooks (useIdeaValidation)
│   ├── layouts/            # Page shell layouts (MainLayout)
│   ├── pages/              # Routed views (HomePage, ValidatorPage, AboutPage, NotFoundPage)
│   ├── styles/             # Tailwind CSS entry points
│   ├── utils/              # Helper utilities and industry constants
│   ├── App.jsx             # Top-level declarative route tree
│   └── main.jsx            # React 19 entry point
├── index.html              # HTML shell
├── package.json            # NPM project manifest
├── vite.config.js          # Vite build and proxy configuration
├── tailwind.config.js      # Tailwind styling configuration
└── README.md
```

---

## 🎨 Design Philosophy
- **Clean & Minimalist:** Inspired by Notion, GitHub, and ChatGPT. White background, light gray sections, blue accent, clean typography, rounded cards.
- **Zero Distractions:** No glassmorphism, 3D cards, moving backgrounds, particles, or complex loaders.
- **Consulting-Grade Output:** Generates structured strategic briefs modeled after top-tier advisory firms (McKinsey, BCG, Deloitte).

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
