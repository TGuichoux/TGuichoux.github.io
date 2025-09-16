import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';

export default defineConfig({
  plugins: [react()],
  base: '/', // user site at root domain
  resolve: {
    alias: { '@': resolve(__dirname, 'src') },
  },
});
