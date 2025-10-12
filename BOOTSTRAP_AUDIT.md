# Bootstrap Audit & Migration Plan

**Date:** October 13, 2025
**Phase:** 2 - Design System Consolidation

---

## Current State

### Bootstrap Usage

**Version:** Bootstrap 5.3.8
**Import Location:** `frontend/src/main.js`

```javascript
import "bootstrap/dist/css/bootstrap.min.css"
import "bootstrap"
```

**Bundle Impact:**
- Bootstrap CSS: ~150KB minified
- Bootstrap JS: ~50KB minified
- Popper.js dependency: ~20KB
- **Total:** ~220KB

---

## Files Using Bootstrap Classes

### 1. OAuthSetupWizard.vue (Session 2 - Breadcrumbs)
**Bootstrap Classes:** `breadcrumb`, `breadcrumb-item`, `bg-transparent`

**Usage:**
```html
<ol class="breadcrumb bg-transparent mb-0 pb-0">
  <li class="breadcrumb-item">...</li>
  <li class="breadcrumb-item active" aria-current="page">...</li>
</ol>
```

**Migration:** Replace with Tailwind breadcrumb (already using `flex` and `gap`)

---

### 2. GoogleAISetupWizard.vue
**Bootstrap Classes:**
- `btn`, `btn-primary`, `btn-secondary`, `btn-success`, `btn-outline-secondary`
- `btn-lg`, `btn-sm`, `btn-group`
- `btn-close`, `btn-close-white`

**Heavy Bootstrap usage** - Needs complete rewrite

---

### 3. TierDetailsModal.vue
**Bootstrap Classes:** `btn-close`, `btn`, `btn-secondary`

**Light usage** - Easy migration

---

### 4. OAuthSetupWizardEnhanced.vue
**Bootstrap Classes:**
- `btn-close`, `btn-close-white`
- `btn-group`, `btn-group-sm`
- `btn-primary`, `btn-outline-secondary`, `btn-sm`

**Moderate usage** - Button group needs attention

---

## Migration Strategy

### Phase 1: Create Design Tokens (This PR)
- Define CSS custom properties
- Color palette
- Typography scale
- Spacing scale
- Border radius values
- Shadow values

### Phase 2: Migrate Breadcrumb Component
- Convert OAuthSetupWizard breadcrumb to Tailwind
- Remove Bootstrap breadcrumb CSS

### Phase 3: Create Button Component Library
- Replace all `btn` classes with Tailwind
- Create reusable button components
- Standardize button variants

### Phase 4: Remove Bootstrap Dependency
- Remove imports from main.js
- Remove from package.json
- Verify no regressions

---

## Design Token Proposal

### Colors
```css
:root {
  /* Brand Colors */
  --color-primary-50: #eff6ff;
  --color-primary-100: #dbeafe;
  --color-primary-500: #3b82f6; /* blue-500 */
  --color-primary-600: #2563eb; /* blue-600 */
  --color-primary-700: #1d4ed8; /* blue-700 */

  --color-secondary-500: #8b5cf6; /* purple-500 */
  --color-secondary-600: #7c3aed; /* purple-600 */

  /* Semantic Colors */
  --color-success: #10b981; /* green-500 */
  --color-warning: #f59e0b; /* amber-500 */
  --color-error: #ef4444; /* red-500 */
  --color-info: #3b82f6; /* blue-500 */

  /* Neutrals */
  --color-gray-50: #f9fafb;
  --color-gray-100: #f3f4f6;
  --color-gray-200: #e5e7eb;
  --color-gray-300: #d1d5db;
  --color-gray-400: #9ca3af;
  --color-gray-500: #6b7280;
  --color-gray-600: #4b5563;
  --color-gray-700: #374151;
  --color-gray-800: #1f2937;
  --color-gray-900: #111827;
}
```

