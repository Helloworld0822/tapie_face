# TAPIE FACE Design System

## 0. Research Log

- Embedded refs: shortlisted `linear.app`, `sentry`, and `posthog`; picked `taste-skill` plus `linear.app` because this is a precise operational ML workbench, not a marketing page.
- Lazyweb: 3 queries, 5 screens viewed (`veriff`, `hyperverge`, `iproov`, `runway`, `luma-ai`); kept Veriff's trust cues, Runway's input-to-inference workspace, and Luma's explicit progress, empty, and failure states.
- Imagen drafts: `.omo/evidence/face-similarity/design-concepts/dark-workbench.png` and `.omo/evidence/face-similarity/design-concepts/light-workbench.png`; picked the dark workbench as the visual contract because it makes face alignment and match ranking legible without feeling clinical or threatening.
- Design read: internal face-comparison workbench for operators, using a calm dark technical language. Dials are design variance 4, motion intensity 2, and visual density 6.

## 1. Atmosphere and Identity

TAPIE FACE feels like a quiet computer-vision workbench: exact, local, and transparent about what the model did. The signature is the correction rail, a four-frame sequence that shows input, YOLO detection, five-point alignment, and hair/background suppression before a score appears. It must never borrow police, surveillance, fingerprint, or threat imagery.

Primary personas are an operator comparing a new portrait, a developer validating the pipeline, and a privacy-conscious subject who needs to understand what is stored. The main task is one-pass analysis; model setup and reference management stay secondary.

## 2. Color

The product is dark-mode-only. Emerald is the single chromatic accent and indicates interactive or successful states. Warning and error colors are semantic exceptions.

| Role | Token | Value | Use |
|---|---|---:|---|
| Canvas | `--surface-canvas` | `#080a0b` | Page background |
| Shell | `--surface-shell` | `#0d1012` | Header and fixed regions |
| Panel | `--surface-panel` | `#121619` | Primary work areas |
| Elevated | `--surface-elevated` | `#181d21` | Nested controls and result rows |
| Recessed | `--surface-recessed` | `#0a0d0f` | Image wells and logs |
| Text primary | `--text-primary` | `#f4f7f5` | Titles and values |
| Text secondary | `--text-secondary` | `#a8b0ac` | Descriptions |
| Text muted | `--text-muted` | `#87918d` | Metadata and disabled copy |
| Border subtle | `--border-subtle` | `rgba(255,255,255,.07)` | Default separators |
| Border strong | `--border-strong` | `rgba(255,255,255,.13)` | Focused wells and controls |
| Accent | `--accent` | `#31e694` | Primary actions and progress |
| Accent hover | `--accent-hover` | `#65f3af` | Hover only |
| Accent ink | `--accent-ink` | `#032719` | Text on accent |
| Warning | `--status-warning` | `#e6b65d` | Quality caution |
| Error | `--status-error` | `#ff7b7b` | Invalid image or model error |

Rules:

- Depth comes from surface luminance steps and translucent borders, not drop shadows.
- Accent appears only on controls, focus, current progress, landmarks, and the winning score.
- Raw hex and rgba values belong only in the token block in `app.css`.

## 3. Typography

- UI and Korean body: `Pretendard Variable`, `Apple SD Gothic Neo`, `Noto Sans KR`, system sans fallback.
- Numeric and model metadata: `JetBrains Mono`, `SFMono-Regular`, `Consolas`, monospace fallback.
- Use font weights 400 for reading, 520 for UI emphasis, and 650 for headings. Do not use 700+.
- Scale: 12, 13, 14, 16, 20, 28, and 36px. Line heights: 1.35 for labels, 1.5 for body, 1.1 for display values.
- Korean phrases must wrap as semantic units. Buttons and step labels never wrap on desktop.

## 4. Spacing and Layout

