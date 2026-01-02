# CSS Architecture

## Overview

This project uses a **component-based CSS architecture** inspired by React component patterns. Each UI component has its own CSS file, organized in a modular structure that promotes maintainability and scalability.

## Philosophy

### Component-First Approach

Like React components, our CSS is organized by component responsibility:
- Each UI component = One CSS file
- Clear boundaries between components
- Easy to locate and modify styles
- Prevents style conflicts and duplication

### BEM Naming Convention

We use **BEM (Block Element Modifier)** naming for CSS classes:

```
Block__Element--Modifier
```

**Examples:**
- `Button` - Block (component)
- `Button__icon` - Element (part of component)
- `Button--primary` - Modifier (variant of component)

This is analogous to React props and component composition:

```jsx
// React Component
<Button variant="primary" icon={<Icon />}>
  Click me
</Button>

// BEM CSS
<button class="Button Button--primary">
  <span class="Button__icon"></span>
  Click me
</button>
```

## Directory Structure

```
static/css/
├── main.css                    # Entry point (like React's index.js)
│
├── base/                       # Foundation layer
│   ├── reset.css              # CSS reset
│   ├── variables.css          # Design tokens (:root variables)
│   └── typography.css         # Base typography
│
├── layout/                     # Layout components
│   ├── Container.css          # Max-width container
│   ├── Navbar.css             # Site navigation
│   └── Footer.css             # Site footer
│
├── components/                 # Reusable UI components
│   ├── Button.css             # Button with variants
│   ├── Card.css               # Generic card
│   ├── Tag.css                # Tags/labels
│   ├── StatusBadge.css        # Status indicator
│   ├── PhoneMockup.css        # Phone device mockup
│   └── SectionHeader.css      # Section headers
│
├── sections/                   # Page sections
│   ├── Hero.css               # Hero section
│   ├── TechGrid.css           # Technologies grid
│   ├── ProjectCard.css        # Project cards
│   ├── PostCard.css           # Blog post cards
│   └── Timeline.css           # Experience timeline
│
├── pages/                      # Page-specific styles
│   ├── BlogDetail.css         # Blog post detail page
│   └── BlogList.css           # Blog posts listing
│
└── dist/                       # Built CSS (generated, not committed)
    └── styles.css             # Compiled output
```

## Build System

### PostCSS

We use **PostCSS** for CSS processing with the following plugins:

1. **postcss-import** - Enables `@import` for modularity
2. **postcss-nesting** - CSS nesting (like Sass/styled-components)
3. **autoprefixer** - Automatic vendor prefixes
4. **cssnano** - Minification for production

### Build Commands

**All commands are executed via Makefile** (works in Docker and locally):

```bash
# Install Node.js dependencies
make css-install

# Development build (one-time)
make css-build

# Development with watch mode (auto-rebuild on changes)
make css-watch

# Production build (minified)
make css-prod
```

### Build Configuration

**postcss.config.js:**
```javascript
module.exports = {
  plugins: [
    require('postcss-import'),
    require('postcss-nesting'),
    require('autoprefixer'),
    ...(process.env.NODE_ENV === 'production'
      ? [require('cssnano')({ preset: 'default' })]
      : []
    ),
  ],
};
```

## CSS Nesting

PostCSS nesting allows you to write nested selectors like styled-components:

**Before (Flat CSS):**
```css
.Button { }
.Button--primary { }
.Button--primary:hover { }
.Button__icon { }
```

**After (Nested CSS):**
```css
.Button {
  &--primary {
    &:hover { }
  }

  &__icon { }
}
```

## Design Tokens

All design values are centralized in `base/variables.css`:

```css
:root {
  /* Colors */
  --color-text-primary: #0a0a0a;
  --color-accent: #0a0a0a;
  --color-blue: #6b9af5;

  /* Spacing */
  --spacing-xs: 0.5rem;
  --spacing-sm: 1rem;
  --spacing-md: 2rem;

  /* Shadows */
  --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.05);
}
```

**Usage:**
```css
.Card {
  padding: var(--spacing-md);
  box-shadow: var(--shadow-sm);
  color: var(--color-text-primary);
}
```

## Development Workflow

### 1. Local Development

**Terminal 1 - CSS Watch Mode:**
```bash
make css-watch
```

**Terminal 2 - Django Server:**
```bash
make up
make logs
```

The CSS watch mode will automatically rebuild when you modify any `.css` file.

**Note**: All commands run on the host machine (not inside Docker), but work with Dockerized application.

### 2. Adding a New Component

**Step 1:** Create component file
```bash
touch static/css/components/NewComponent.css
```