### Typography
```css
:root {
  /* Font Families */
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-mono: 'Fira Code', 'Courier New', monospace;

  /* Font Sizes */
  --text-xs: 0.75rem;    /* 12px */
  --text-sm: 0.875rem;   /* 14px */
  --text-base: 1rem;     /* 16px */
  --text-lg: 1.125rem;   /* 18px */
  --text-xl: 1.25rem;    /* 20px */
  --text-2xl: 1.5rem;    /* 24px */
  --text-3xl: 1.875rem;  /* 30px */
  --text-4xl: 2.25rem;   /* 36px */
  --text-5xl: 3rem;      /* 48px */

  /* Font Weights */
  --font-normal: 400;
  --font-medium: 500;
  --font-semibold: 600;
  --font-bold: 700;

  /* Line Heights */
  --leading-tight: 1.25;
  --leading-normal: 1.5;
  --leading-relaxed: 1.625;
}
```

### Spacing
```css
:root {
  --spacing-0: 0;
  --spacing-1: 0.25rem;  /* 4px */
  --spacing-2: 0.5rem;   /* 8px */
  --spacing-3: 0.75rem;  /* 12px */
  --spacing-4: 1rem;     /* 16px */
  --spacing-5: 1.25rem;  /* 20px */
  --spacing-6: 1.5rem;   /* 24px */
  --spacing-8: 2rem;     /* 32px */
  --spacing-10: 2.5rem;  /* 40px */
  --spacing-12: 3rem;    /* 48px */
  --spacing-16: 4rem;    /* 64px */
  --spacing-20: 5rem;    /* 80px */
  --spacing-24: 6rem;    /* 96px */
}
```

### Border Radius
```css
:root {
  --radius-none: 0;
  --radius-sm: 0.125rem;   /* 2px */
  --radius-base: 0.25rem;  /* 4px */
  --radius-md: 0.375rem;   /* 6px */
  --radius-lg: 0.5rem;     /* 8px */
  --radius-xl: 0.75rem;    /* 12px */
  --radius-2xl: 1rem;      /* 16px */
  --radius-full: 9999px;
}
```

### Shadows
```css
:root {
  --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-base: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
  --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
  --shadow-2xl: 0 25px 50px -12px rgb(0 0 0 / 0.25);
}
```

### Transitions
```css
:root {
  --transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
  --transition-base: 200ms cubic-bezier(0.4, 0, 0.2, 1);
  --transition-slow: 300ms cubic-bezier(0.4, 0, 0.2, 1);
}
```

---

## Migration Priority

### High Priority (This PR):
1. ✅ Create design tokens file
2. ✅ Migrate OAuthSetupWizard breadcrumb
3. ✅ Remove Bootstrap imports
4. ✅ Test existing components

### Medium Priority (Next PR):
5. Migrate GoogleAISetupWizard buttons
6. Migrate TierDetailsModal
7. Migrate OAuthSetupWizardEnhanced

### Low Priority (Future):
8. Create Storybook documentation
9. Add dark mode support
10. Create component variants library

---

## Benefits of Migration

### Performance:
- **-220KB bundle size** (Bootstrap removal)
- Faster page load
- Better Core Web Vitals score

### Developer Experience:
- Single source of truth (Tailwind)
- No class naming conflicts
- Easier maintenance
- Better autocomplete

### Design Consistency:
- All components use same design tokens
- Consistent spacing/colors/typography
- Easier to theme
- Dark mode ready

---

## Risks & Mitigation

### Risk 1: Visual Regressions
**Mitigation:**
- Test each component thoroughly
- Take screenshots before/after
- Visual regression testing with Percy/Chromatic

### Risk 2: Breaking Changes
**Mitigation:**
- Migrate incrementally (file by file)
- Keep Bootstrap until all migrations complete
- Deploy in stages

### Risk 3: Third-party Dependencies
**Mitigation:**
- Check if frappe-ui depends on Bootstrap
- Test all integrations after removal

---

## Success Criteria

- [ ] All Bootstrap classes replaced with Tailwind
- [ ] Bundle size reduced by ~220KB
- [ ] No visual regressions
- [ ] All tests passing
- [ ] Design tokens documented
- [ ] UX score maintained (8.5/10)

---

## Timeline

**Phase 2 Total:** 2-3 weeks

- **Week 1:** Design tokens + breadcrumb migration
- **Week 2:** Button component library + migrations
- **Week 3:** Bootstrap removal + testing + documentation

---

**Status:** In Progress
**Next Step:** Create design tokens file
