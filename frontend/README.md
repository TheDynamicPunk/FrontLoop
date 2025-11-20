# FrontLoop Frontend

React + TypeScript frontend for the FrontLoop salon agent application.

## Features

- **Customer Chat Tab**: Real-time chat interface with the AI agent
- **Supervisor Dashboard**: View and respond to customer help requests
- **Responsive Design**: Works on desktop and mobile devices

## Setup

1. Install dependencies:
```bash
npm install
```

2. Start development server:
```bash
npm run dev
```

The app will be available at `http://localhost:3000`

## Build

```bash
npm run build
```

## Environment

Update `vite.config.ts` to configure the backend API URL:
```typescript
proxy: {
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true
  }
}
```

## Project Structure

```
src/
├── components/
│   ├── CustomerChat.tsx      # Customer chat interface
│   ├── CustomerChat.css
│   ├── SupervisorDashboard.tsx # Supervisor request management
│   └── SupervisorDashboard.css
├── App.tsx                   # Main app with tab switcher
├── App.css
├── main.tsx
└── index.css
```
