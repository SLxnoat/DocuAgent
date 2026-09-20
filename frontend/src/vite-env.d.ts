/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string;
  readonly VITE_API_HOST: string;
  readonly VITE_API_TOKEN: string;
  readonly VITE_ENABLE_PDF_EXPORT: string;
  readonly VITE_ENABLE_WEBSOCKET_CHAT: string;
  readonly VITE_MAX_SCRIPT_LENGTH: string;
  readonly VITE_EDITOR_THEME: string;
  readonly VITE_DEFAULT_LANGUAGE: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
