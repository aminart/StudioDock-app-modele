import nightNavy from "night-navy/tailwind-v3-preset";

/**
 * Couleurs, police et arrondis : design system Night Navy (github:aminart/Design-system-).
 * N'ajoutez pas de couleurs ici : utilisez les jetons (bg-surface, text-ink, text-accent, bg-primary…).
 */
/** @type {import('tailwindcss').Config} */
export default {
  presets: [nightNavy],
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
};
