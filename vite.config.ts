import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';

const rawBase = process.env.VITE_BASE_PATH || '/';
const withTrailing = rawBase.endsWith('/') ? rawBase : `${rawBase}/`;
const normalisedBase = withTrailing.startsWith('/') ? withTrailing : `/${withTrailing}`;

export default defineConfig({
  plugins: [react()],
  base: normalisedBase,
  resolve: {
    alias: { '@': resolve(__dirname, 'src') },
  },
});
