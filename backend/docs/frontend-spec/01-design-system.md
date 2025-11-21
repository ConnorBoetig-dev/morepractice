# Design System

A clean, modern, professional design system for CompTIA exam preparation platform targeting computer professionals and students.

## Design Philosophy

**Core Principles:**
1. **Clarity over flair** - Information hierarchy is clear, not cluttered
2. **Professional, not playful** - Suitable for adult learners and professionals
3. **Focused on learning** - Features support education, not distraction
4. **Accessible by default** - WCAG 2.1 AA compliance minimum
5. **Responsive first** - Mobile through desktop (320px - 1920px+)

**Inspiration:**
- **Duolingo**: Gamification done right (achievements, streaks, levels)
- **Khan Academy**: Clean, educational, trustworthy
- **FreeCodeCamp**: Progress tracking, clear learning paths
- **CompTIA Official**: Professional certification aesthetic

---

## Color Palette

### Primary Colors

**Blue (Primary Brand Color)**
- Purpose: Trust, learning, progress, primary actions
- Usage: Buttons, links, active states, progress bars

```css
--primary-50:  #eff6ff  /* Lightest - hover backgrounds */
--primary-100: #dbeafe  /* Light - selected states */
--primary-200: #bfdbfe  /* Light - badges */
--primary-300: #93c5fd  /* Medium light - disabled */
--primary-400: #60a5fa  /* Medium - hover states */
--primary-500: #3b82f6  /* Base - primary buttons, links */
--primary-600: #2563eb  /* Dark - button hover */
--primary-700: #1d4ed8  /* Darker - active states */
--primary-800: #1e40af  /* Very dark - text on light */
--primary-900: #1e3a8a  /* Darkest - headings */
```

**Usage Examples:**
- Primary buttons: `bg-primary-600 hover:bg-primary-700`
- Links: `text-primary-600 hover:text-primary-700`
- Progress bars: `bg-primary-500`

### Success (Correct Answers, Achievements)

```css
--success-50:  #f0fdf4  /* Achievement unlock background */
--success-100: #dcfce7
--success-200: #bbf7d0
--success-300: #86efac
--success-400: #4ade80
--success-500: #22c55e  /* Base - correct answer indicator */
--success-600: #16a34a  /* Achievement badges */
--success-700: #15803d
--success-800: #166534
--success-900: #14532d
```

**Usage:**
- Correct answers: Border/background `success-500`
- Achievement badges: `bg-success-600`
- Success toasts: `bg-success-50 border-success-600`

### Warning (Time Limits, Cautions)

```css
--warning-50:  #fffbeb
--warning-100: #fef3c7
--warning-200: #fde68a
--warning-300: #fcd34d
--warning-400: #fbbf24
--warning-500: #f59e0b  /* Base - timer warnings */
--warning-600: #d97706  /* Important notifications */
--warning-700: #b45309
--warning-800: #92400e
--warning-900: #78350f
```

**Usage:**
- Quiz timer (< 5min remaining): `text-warning-600`
- Warning toasts: `bg-warning-50 border-warning-600`

### Error (Incorrect Answers, Validation Errors)

```css
--error-50:  #fef2f2
--error-100: #fee2e2
--error-200: #fecaca
--error-300: #fca5a5
--error-400: #f87171
--error-500: #ef4444  /* Base - incorrect answers */
--error-600: #dc2626  /* Error messages */
--error-700: #b91c1c
--error-800: #991b1b
--error-900: #7f1d1d
```

**Usage:**
- Incorrect answers: Border/background `error-500`
- Validation errors: `text-error-600`
- Error toasts: `bg-error-50 border-error-600`

### Neutral (Text, Backgrounds, Borders)

```css
--neutral-50:  #f9fafb  /* Page backgrounds */
--neutral-100: #f3f4f6  /* Card backgrounds */
--neutral-200: #e5e7eb  /* Borders, dividers */
--neutral-300: #d1d5db  /* Disabled text */
--neutral-400: #9ca3af  /* Placeholder text */
--neutral-500: #6b7280  /* Secondary text */
--neutral-600: #4b5563  /* Body text */
--neutral-700: #374151  /* Headings */
--neutral-800: #1f2937  /* Strong headings */
--neutral-900: #111827  /* Darkest text */
```

**Usage:**
- Page background: `bg-neutral-50`
- Card background: `bg-white` or `bg-neutral-100`
- Body text: `text-neutral-700`
- Headings: `text-neutral-900`
- Borders: `border-neutral-200`

