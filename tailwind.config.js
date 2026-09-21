/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{html,py}",
    "./static/**/*.{html,js}",
    "./templates/**/*.html",
  ],
  theme: {
    extend: {
      colors: {
        // Golf-themed color palette
        'golf': {
          // Greens (fairway, rough, dark green)
          'fairway': '#f0f4ec',      // Light green-tinted background
          'green': '#4a7c2c',         // Golf course green
          'green-dark': '#2d5016',    // Dark green
          'green-light': '#6ba547',   // Light green
          'rough': '#7d8f69',         // Muted green for secondary elements

          // Golds (trophy, championship, accent)
          'gold': '#d4af37',          // Classic gold
          'gold-dark': '#b8941f',     // Darker gold for hover states
          'gold-light': '#ffd700',    // Bright gold for highlights

          // Navy (text, headers, professional)
          'navy': '#1a2332',          // Deep navy for text
          'navy-light': '#2c3e50',    // Lighter navy for secondary text

          // White/Neutrals
          'white': '#ffffff',
          'sand': '#f5f1e8',          // Sand trap color for backgrounds
          'gray-light': '#e5e7eb',    // Light gray
          'gray': '#6b7280',          // Medium gray
          'gray-dark': '#374151',     // Dark gray
        },

        // Status colors
        'success': '#10b981',         // Green for success
        'warning': '#f59e0b',         // Amber for warnings
        'error': '#ef4444',           // Red for errors
        'info': '#3b82f6',            // Blue for info
      },
      fontFamily: {
        sans: [
          'Inter',
          'system-ui',
          '-apple-system',
          'BlinkMacSystemFont',
          'Segoe UI',
          'Roboto',
          'Helvetica Neue',
          'Arial',
          'sans-serif',
        ],
        mono: [
          'JetBrains Mono',
          'Fira Code',
          'Consolas',
          'Monaco',
          'Courier New',
          'monospace',
        ],
      },
      spacing: {
        '128': '32rem',
        '144': '36rem',
      },
      borderRadius: {
        '4xl': '2rem',
      },
      boxShadow: {
        'golf': '0 4px 6px -1px rgba(45, 80, 22, 0.1), 0 2px 4px -1px rgba(45, 80, 22, 0.06)',
        'golf-lg': '0 10px 15px -3px rgba(45, 80, 22, 0.1), 0 4px 6px -2px rgba(45, 80, 22, 0.05)',
        'gold': '0 4px 6px -1px rgba(212, 175, 55, 0.2), 0 2px 4px -1px rgba(212, 175, 55, 0.1)',
        'gold-lg': '0 10px 15px -3px rgba(212, 175, 55, 0.2), 0 4px 6px -2px rgba(212, 175, 55, 0.1)',
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'bounce-gentle': 'bounceGentle 2s infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        bounceGentle: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-5px)' },
        },
      },
    },
  },
  plugins: [
    // Add forms plugin for better form styling
    // require('@tailwindcss/forms'),
    // Add typography plugin for rich text content
    // require('@tailwindcss/typography'),
  ],
}
