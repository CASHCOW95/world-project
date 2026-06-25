/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./core/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontSize: {
        'xs': '0.875rem',   // 원래 12px -> 14px로 (sm 수준)
        'sm': '1rem',       // 원래 14px -> 16px로 (base 수준)
        'base': '1.125rem', // 원래 16px -> 18px로 (lg 수준)
        'lg': '1.25rem',    // 원래 18px -> 20px로 (xl 수준)
        'xl': '1.5rem',     // 원래 20px -> 24px로 (2xl 수준)
        '2xl': '1.875rem',  // 원래 24px -> 30px로 (3xl 수준)
        '3xl': '2.25rem',   // 원래 30px -> 36px로 (4xl 수준)
        '4xl': '3rem',      // 원래 36px -> 48px로 (5xl 수준)
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      }
    },
  },
  plugins: [],
}