### Accent Colors (Special Uses)

**Purple** (XP, Levels, Premium Features)
```css
--accent-purple-500: #a855f7  /* XP indicators */
--accent-purple-600: #9333ea  /* Level badges */
```

**Orange** (Streaks, Fire)
```css
--accent-orange-500: #f97316  /* Streak flames */
--accent-orange-600: #ea580c  /* Streak counter */
```

**Gold** (Achievements, Trophies)
```css
--accent-gold-400: #fbbf24   /* Trophy icons */
--accent-gold-500: #f59e0b   /* Achievement glow */
```

---

## Typography

### Font Families

**System Font Stack** (Fast loading, native feel)
```css
--font-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto',
             'Helvetica Neue', Arial, sans-serif;

--font-mono: 'Fira Code', 'SF Mono', Monaco, 'Cascadia Code',
             'Consolas', monospace;
```

**Why System Fonts?**
- Zero font loading time
- Native OS appearance
- Excellent readability
- Smaller bundle size

**Alternative (if custom fonts desired):**
```css
/* If you want Inter (optional, adds ~50KB) */
--font-sans: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
```

### Font Sizes

**Desktop Scale** (base: 16px)
```css
--text-xs:   0.75rem  /* 12px - timestamps, captions */
--text-sm:   0.875rem /* 14px - secondary text */
--text-base: 1rem     /* 16px - body text */
--text-lg:   1.125rem /* 18px - large body */
--text-xl:   1.25rem  /* 20px - h4 */
--text-2xl:  1.5rem   /* 24px - h3 */
--text-3xl:  1.875rem /* 30px - h2 */
--text-4xl:  2.25rem  /* 36px - h1 */
--text-5xl:  3rem     /* 48px - hero text */
```

**Mobile Scale** (slightly smaller for readability)
```css
/* Automatically reduced by 1-2px at breakpoints < 640px */
--text-base: 0.9375rem  /* 15px on mobile */
--text-lg:   1rem       /* 16px on mobile */
```

### Font Weights

```css
--font-normal:    400  /* Body text */
--font-medium:    500  /* Emphasized text, buttons */
--font-semibold:  600  /* Subheadings */
--font-bold:      700  /* Headings, strong emphasis */
```

**Usage:**
- Body text: `font-normal`
- Buttons, labels: `font-medium`
- Subheadings: `font-semibold`
- Main headings: `font-bold`

### Line Heights

```css
--leading-tight:  1.25  /* Headings */
--leading-snug:   1.375 /* UI elements */
--leading-normal: 1.5   /* Body text (optimal for reading) */
--leading-relaxed: 1.625 /* Long-form content */
```

### Typography Components

**Heading Styles:**
```tsx
<h1 className="text-3xl font-bold text-neutral-900 leading-tight">
  Dashboard
</h1>

<h2 className="text-2xl font-bold text-neutral-800 leading-tight">
  Recent Activity
</h2>

<h3 className="text-xl font-semibold text-neutral-700">
  Quiz Results
</h3>
```

**Body Text:**
```tsx
<p className="text-base text-neutral-700 leading-normal">
  Regular paragraph text with optimal readability.
</p>

<p className="text-sm text-neutral-600">
  Secondary information, captions, metadata.
</p>
```

**Code/Monospace** (for exam questions with code):
```tsx
<code className="font-mono text-sm bg-neutral-100 px-2 py-1 rounded">
  ssh root@server.com
</code>
```

---

## Spacing System

**8px Grid System** (Tailwind default)

```css
--space-0:  0       /* 0px */
--space-1:  0.25rem /* 4px  - tight spacing */
--space-2:  0.5rem  /* 8px  - small gaps */
--space-3:  0.75rem /* 12px - default gaps */
--space-4:  1rem    /* 16px - standard spacing */
--space-5:  1.25rem /* 20px - medium spacing */
--space-6:  1.5rem  /* 24px - large spacing */
--space-8:  2rem    /* 32px - section spacing */
--space-10: 2.5rem  /* 40px - major sections */
--space-12: 3rem    /* 48px - page margins */
--space-16: 4rem    /* 64px - hero spacing */
```

**Usage Examples:**
- Between elements in a card: `gap-4` (16px)
- Card padding: `p-6` (24px)
- Page margins: `px-4 md:px-8 lg:px-12`
- Section gaps: `space-y-8` (32px vertical)

---

## Component Specifications

### Buttons

