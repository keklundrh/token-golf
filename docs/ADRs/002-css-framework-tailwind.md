# ADR 002: CSS Framework - Tailwind CSS

## Status

Accepted

## Context

Token Golf needs a CSS framework for styling the web interface. The application requires:
- Professional, modern appearance for conference demos
- Responsive design for laptops and projection screens
- Ability to rapidly iterate on UI during development
- Consistent design system for components (pills, stat cards, leaderboards)
- Easy customization for branding

The team prefers to minimize JavaScript complexity and focus on server-side rendering with htmx and Alpine.js. The CSS solution should complement this architecture.

## Decision

We will use **Tailwind CSS** as our CSS framework.

Tailwind will be configured with:
- JIT (Just-In-Time) mode for faster builds
- Custom color palette for Token Golf branding
- Purging unused styles in production
- Integration with the build process (minimal)

## Consequences

### Positive Consequences

- **Rapid Development**: Utility-first classes enable fast prototyping
- **Consistency**: Design tokens ensure consistent spacing, colors, sizing
- **Customization**: Easy to customize via `tailwind.config.js`
- **Small Production Builds**: Purging removes unused CSS
- **Good Documentation**: Excellent docs and large community
- **Component Libraries**: Can leverage pre-built Tailwind component libraries if needed
- **No CSS Conflicts**: Utility classes avoid naming conflicts

### Negative Consequences

- **Learning Curve**: Team needs to learn Tailwind utility classes
- **HTML Verbosity**: Many utility classes in HTML templates
- **Build Step**: Requires PostCSS/Tailwind CLI (minimal overhead)
- **Initial Setup**: Configuration needed for customization

### Risks

- **Risk**: Team finds utility-first approach too verbose
  - **Mitigation**: Can extract components in templates, use `@apply` for common patterns
  - **Likelihood**: Low - Tailwind is widely adopted for good reasons

- **Risk**: Build step adds complexity
  - **Mitigation**: Minimal setup with Tailwind CLI, well-documented
  - **Likelihood**: Low - standard tooling

## Alternatives Considered

### Alternative 1: Pico.css

- **Description**: Classless CSS framework with semantic styling
- **Pros**: 
  - No classes needed - just semantic HTML
  - Tiny file size (~10KB)
  - Zero build step
  - Very fast to get started
  - Clean, minimal aesthetic
- **Cons**: 
  - Limited customization without overrides
  - Less control over specific component styling
  - Fewer ready-made components
  - Harder to create unique designs
  - Smaller ecosystem
- **Why not chosen**: Need more control and customization for professional conference demos

### Alternative 2: Custom CSS

- **Description**: Write all CSS from scratch
- **Pros**: 
  - Complete control
  - No framework overhead
  - Learn exactly what's needed
  - No dependencies
- **Cons**: 
  - Slower development
  - Inconsistent without design system
  - Reinventing common patterns
  - Harder to maintain
  - No community resources
- **Why not chosen**: Too slow for rapid iteration on conference deadline

### Alternative 3: Bootstrap

- **Description**: Traditional component-based CSS framework
- **Pros**: 
  - Well-known, mature framework
  - Pre-built components
  - Extensive documentation
  - Large ecosystem
- **Cons**: 
  - Heavier framework (~200KB)
  - jQuery dependency for some components (we're avoiding jQuery)
  - More opinionated styling (harder to customize)
  - "Bootstrap look" is very recognizable
  - Less modern than Tailwind
- **Why not chosen**: Heavier, less customizable, doesn't fit our minimal-JS approach

### Alternative 4: CSS Modules / Styled Components

- **Description**: CSS-in-JS or scoped CSS modules
- **Pros**: 
  - Scoped styles
  - Component-oriented
  - Modern approach
- **Cons**: 
  - Requires JavaScript runtime
  - Complex build setup
  - Doesn't fit server-side rendering approach
  - Overkill for our needs
- **Why not chosen**: Adds JS complexity we're trying to avoid

## Implementation Notes

### Setup
```bash
# Install Tailwind
npm install -D tailwindcss
npx tailwindcss init

# Or use standalone CLI (no Node required)
# Download tailwindcss-cli binary
```

### Configuration
```javascript
// tailwind.config.js
module.exports = {
  content: [
    './app/templates/**/*.html',
    './static/js/**/*.js',
  ],
  theme: {
    extend: {
      colors: {
        'golf-green': '#2D5F3F',
        'golf-sand': '#E8D5B7',
        // Custom colors
      },
    },
  },
  plugins: [],
}
```

### Build Process
```bash
# Development (watch mode)
npx tailwindcss -i ./static/css/input.css -o ./static/css/output.css --watch

# Production (minified)
npx tailwindcss -i ./static/css/input.css -o ./static/css/output.css --minify
```

### Integration with FastAPI
- Generated CSS served from `static/css/output.css`
- Input CSS includes Tailwind directives
- Templates use Tailwind utility classes

## References

- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Tailwind with FastAPI Example](https://github.com/tiangolo/fastapi/discussions/4693)
- [Tailwind JIT Mode](https://tailwindcss.com/docs/just-in-time-mode)
- [Tailwind UI Components](https://tailwindui.com/) (paid, but reference)

---

**Date**: 2026-09-09  
**Author**: Token Golf Team  
**Reviewers**: Karl Eklund
