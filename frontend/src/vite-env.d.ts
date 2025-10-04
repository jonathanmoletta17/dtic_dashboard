/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL?: string;
  readonly VITE_REALTIME_POLL_INTERVAL_SEC?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}