**Primary Button** (Main actions)
```tsx
<button className="
  px-6 py-3
  bg-primary-600 hover:bg-primary-700 active:bg-primary-800
  text-white font-medium
  rounded-lg
  transition-colors duration-150
  focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2
  disabled:bg-neutral-300 disabled:cursor-not-allowed
">
  Start Quiz
</button>
```

**Secondary Button** (Alternative actions)
```tsx
<button className="
  px-6 py-3
  bg-white hover:bg-neutral-50
  text-primary-600 hover:text-primary-700
  font-medium
  border border-primary-300
  rounded-lg
  transition-colors duration-150
  focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2
">
  View History
</button>
```

**Danger Button** (Destructive actions)
```tsx
<button className="
  px-6 py-3
  bg-error-600 hover:bg-error-700
  text-white font-medium
  rounded-lg
  transition-colors duration-150
  focus:outline-none focus:ring-2 focus:ring-error-500 focus:ring-offset-2
">
  Delete Account
</button>
```

**Small Button**
```tsx
<button className="px-4 py-2 text-sm ...">
  Submit
</button>
```

**Icon Button**
```tsx
<button className="
  p-2
  hover:bg-neutral-100
  rounded-lg
  transition-colors
">
  <Icon className="w-5 h-5 text-neutral-600" />
</button>
```

### Inputs

**Text Input**
```tsx
<input
  type="text"
  className="
    w-full px-4 py-3
    border border-neutral-300 focus:border-primary-500
    rounded-lg
    text-neutral-900 placeholder:text-neutral-400
    focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-1
    disabled:bg-neutral-100 disabled:cursor-not-allowed
  "
  placeholder="Enter your email..."
/>
```

**Input with Error**
```tsx
<input className="
  border-error-500 focus:border-error-600
  focus:ring-error-500
" />
<p className="mt-1 text-sm text-error-600">
  Email is required
</p>
```

**Textarea**
```tsx
<textarea
  rows={4}
  className="
    w-full px-4 py-3
    border border-neutral-300 focus:border-primary-500
    rounded-lg
    resize-none
    focus:outline-none focus:ring-2 focus:ring-primary-500
  "
/>
```

### Cards

**Base Card**
```tsx
<div className="
  bg-white
  border border-neutral-200
  rounded-lg
  p-6
  shadow-sm hover:shadow-md
  transition-shadow duration-200
">
  {children}
</div>
```

**Clickable Card** (e.g., exam selection)
```tsx
<div className="
  bg-white
  border-2 border-neutral-200 hover:border-primary-500
  rounded-lg
  p-6
  cursor-pointer
  transition-all duration-200
  hover:shadow-lg
">
  {children}
</div>
```

**Highlighted Card** (active/selected state)
```tsx
<div className="
  bg-primary-50
  border-2 border-primary-500
  rounded-lg
  p-6
  shadow-md
">
  {children}
</div>
```

### Badges

**Status Badge**
```tsx
<span className="
  inline-flex items-center
  px-3 py-1
  bg-success-100 text-success-800
  text-xs font-medium
  rounded-full
">
  Active
</span>
```

**Count Badge** (e.g., achievement count)
```tsx
<span className="
  inline-flex items-center justify-center
  min-w-[24px] h-6 px-2
  bg-primary-600 text-white
  text-xs font-bold
  rounded-full
">
  12
</span>
```

### Modals

**Modal Overlay**
```tsx
<div className="
  fixed inset-0
  bg-black/50
  backdrop-blur-sm
  z-50
">
  {/* Modal content */}
</div>
```

**Modal Content**
```tsx
<div className="
  fixed inset-0
  flex items-center justify-center
  p-4
  z-50
">
  <div className="
    bg-white
    rounded-xl
    shadow-2xl
    max-w-lg w-full
    max-h-[90vh] overflow-y-auto
  ">
    {/* Header */}
    <div className="px-6 py-4 border-b border-neutral-200">
      <h2 className="text-xl font-bold">Modal Title</h2>
    </div>

    {/* Body */}
    <div className="px-6 py-4">
      {children}
    </div>

    {/* Footer */}
    <div className="px-6 py-4 border-t border-neutral-200 flex justify-end gap-3">
      <Button variant="secondary">Cancel</Button>
      <Button variant="primary">Confirm</Button>
    </div>
  </div>
</div>
```

### Toast Notifications

