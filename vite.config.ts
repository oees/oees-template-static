/// <reference types="vitest/config" />
import { readdirSync } from "node:fs";
import { resolve } from "node:path";

import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

const ROOT = import.meta.dirname;
const SKIP_DIRS = new Set([
  "node_modules",
  "dist",
  "public",
  "src",
  "docs",
  "scripts",
  ".github",
  ".do",
  ".claude",
]);

// Every .html file in the project is a page: index.html is "/", ejemplo/index.html is "/ejemplo/".
// Add a page by adding a folder with an index.html. 404.html is the page for unknown paths.
function findPages(dir: string): string[] {
  return readdirSync(dir, { withFileTypes: true }).flatMap((entry) => {
    if (entry.isDirectory()) {
      return SKIP_DIRS.has(entry.name) || entry.name.startsWith(".")
        ? []
        : findPages(resolve(dir, entry.name));
    }
    return entry.name.endsWith(".html") ? [resolve(dir, entry.name)] : [];
  });
}

export default defineConfig({
  base: "/",
  plugins: [react()],
  build: {
    rolldownOptions: {
      input: findPages(ROOT),
    },
  },
  test: {
    environment: "jsdom",
    setupFiles: ["./src/test-setup.ts"],
    include: ["src/**/*.test.{ts,tsx}"],
  },
});
