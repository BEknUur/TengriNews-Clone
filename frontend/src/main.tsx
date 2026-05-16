import React from 'react';
import ReactDOM from 'react-dom/client';
import { RouterProvider } from 'react-router-dom';
import { Toaster } from 'sonner';

import { AppInitializer } from '@/common/components/app-initializer';
import { router } from '@/router/routes';

import '@/common/styles/base.css';
import '@/common/styles/variables.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <AppInitializer />
    <RouterProvider router={router} />
    <Toaster position="top-right" richColors closeButton />
  </React.StrictMode>,
);
