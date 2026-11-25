declare module "night-navy/theme-toggle";
declare module "night-navy/tailwind-v3-preset";

interface Window {
  NightNavy: { toggle(): void; set(theme: "light" | "dark" | null): void; current(): "light" | "dark" };
}