**Success Toast**
```tsx
<div className="
  flex items-center gap-3
  px-4 py-3
  bg-success-50 border border-success-600
  text-success-900
  rounded-lg
  shadow-lg
">
  <CheckCircleIcon className="w-5 h-5 text-success-600" />
  <p className="font-medium">Achievement unlocked!</p>
</div>
```

**Error Toast**
```tsx
<div className="
  flex items-center gap-3
  px-4 py-3
  bg-error-50 border border-error-600
  text-error-900
  rounded-lg
  shadow-lg
">
  <XCircleIcon className="w-5 h-5 text-error-600" />
  <p className="font-medium">Failed to submit quiz</p>
</div>
```

### Progress Bars

**Linear Progress**
```tsx
<div className="w-full h-2 bg-neutral-200 rounded-full overflow-hidden">
  <div
    className="h-full bg-primary-600 transition-all duration-300"
    style={{ width: `${progress}%` }}
  />
</div>
```

**Progress with Label**
```tsx
<div>
  <div className="flex justify-between text-sm mb-1">
    <span className="text-neutral-600">Progress</span>
    <span className="font-medium text-neutral-900">75%</span>
  </div>
  <div className="w-full h-2 bg-neutral-200 rounded-full">
    <div className="h-full bg-primary-600" style={{ width: '75%' }} />
  </div>
</div>
```

**Circular Progress** (for XP to next level)
```tsx
{/* Use a library like react-circular-progressbar */}
<CircularProgressbar
  value={xpProgress}
  text={`${xpProgress}%`}
  styles={{
    path: { stroke: '#3b82f6' },
    text: { fill: '#374151', fontSize: '1.5rem', fontWeight: 600 }
  }}
/>
```

---

## Iconography

**Icon Library:** Lucide React
- Clean, consistent stroke-based icons
- Excellent for educational/professional UI
- 1000+ icons available
- Optimized SVGs

**Icon Sizes:**
```css
--icon-xs: 16px  /* Inline with text */
--icon-sm: 20px  /* Buttons, list items */
--icon-md: 24px  /* Default */
--icon-lg: 32px  /* Feature icons */
--icon-xl: 48px  /* Hero icons, empty states */
```

**Usage:**
```tsx
import { BookmarkIcon, TrophyIcon } from 'lucide-react'

<BookmarkIcon className="w-5 h-5 text-neutral-600" />
<TrophyIcon className="w-6 h-6 text-accent-gold-500" />
```

---

## Shadows

**Shadow Scale:**
```css
--shadow-sm:  0 1px 2px 0 rgb(0 0 0 / 0.05)          /* Subtle depth */
--shadow:     0 1px 3px 0 rgb(0 0 0 / 0.1)           /* Default cards */
--shadow-md:  0 4px 6px -1px rgb(0 0 0 / 0.1)        /* Elevated cards */
--shadow-lg:  0 10px 15px -3px rgb(0 0 0 / 0.1)      /* Modals, dropdowns */
--shadow-xl:  0 20px 25px -5px rgb(0 0 0 / 0.1)      /* Large modals */
--shadow-2xl: 0 25px 50px -12px rgb(0 0 0 / 0.25)    /* Achievement unlocks */
```

**Usage:**
- Cards: `shadow-sm hover:shadow-md`
- Modals: `shadow-xl`
- Achievement unlock modal: `shadow-2xl`

---

## Border Radius

```css
--radius-sm:   0.25rem  /* 4px  - badges, small elements */
--radius:      0.375rem /* 6px  - inputs, buttons (default) */
--radius-md:   0.5rem   /* 8px  - cards */
--radius-lg:   0.75rem  /* 12px - modals, large cards */
--radius-xl:   1rem     /* 16px - special cards */
--radius-full: 9999px   /* Fully rounded - badges, avatars */
```

**Usage:**
- Buttons, inputs: `rounded-lg` (6px)
- Cards: `rounded-lg` (8px)
- Modals: `rounded-xl` (12px)
- Avatars: `rounded-full`
- Badges: `rounded-full`

---

## Animations & Transitions

**Transition Durations:**
```css
--duration-fast:   150ms   /* Hover states, button presses */
--duration-normal: 200ms   /* Default transitions */
--duration-slow:   300ms   /* Page transitions, modals */
--duration-slower: 500ms   /* Achievement unlocks */
```

**Easing Functions:**
```css
--ease-in:     cubic-bezier(0.4, 0, 1, 1)
--ease-out:    cubic-bezier(0, 0, 0.2, 1)     /* Default - feels snappy */
--ease-in-out: cubic-bezier(0.4, 0, 0.2, 1)
--ease-bounce: cubic-bezier(0.68, -0.55, 0.265, 1.55)  /* Achievement unlocks */
```

