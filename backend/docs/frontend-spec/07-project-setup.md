# Project Setup Guide

## Table of Contents
- [Prerequisites](#prerequisites)
- [Initial Project Setup](#initial-project-setup)
- [Project Structure](#project-structure)
- [Installing Dependencies](#installing-dependencies)
- [Configuration Files](#configuration-files)
- [Environment Variables](#environment-variables)
- [Setting Up Tailwind CSS](#setting-up-tailwind-css)
- [Setting Up Shadcn/ui](#setting-up-shadcnui)
- [Code Quality Tools](#code-quality-tools)
- [Git Setup](#git-setup)
- [Development Workflow](#development-workflow)
- [Deployment](#deployment)

---

## Prerequisites

### Required Software
- **Node.js**: v18.0.0 or higher
- **npm**: v9.0.0 or higher (comes with Node.js)
- **Git**: Latest version

### Verify Installation
```bash
node --version   # Should be v18+
npm --version    # Should be v9+
git --version
```

### Optional Tools
- **VS Code**: Recommended IDE
- **VS Code Extensions**:
  - ESLint
  - Prettier
  - Tailwind CSS IntelliSense
  - PostCSS Language Support
  - Error Lens

---

## Initial Project Setup

### Step 1: Create Vite Project
```bash
# Create new Vite project with React + TypeScript
npm create vite@latest frontend -- --template react-ts

# Navigate to project directory
cd frontend
```

### Step 2: Initialize Git (if not already done)
```bash
git init
git add .
git commit -m "Initial commit: Vite + React + TypeScript"
```

### Step 3: Install Base Dependencies
```bash
npm install
```

### Step 4: Test Development Server
```bash
npm run dev
```

Visit `http://localhost:5173` to verify the app runs.

---

## Project Structure

Create the following directory structure:

```bash
mkdir -p src/{components,pages,hooks,utils,stores,services,types,tests,assets}
mkdir -p src/components/{ui,layout,features}
mkdir -p src/components/features/{auth,quiz,study,achievements,leaderboard,profile,bookmarks,admin}
mkdir -p src/tests/{utils,mocks,integration}
mkdir -p public
```

### Full Structure
```
frontend/
├── public/
│   └── vite.svg
├── src/
│   ├── assets/              # Images, fonts, static files
│   ├── components/
│   │   ├── ui/             # Base UI components (Button, Input, etc.)
│   │   ├── layout/         # Layout components (AppShell, Sidebar, etc.)
│   │   └── features/       # Feature-specific components
│   │       ├── auth/
│   │       ├── quiz/
│   │       ├── study/
│   │       ├── achievements/
│   │       ├── leaderboard/
│   │       ├── profile/
│   │       ├── bookmarks/
│   │       └── admin/
│   ├── hooks/              # Custom React hooks
│   ├── pages/              # Page components
│   ├── services/           # API clients and external services
│   ├── stores/             # Zustand stores
│   ├── types/              # TypeScript types and interfaces
│   ├── utils/              # Utility functions
│   ├── tests/              # Test utilities and mocks
│   │   ├── utils/
│   │   ├── mocks/
│   │   └── integration/
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css
├── e2e/                    # Playwright E2E tests
├── .env.example
├── .env.local
├── .gitignore
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
├── postcss.config.js
├── eslint.config.js
└── README.md
```

---

## Installing Dependencies

### Core Dependencies
```bash
# Routing
npm install react-router-dom

# State Management
npm install zustand

# Server State & Data Fetching
npm install @tanstack/react-query axios

# Forms & Validation
npm install react-hook-form @hookform/resolvers zod

# UI & Styling
npm install tailwindcss postcss autoprefixer
npm install clsx tailwind-merge
npm install lucide-react

# Animations
npm install framer-motion

# Charts
npm install recharts

# Utilities
npm install date-fns
npm install react-confetti
```

### Development Dependencies
```bash
# TypeScript
npm install -D @types/node

# Testing
npm install -D vitest @vitest/ui jsdom
npm install -D @testing-library/react @testing-library/jest-dom @testing-library/user-event
npm install -D @axe-core/react jest-axe
npm install -D msw

# E2E Testing
npm install -D @playwright/test
npx playwright install

# Code Quality
npm install -D eslint @typescript-eslint/parser @typescript-eslint/eslint-plugin
npm install -D prettier eslint-config-prettier eslint-plugin-prettier
npm install -D eslint-plugin-react eslint-plugin-react-hooks
npm install -D husky lint-staged

# Build Tools
npm install -D vite-plugin-compression
```

---

## Configuration Files

### TypeScript Configuration (`tsconfig.json`)
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,

    /* Bundler mode */
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",

    /* Linting */
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,

    /* Path Aliases */
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

### TypeScript Node Configuration (`tsconfig.node.json`)
```json
{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true
  },
  "include": ["vite.config.ts"]
}
```

### Vite Configuration (`vite.config.ts`)
```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'
import viteCompression from 'vite-plugin-compression'

export default defineConfig({
  plugins: [
    react(),
    viteCompression({
      algorithm: 'gzip',
      ext: '.gz',
    }),
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          'query-vendor': ['@tanstack/react-query'],
          'ui-vendor': ['framer-motion', 'lucide-react'],
        },
      },
    },
  },
})
```

### Vitest Configuration (`vitest.config.ts`)
```typescript
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/tests/setup.ts',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'src/tests/',
        '**/*.d.ts',
        '**/*.config.*',
        '**/mockData/',
      ],
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})
```

---

## Environment Variables

### Create `.env.example`
```bash
# API Configuration
VITE_API_BASE_URL=http://localhost:8000
VITE_API_VERSION=v1

# Feature Flags
VITE_ENABLE_ANALYTICS=false
VITE_ENABLE_SENTRY=false

# Environment
VITE_ENV=development
```

### Create `.env.local` (Git ignored)
```bash
cp .env.example .env.local
```

Edit `.env.local` with your actual values.

### Update `.gitignore`
```bash
# Environment variables
.env.local
.env.*.local

# Testing
coverage/
playwright-report/
test-results/

# Build output
dist/
dist-ssr/

# Editor
.vscode/*
!.vscode/extensions.json
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
```

### Access Environment Variables in Code
```typescript
// src/config/env.ts
export const env = {
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  apiVersion: import.meta.env.VITE_API_VERSION || 'v1',
  enableAnalytics: import.meta.env.VITE_ENABLE_ANALYTICS === 'true',
  isDevelopment: import.meta.env.DEV,
  isProduction: import.meta.env.PROD,
}
```

---

## Setting Up Tailwind CSS

### Step 1: Initialize Tailwind
```bash
npx tailwindcss init -p
```

### Step 2: Configure Tailwind (`tailwind.config.js`)
```javascript
/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6', // Base primary
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
          950: '#172554',
        },
        success: {
          50: '#f0fdf4',
          100: '#dcfce7',
          200: '#bbf7d0',
          300: '#86efac',
          400: '#4ade80',
          500: '#22c55e', // Base success
          600: '#16a34a',
          700: '#15803d',
          800: '#166534',
          900: '#14532d',
        },
        error: {
          50: '#fef2f2',
          100: '#fee2e2',
          200: '#fecaca',
          300: '#fca5a5',
          400: '#f87171',
          500: '#ef4444', // Base error
          600: '#dc2626',
          700: '#b91c1c',
          800: '#991b1b',
          900: '#7f1d1d',
        },
        warning: {
          50: '#fffbeb',
          100: '#fef3c7',
          200: '#fde68a',
          300: '#fcd34d',
          400: '#fbbf24',
          500: '#f59e0b', // Base warning
          600: '#d97706',
          700: '#b45309',
          800: '#92400e',
          900: '#78350f',
        },
        accent: {
          purple: {
            500: '#a855f7', // XP
            600: '#9333ea',
          },
          orange: {
            500: '#f97316', // Streaks
            600: '#ea580c',
          },
          gold: {
            500: '#f59e0b', // Achievements
            600: '#d97706',
          },
        },
        neutral: {
          50: '#fafafa',
          100: '#f5f5f5',
          200: '#e5e5e5',
          300: '#d4d4d4',
          400: '#a3a3a3',
          500: '#737373',
          600: '#525252',
          700: '#404040',
          800: '#262626',
          900: '#171717',
          950: '#0a0a0a',
        },
      },
      fontFamily: {
        sans: [
          '-apple-system',
          'BlinkMacSystemFont',
          '"Segoe UI"',
          'Roboto',
          '"Helvetica Neue"',
          'Arial',
          'sans-serif',
        ],
        mono: [
          '"Fira Code"',
          '"SF Mono"',
          'Monaco',
          'Consolas',
          'monospace',
        ],
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
        '112': '28rem',
        '128': '32rem',
      },
      borderRadius: {
        '4xl': '2rem',
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-in',
        'slide-in': 'slideIn 0.3s ease-out',
        'bounce-in': 'bounceIn 0.5s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideIn: {
          '0%': { transform: 'translateY(-10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        bounceIn: {
          '0%': { transform: 'scale(0.3)', opacity: '0' },
          '50%': { transform: 'scale(1.05)' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
      },
    },
  },
  plugins: [],
}
```

### Step 3: Add Tailwind Directives (`src/index.css`)
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  * {
    @apply border-neutral-200;
  }

  body {
    @apply bg-neutral-50 text-neutral-900 antialiased;
  }

  h1 {
    @apply text-4xl font-bold;
  }

  h2 {
    @apply text-3xl font-semibold;
  }

  h3 {
    @apply text-2xl font-semibold;
  }

  h4 {
    @apply text-xl font-medium;
  }
}

@layer components {
  .btn {
    @apply px-4 py-2 rounded-lg font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2;
  }

  .btn-primary {
    @apply btn bg-primary-500 text-white hover:bg-primary-600 focus:ring-primary-500;
  }

  .btn-secondary {
    @apply btn bg-neutral-100 text-neutral-900 hover:bg-neutral-200 focus:ring-neutral-500;
  }

  .input {
    @apply w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent;
  }

  .card {
    @apply bg-white rounded-lg shadow-sm border border-neutral-200 p-6;
  }
}

@layer utilities {
  .text-balance {
    text-wrap: balance;
  }
}
```

---

## Setting Up Shadcn/ui

### Step 1: Install Shadcn CLI
```bash
npx shadcn-ui@latest init
```

**Configuration options:**
- TypeScript: Yes
- Style: Default
- Base color: Slate
- CSS variables: Yes
- React Server Components: No
- Location for components: src/components/ui
- Use "src" alias: Yes (@/components)
- Use React Server Components: No
- Tailwind config: tailwind.config.js

### Step 2: Add Components
```bash
# Add commonly used components
npx shadcn-ui@latest add button
npx shadcn-ui@latest add input
npx shadcn-ui@latest add card
npx shadcn-ui@latest add badge
npx shadcn-ui@latest add dialog
npx shadcn-ui@latest add dropdown-menu
npx shadcn-ui@latest add tabs
npx shadcn-ui@latest add toast
npx shadcn-ui@latest add progress
npx shadcn-ui@latest add select
npx shadcn-ui@latest add checkbox
npx shadcn-ui@latest add radio-group
npx shadcn-ui@latest add avatar
npx shadcn-ui@latest add separator
```

### Step 3: Create Utility for Class Merging (`src/lib/utils.ts`)
```typescript
import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
```

---

## Code Quality Tools

### ESLint Configuration (`eslint.config.js`)
```javascript
import js from '@eslint/js'
import globals from 'globals'
import reactHooks from 'eslint-plugin-react-hooks'
import reactRefresh from 'eslint-plugin-react-refresh'
import tseslint from 'typescript-eslint'

export default tseslint.config(
  { ignores: ['dist'] },
  {
    extends: [js.configs.recommended, ...tseslint.configs.recommended],
    files: ['**/*.{ts,tsx}'],
    languageOptions: {
      ecmaVersion: 2020,
      globals: globals.browser,
    },
    plugins: {
      'react-hooks': reactHooks,
      'react-refresh': reactRefresh,
    },
    rules: {
      ...reactHooks.configs.recommended.rules,
      'react-refresh/only-export-components': [
        'warn',
        { allowConstantExport: true },
      ],
      '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
    },
  }
)
```

### Prettier Configuration (`.prettierrc`)
```json
{
  "semi": false,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5",
  "printWidth": 100,
  "arrowParens": "always",
  "endOfLine": "lf"
}
```

### Prettier Ignore (`.prettierignore`)
```
dist
coverage
node_modules
*.md
```

### VS Code Settings (`.vscode/settings.json`)
```json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  },
  "typescript.tsdk": "node_modules/typescript/lib",
  "tailwindCSS.experimental.classRegex": [
    ["cn\\(([^)]*)\\)", "'([^']*)'"]
  ]
}
```

### Recommended Extensions (`.vscode/extensions.json`)
```json
{
  "recommendations": [
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode",
    "bradlc.vscode-tailwindcss",
    "usernamehw.errorlens",
    "csstools.postcss"
  ]
}
```

---

## Git Setup

### Initialize Husky
```bash
npx husky-init && npm install
```

### Configure Pre-commit Hook (`.husky/pre-commit`)
```bash
#!/usr/bin/env sh
. "$(dirname -- "$0")/_/husky.sh"

npx lint-staged
```

### Configure Lint-Staged (`package.json`)
```json
{
  "lint-staged": {
    "*.{ts,tsx}": [
      "eslint --fix",
      "prettier --write",
      "vitest related --run"
    ],
    "*.{json,css,md}": [
      "prettier --write"
    ]
  }
}
```

### Update Package Scripts (`package.json`)
```json
{
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
    "lint:fix": "eslint . --ext ts,tsx --fix",
    "format": "prettier --write \"src/**/*.{ts,tsx,css,json}\"",
    "format:check": "prettier --check \"src/**/*.{ts,tsx,css,json}\"",
    "test": "vitest",
    "test:ui": "vitest --ui",
    "test:coverage": "vitest run --coverage",
    "test:e2e": "playwright test",
    "test:e2e:ui": "playwright test --ui",
    "type-check": "tsc --noEmit",
    "prepare": "husky install"
  }
}
```

---

## Development Workflow

### Starting Development Server
```bash
npm run dev
```

Visit `http://localhost:5173`

### Running Tests
```bash
# Run tests in watch mode
npm test

# Run tests with coverage
npm run test:coverage

# Run E2E tests
npm run test:e2e

# Run E2E tests with UI
npm run test:e2e:ui
```

### Code Quality Checks
```bash
# Lint code
npm run lint

# Fix lint issues
npm run lint:fix

# Format code
npm run format

# Check formatting
npm run format:check

# Type check
npm run type-check
```

### Building for Production
```bash
# Build
npm run build

# Preview production build
npm run preview
```

### Recommended Development Flow
1. Create feature branch: `git checkout -b feature/quiz-system`
2. Make changes
3. Run tests: `npm test`
4. Lint and format: `npm run lint:fix && npm run format`
5. Commit changes (triggers pre-commit hooks)
6. Push and create PR

---

## Deployment

### Netlify Deployment

#### Step 1: Create `netlify.toml`
```toml
[build]
  command = "npm run build"
  publish = "dist"

[build.environment]
  NODE_VERSION = "18"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200

[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "DENY"
    X-Content-Type-Options = "nosniff"
    Referrer-Policy = "strict-origin-when-cross-origin"
```

#### Step 2: Deploy
```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login
netlify login

# Deploy
netlify deploy --prod
```

### Vercel Deployment

#### Step 1: Install Vercel CLI
```bash
npm install -g vercel
```

#### Step 2: Deploy
```bash
# Login
vercel login

# Deploy
vercel --prod
```

#### Step 3: Configure Environment Variables
Add environment variables in Vercel dashboard:
- `VITE_API_BASE_URL`
- `VITE_API_VERSION`

### Docker Deployment

#### Create `Dockerfile`
```dockerfile
# Build stage
FROM node:18-alpine AS build

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

#### Create `nginx.conf`
```nginx
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
}
```

#### Build and Run
```bash
# Build Docker image
docker build -t comptia-frontend .

# Run container
docker run -p 80:80 comptia-frontend
```

---

## Troubleshooting

### Common Issues

#### Issue: Import path errors with `@/` alias
**Solution**: Ensure `tsconfig.json` has correct path mapping and restart VS Code.

#### Issue: Tailwind styles not applying
**Solution**:
1. Check `tailwind.config.js` content paths include all files
2. Verify `@tailwind` directives are in `src/index.css`
3. Restart dev server

#### Issue: Tests failing with module resolution errors
**Solution**: Ensure `vitest.config.ts` has same path alias as `vite.config.ts`.

#### Issue: ESLint not working
**Solution**: Install ESLint extension in VS Code and reload window.

#### Issue: Environment variables not loading
**Solution**:
1. Ensure `.env.local` exists
2. Restart dev server after changing env vars
3. Verify variables start with `VITE_`

---

## Next Steps

After completing setup:

1. **Review specifications**:
   - Read `00-overview.md` for project goals
   - Review `01-design-system.md` for design tokens
   - Study `04-component-architecture.md` for component structure

2. **Set up base components**:
   - Create layout components (AppShell, Sidebar, MobileNav)
   - Set up routing structure
   - Implement authentication flow

3. **Start development**:
   - Begin with Sprint 1 tasks from `00-overview.md`
   - Follow TDD approach from `06-testing-strategy.md`
   - Reference `05-feature-implementation-guide.md` for patterns

4. **Maintain quality**:
   - Write tests for all features
   - Keep coverage above 80%
   - Follow accessibility guidelines
   - Document complex components

---

## Summary Checklist

Before starting development, ensure:

- [ ] Node.js 18+ installed
- [ ] Project created with Vite
- [ ] All dependencies installed
- [ ] Tailwind CSS configured
- [ ] Shadcn/ui initialized
- [ ] ESLint and Prettier set up
- [ ] Husky and lint-staged configured
- [ ] Environment variables created
- [ ] Development server runs successfully
- [ ] Tests run successfully
- [ ] VS Code extensions installed
- [ ] Git repository initialized

**You're ready to build!** 🚀
