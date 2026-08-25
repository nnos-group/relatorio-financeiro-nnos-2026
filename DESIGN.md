---
name: Executive Intelligence
colors:
  surface: '#0c1322'
  surface-dim: '#0c1322'
  surface-bright: '#323949'
  surface-container-lowest: '#070e1d'
  surface-container-low: '#141b2b'
  surface-container: '#191f2f'
  surface-container-high: '#232a3a'
  surface-container-highest: '#2e3545'
  on-surface: '#dce2f7'
  on-surface-variant: '#bfc7d2'
  inverse-surface: '#dce2f7'
  inverse-on-surface: '#293040'
  outline: '#89919c'
  outline-variant: '#3f4851'
  surface-tint: '#96ccff'
  primary: '#96ccff'
  on-primary: '#003353'
  primary-container: '#3197df'
  on-primary-container: '#002c48'
  inverse-primary: '#00639a'
  secondary: '#ffb4a2'
  on-secondary: '#621100'
  secondary-container: '#822610'
  on-secondary-container: '#ff9b82'
  tertiary: '#ffb77a'
  on-tertiary: '#4c2700'
  tertiary-container: '#d37b1d'
  on-tertiary-container: '#422100'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#cee5ff'
  primary-fixed-dim: '#96ccff'
  on-primary-fixed: '#001d32'
  on-primary-fixed-variant: '#004a75'
  secondary-fixed: '#ffdad2'
  secondary-fixed-dim: '#ffb4a2'
  on-secondary-fixed: '#3c0700'
  on-secondary-fixed-variant: '#822610'
  tertiary-fixed: '#ffdcc1'
  tertiary-fixed-dim: '#ffb77a'
  on-tertiary-fixed: '#2e1500'
  on-tertiary-fixed-variant: '#6c3a00'
  background: '#0c1322'
  on-background: '#dce2f7'
  surface-variant: '#2e3545'
  surface-elevation-1: '#1F2937'
  surface-elevation-2: '#374151'
  text-primary: '#FFFFFF'
  text-muted: '#9CA3AF'
  accent-amber: '#FBBF24'
typography:
  display-lg:
    fontFamily: Manrope
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Manrope
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
  headline-lg-mobile:
    fontFamily: Manrope
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  headline-md:
    fontFamily: Manrope
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  label-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
    letterSpacing: 0.01em
  label-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.05em
  data-number:
    fontFamily: Manrope
    fontSize: 28px
    fontWeight: '700'
    lineHeight: 34px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  unit: 4px
  gutter: 24px
  margin-mobile: 16px
  margin-desktop: 32px
  container-max: 1440px
---

## Brand & Style
The design system is engineered for executive-level Business Intelligence, prioritizing clarity, authority, and high-density data visualization. The brand personality is "The Sophisticated Navigator"—reliable and sharp, transforming complex data into actionable insights.

The design style is **Corporate Modern with subtle Glassmorphism**. It utilizes a dark-mode-first approach to reduce eye strain during long analytical sessions, employing layered surfaces and precision-engineered typography. The aesthetic reflects a premium, high-tech consultancy vibe that balances the "Deep Blue" corporate foundation with energetic "Amber" accents for critical data points.

## Colors
The palette is rooted in a "Deep Sea" executive blue (#111827) which serves as the primary canvas for the dashboard. 

- **Primary Blue (#0083CA):** Used for primary actions, active states, and core branding elements.
- **Secondary Amber/Coral (#E87154):** Reserved for high-priority alerts, significant data trends, and secondary call-to-actions.
- **Executive Neutrals:** A range of slate grays derived from the background color to create hierarchical depth without breaking the dark-mode immersion.
- **Text:** Pure white is used sparingly for headers to maintain high contrast; secondary information uses muted grays to establish a clear visual hierarchy.

## Typography
The system employs a dual-font strategy. **Manrope** is used for headlines and large data indicators (KPIs) to provide a modern, structural, and slightly geometric feel that reads as "premium tech." **Inter** is used for all body text, UI labels, and interface elements to ensure maximum legibility at small sizes and high data densities.

Large numeric values in charts should utilize the `data-number` style to stand out. Tracking is tightened on headlines for a more "designed" editorial look and slightly loosened on small labels to improve scanability.

## Layout & Spacing
The layout follows a **Fixed-Fluid hybrid grid**. The sidebar is fixed at 280px, while the main dashboard area utilizes a 12-column fluid grid.

- **Rhythm:** An 8px base grid is used for component sizing, but a 4px "half-step" is permitted for tight data tables and micro-interactions.
- **Density:** High density is preferred. Information should be grouped into logical modules (cards) with 24px gutters to allow the eye to rest between different data sets.
- **Breakpoints:** 
  - Mobile: < 768px (Single column stacked)
  - Tablet: 768px - 1024px (2 columns)
  - Desktop: > 1024px (12-column grid)

## Elevation & Depth
In this design system, depth is communicated through **Tonal Stacking** and **Soft Ambient Shadows**. 

1. **Base Layer:** The deepest layer uses the primary neutral (#111827).
2. **Card Layer:** Cards are slightly elevated using a lighter fill (#1F2937). 
3. **Interactive Layer:** Hover states and modals use an even lighter fill (#374151) paired with a high-diffusion shadow: `0px 10px 30px rgba(0, 0, 0, 0.5)`.
4. **Glassmorphism:** For top navigation and floating filters, apply a 12px backdrop blur with a 10% white border-stroke to simulate polished glass, reinforcing the sophisticated executive feel.

## Shapes
The visual language uses **Rounded** geometry (8px standard) to soften the analytical nature of the data. This radius is applied to all container cards, input fields, and buttons. Larger layouts or hero sections can use `rounded-xl` (24px) to create a more contemporary, "app-like" feel, while inner elements like chips or small tags should remain subtly rounded.

## Components
- **Dashboard Cards:** The cornerstone of the UI. Use a background of `#1F2937`, a subtle 1px border of `#374151`, and an 8px corner radius. Include a header section within the card for titles and "More Info" icons.
- **Buttons:**
  - *Primary:* Solid `#0083CA` with white text.
  - *Secondary:* Ghost style with `#0083CA` border and text.
  - *Actionable:* Amber `#E87154` only for "Alert" or "Critical Export" actions.
- **Inputs:** Darker background than the card they sit on, using a 1px focus ring of the primary blue.
- **Data Tables:** Alternate row colors (zebra striping) using a very subtle contrast difference. Headers should be `label-sm` in muted gray.
- **Charts:** Use a custom palette for chart series starting with `#0083CA`, followed by `#E87154`, then complementary teal and indigo tones to maintain the professional aesthetic.
- **KPI Widgets:** Large bold typography for the metric, accompanied by a small trend sparkline and a percentage change indicator (Green for growth, Secondary Red for decline).