- Base unit is 4px; primary rhythm is 8, 12, 16, 24, 32, and 48px.
- Desktop is an application shell bounded by `100dvb`: 64px header plus one scrolling body.
- The workbench uses a 7:5 two-column grid above 960px and one column below it.
- All intrinsic grids use `repeat(auto-fit, minmax(min(16rem, 100%), 1fr))`.
- Primary body owns vertical scroll. Header and upload action bar remain visible.
- At 375px, every region is one column, controls keep 44px minimum touch height, and there is no horizontal scroll.
- Radius system: controls 6px, cards and panels 10px, status chips full-pill. These are the only radius families.

## 5. Components and States

### App header

Compact wordmark, model readiness, indexed-person count, and a reindex action. States are ready, indexing, missing models, and failed. Readiness is text plus icon/color, never color alone.

### Upload well

A real labeled file input supporting click and drag/drop. States are empty, drag-active, selected, processing, success, and error. Selected image name and size are visible. The primary analyze button stays disabled until a valid image exists and the model is ready.

### Correction rail

Four reusable `ProcessFrame` cells: original, YOLO detection, five-point alignment, and identity-only mask. Each frame has a fixed 4:5 image area, one title, and one short status line. Loading uses a shape-matched skeleton. Error states explain the failing stage.

### Result summary

Shows top identity, 0 to 100 calibrated similarity score, raw cosine similarity, and a plain-language interpretation. It must always state that similarity is not identity proof. Score color is emerald only after successful inference.

### Match row

Rank, anonymized/reference label, cosine value, calibrated score, and reference-image count. Repeated rows use the same anatomy and support long labels with ellipsis plus a title attribute.

### Quality notice

Inline notice for no face, multiple faces, low detector confidence, small face, or strong pose. Warning state never blocks unless the pipeline cannot produce a reliable embedding.

### Privacy notice

Explains that uploaded images are processed in memory and not stored by the API; reference embeddings are biometric data and require consent and protected storage.

### Primitive showcase

`/showcase` renders every primitive and the required empty, loading, success, warning, error, disabled, focus, and long-content states at mobile, tablet, and desktop widths before product QA.

## 6. Motion and Interaction

- Interaction references: beui.dev `file-upload` and `button`; reuse its explicit idle → processing → success/error state changes, 160ms opacity/transform swaps, progress feedback, and reduced-motion fallback without importing a motion library.
- Motion intensity is 2. Only action feedback and state changes move.
- Buttons translate down 1px on press and change luminance on hover.
- Processing stages cross-fade over 160ms; score and rows appear only when results are complete.
- Drag-active is indicated by border, surface, and text changes with no pulsing or infinite animation.
- `prefers-reduced-motion: reduce` disables transitions and animated skeleton shimmer.
- Keyboard focus uses a 2px emerald outline with 2px offset. Every workflow action is keyboard reachable.

## 7. Depth and Imagery

- Level 0: canvas.
- Level 1: shell and panel using one luminance step.
- Level 2: nested wells using a second luminance step plus subtle border.
- Level 3: focused or selected state using stronger border and a small inset highlight.
- Real uploaded and reference images use `object-fit: cover`, explicit dimensions, and a neutral dark fallback.
- The masked preview replaces background and hair pixels with neutral gray. It is a functional artifact, not decoration.
- No gradients, ambient blobs, glassmorphism, fake screenshots, hand-drawn icons, or decorative photography.

## 8. Accessibility Constraints and Accepted Debt

- Target WCAG 2.2 AA: 4.5:1 body contrast, 3:1 large text and controls, 44px touch targets, visible keyboard focus, semantic landmarks, labels, and live regions.
- File errors and model failures are announced through `role="alert"`; progress uses `aria-live="polite"`.
- Images have functional Korean alt text. Landmark decoration is hidden from assistive technology.
- The core task must work without drag/drop and without animation.
- Similarity never uses labels such as “same person” or “verified identity”.
- Accepted debt: camera capture is not included in the first version; users upload an existing image. No other accessibility, keyboard, motion, or CJK debt is accepted.
