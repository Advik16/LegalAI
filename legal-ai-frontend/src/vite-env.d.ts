/// <reference types="vite/client" />

interface ImportMetaEnv {
    readonly VITE_API_BASE_URL: string;
    readonly VITE_APP_NAME?: string;
    // add other env variables here
  }
  
  interface ImportMeta {
    readonly env: ImportMetaEnv;
  }