/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-conic':
          'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
      },
      colors: {
        primary: {
          50: '#f0f2ff',
          100: '#e6eaff',
          500: '#667eea',
          600: '#5a6fd8',
          700: '#4f5fc7',
        },
        secondary: {
          500: '#764ba2',
          600: '#6a4190',
          700: '#5e377e',
        }
      }
    },
  },
  plugins: [],
} 