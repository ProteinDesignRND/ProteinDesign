/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // FUSE Official Design System: Deep Obsidian Black & Light Blue Accents
        fuse: {
          bg: '#080808',          // Main background: Deep Obsidian Black
          secondary: '#0E0E0E',   // Secondary background: Deep Charcoal
          panel: '#141414',       // Main panels: Sleek Dark Surface
          elevated: '#1C1C1C',    // Elevated surfaces: Elevated Dark Tile
          border: '#282828',      // Standard borders: Subtle Dark Divider
          blue: '#38BDF8',        // Primary button / interactive accent: Light Blue
          blueHover: '#7DD3FC',   // Button hover
          ice: '#38BDF8',         // Secondary accent / success: Soft Ice Blue
          gold: '#B99B6A',        // Highlight / warning: Antique Gold
          text: '#F5F5F5',        // Primary text: Crisp Off-White
          secondaryText: '#A3A3A3', // Secondary text: Clean Slate
          mutedText: '#666666',   // Muted text: Neutral Muted
          disabled: '#444444',    // Disabled text
          error: '#C47F70',       // Error (Muted Terracotta)
          info: '#9CA99A',        // Information (Muted Sage)
        },
        nb: {
          bg: '#080808',
          secondary: '#0E0E0E',
          surface: '#141414',
          elevated: '#1C1C1C',
          border: '#282828',
          copper: '#38BDF8',
          copperHover: '#7DD3FC',
          sage: '#38BDF8',
          citron: '#B99B6A',
          text: '#F5F5F5',
          taupe: '#A3A3A3',
          muted: '#666666',
          disabled: '#444444',
          warning: '#B99B6A',
          error: '#C47F70',
          info: '#9CA99A',
        },
        plddt: {
          veryhigh: '#38BDF8',
          high: '#9CA99A',
          medium: '#B99B6A',
          low: '#C47F70',
        }
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'system-ui', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'Menlo', 'Consolas', 'monospace'],
      },
    },
  },
  plugins: [],
}