**Common Transitions:**
```tsx
{/* Hover effects */}
<div className="transition-colors duration-150">

{/* Shadow changes */}
<div className="transition-shadow duration-200">

{/* Transform effects */}
<div className="transition-transform duration-300 hover:scale-105">

{/* Multiple properties */}
<div className="transition-all duration-200">
```

**Achievement Unlock Animation:**
```tsx
{/* Using Framer Motion */}
<motion.div
  initial={{ scale: 0, opacity: 0 }}
  animate={{ scale: 1, opacity: 1 }}
  transition={{
    type: 'spring',
    stiffness: 260,
    damping: 20
  }}
>
  <AchievementBadge />
</motion.div>
```

---

## Responsive Breakpoints

**Tailwind Default Breakpoints:**
```css
/* Mobile-first approach */
sm:  640px   /* Small tablets, large phones (landscape) */
md:  768px   /* Tablets */
lg:  1024px  /* Small laptops, tablets (landscape) */
xl:  1280px  /* Desktops */
2xl: 1536px  /* Large desktops */
```

**Usage Pattern:**
```tsx
<div className="
  px-4        /* Mobile: 16px padding */
  sm:px-6     /* Tablet: 24px padding */
  lg:px-8     /* Desktop: 32px padding */
">
  <h1 className="
    text-2xl   /* Mobile: 24px */
    lg:text-4xl /* Desktop: 36px */
  ">
    Dashboard
  </h1>
</div>
```

---

## Accessibility

**Focus States** (WCAG 2.1 AA)
```tsx
/* Always include visible focus indicators */
<button className="
  focus:outline-none
  focus:ring-2
  focus:ring-primary-500
  focus:ring-offset-2
">
```

**Color Contrast Requirements:**
- Normal text (< 18px): Minimum 4.5:1 contrast ratio
- Large text (>= 18px): Minimum 3:1 contrast ratio
- UI elements: Minimum 3:1 contrast ratio

**Tested Combinations:**
- `text-neutral-700` on `bg-white`: 10.4:1 ✅
- `text-primary-600` on `bg-white`: 5.2:1 ✅
- `text-success-800` on `bg-success-100`: 7.1:1 ✅

**Screen Reader Classes:**
```tsx
<span className="sr-only">Hidden from visual, available to screen readers</span>
```

---

## Dark Mode (Optional - Future Enhancement)

If implementing dark mode later:

```css
/* Dark mode color overrides */
.dark {
  --bg-primary: #111827;     /* neutral-900 */
  --bg-secondary: #1f2937;   /* neutral-800 */
  --text-primary: #f9fafb;   /* neutral-50 */
  --text-secondary: #d1d5db; /* neutral-300 */
}
```

**Not implementing in v1** to focus on core features. Add later if portfolio needs it.

---

## Component Library: Shadcn/ui

**Why Shadcn/ui?**
- Copy-paste components (no npm bloat)
- Built with Radix UI (accessible by default)
- Styled with Tailwind (matches our system)
- Full TypeScript support
- Customizable (we own the code)

**Components to Install:**
- Button
- Input
- Textarea
- Card
- Badge
- Modal (Dialog)
- Toast (Sonner)
- Select
- Checkbox
- Radio Group
- Progress
- Avatar
- Tabs
- Tooltip

**Installation:**
```bash
npx shadcn-ui@latest init
npx shadcn-ui@latest add button input card badge dialog toast
```

---

## Design Tokens Summary

```typescript
// tailwind.config.ts
export default {
  theme: {
    extend: {
      colors: {
        primary: { /* blue scale */ },
        success: { /* green scale */ },
        warning: { /* amber scale */ },
        error: { /* red scale */ },
        neutral: { /* gray scale */ },
        accent: {
          purple: { /* XP/levels */ },
          orange: { /* streaks */ },
          gold: { /* achievements */ },
        }
      },
      fontFamily: {
        sans: ['var(--font-sans)'],
        mono: ['var(--font-mono)'],
      },
      borderRadius: {
        lg: '0.5rem',
        xl: '1rem',
      },
      boxShadow: {
        'achievement': '0 25px 50px -12px rgb(0 0 0 / 0.25)',
      }
    }
  }
}
```

---

**Next**: Review information architecture (02-information-architecture.md)
