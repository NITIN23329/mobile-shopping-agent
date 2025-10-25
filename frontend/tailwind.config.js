import typography from "@tailwindcss/typography";

/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx,js,jsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#f4f7fe",
          100: "#e6edfd",
          200: "#d1ddfb",
          300: "#acc2f7",
          400: "#7a9df1",
          500: "#4d7bea",
          600: "#335ede",
          700: "#294dcc",
          800: "#253ea7",
          900: "#213789"
        }
      },
      boxShadow: {
        card: "0 10px 40px -20px rgba(31, 76, 209, 0.55)",
        glow: "0 0 0 3px rgba(77, 123, 234, 0.25)"
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        display: ["Plus Jakarta Sans", "Inter", "system-ui", "sans-serif"]
      }
    }
  },
  plugins: [typography]
};