**Step 2:** Write component styles with BEM naming
```css
/**
 * NewComponent
 *
 * Description of component
 * Usage: <div class="NewComponent">...</div>
 */

.NewComponent {
  /* Base styles */

  /* Element */
  &__element {
    /* Element styles */
  }

  /* Modifier */
  &--variant {
    /* Variant styles */
  }
}
```

**Step 3:** Import in `main.css`
```css
@import './components/NewComponent.css';
```

**Step 4:** CSS rebuilds automatically (if watch mode is running)

### 3. Using Components in Templates

Apply BEM classes to HTML:

```django
<div class="NewComponent NewComponent--variant">
  <div class="NewComponent__element">
    Content
  </div>
</div>
```

## Component Documentation Pattern

Each CSS file should include a header comment:

```css
/**
 * ComponentName
 *
 * Brief description of the component.
 *
 * Usage:
 *   <element class="ComponentName ComponentName--variant">
 *     <element class="ComponentName__element">...</element>
 *   </element>
 *
 * Variants:
 *   --primary    Primary variant
 *   --secondary  Secondary variant
 */
```

## Deployment

### Production Build

Use Makefile for consistent deployment (works on any server):

```bash
# Full deployment (includes CSS build)
make deploy
```

This command automatically:
1. Builds production CSS (minified)
2. Stops containers
3. Rebuilds containers
4. Runs migrations
5. Collects static files
6. Fixes permissions
7. Reloads Nginx

### Manual Production Build

If you need to build CSS separately:

```bash
# Build production CSS
make css-prod

# Then deploy static files
make deploy-static
```

### CI/CD Integration

Add to your deployment script:

```bash
#!/bin/bash
set -e

# Deploy everything (includes CSS production build)
make deploy

# Or step-by-step:
# make css-prod
# make collectstatic
# make restart
```

## File Size Comparison

- **Before** (monolithic): ~27 KB
- **After** (component-based, minified): ~25 KB
- **Reduction**: ~7% smaller + better organization

## Migration from Old CSS

The old monolithic `static/css/styles.css` has been split into 25+ component files. Old class names remain compatible for now, but new code should use BEM naming.

### Class Name Migration

| Old Class | New BEM Class |
|-----------|---------------|
| `.navbar` | `.Navbar` |
| `.nav-brand` | `.Navbar__brand` |
| `.btn-primary` | `.Button Button--primary` |
| `.hero` | `.Hero` |
| `.hero-content` | `.Hero__content` |
| `.footer` | `.Footer` |
| `.footer-content` | `.Footer__content` |

## React Component Analogy

| React Pattern | CSS Pattern |
|--------------|-------------|
| `Button.jsx` | `Button.css` |
| `<Button variant="primary">` | `<a class="Button Button--primary">` |
| `export default Button` | `@import './components/Button.css'` |
| CSS Modules | BEM naming |
| styled-components nesting | PostCSS nesting |
| Theme context | CSS variables (`:root`) |

## Troubleshooting

### CSS not updating

1. **Check watch mode is running:**
   ```bash
   make css-watch
   ```

2. **Hard refresh browser:** `Cmd+Shift+R` (Mac) or `Ctrl+Shift+R` (Windows)

3. **Rebuild manually:**
   ```bash
   make css-build
   ```

4. **Restart containers:**
   ```bash
   make restart
   ```

### Build errors

**Error: Cannot find module 'postcss-import'**
```bash
make css-install
```

**Error: Permission denied**
```bash
rm -rf node_modules package-lock.json
make css-install
```

**Error: make: command not found**

Install `make` on your system:
- **macOS**: Comes pre-installed with Xcode Command Line Tools
- **Ubuntu/Debian**: `sudo apt-get install build-essential`
- **Windows**: Install via WSL2 or use Git Bash

## Best Practices

### DO ✅

- Use BEM naming for new components
- Keep components focused (single responsibility)
- Use CSS variables for colors, spacing, shadows
- Document components with header comments
- Run watch mode during development
- Build production CSS before deploying

### DON'T ❌

- Don't use inline styles in templates
- Don't hardcode colors/spacing (use variables)
- Don't create overly specific selectors
- Don't forget to import new components in `main.css`
- Don't commit `static/css/dist/` to git
- Don't use `!important` (fix specificity instead)

## Further Reading

- [BEM Methodology](https://getbem.com/)
- [PostCSS Documentation](https://postcss.org/)
- [CSS Nesting Specification](https://drafts.csswg.org/css-nesting/)
- [Atomic Design](https://bradfrost.com/blog/post/atomic-web-design/)
