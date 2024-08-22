import { fileURLToPath, URL } from 'node:url'

import path from "path";
import { defineConfig } from 'vite'
import AutoImport from "unplugin-auto-import/vite";
import Components from "unplugin-vue-components/vite";
import { ElementPlusResolver } from "unplugin-vue-components/resolvers";

import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    AutoImport({
      resolvers: [ElementPlusResolver()],
    }),
    Components({
      resolvers: [
        ElementPlusResolver({
          importStyle: "sass",
          // directives: true,
          // version: "2.1.5",
        }),
      ],
    }),
  ],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
      "~/": `${path.resolve(__dirname, "src")}/`,
    },
  },
  css: {
    preprocessorOptions: {
      scss: {
        additionalData: `@use "~/assets/element/index.scss" as *;`,
      },
    },
  },
  server: {
    proxy: {
      "/api": {
        target: "http://ef32db.r29.cpolar.top",
        changeOrigin: true,
        // rewrite: (path) => path.replace(/^\/api/, ''),
      },
      "/model/similartext/": {
        target: "https://4afb32e1.r29.cpolar.top",
        changeOrigin: true,
      },
      // "/model": {
      //   target: "ws://4afb32e1.r29.cpolar.top",
      //   changeOrigin: true,
      //   ws: true,
      // },
    },
  },
});
