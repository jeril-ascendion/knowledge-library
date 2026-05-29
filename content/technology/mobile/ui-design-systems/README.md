# Mobile UI & Design Systems

Material Design 3, Apple Human Interface Guidelines, design tokens as the cross-platform abstraction, the Figma-to-code pipeline, dark mode discipline, and component-driven development for mobile UI at enterprise scale.

**Section:** `technology/mobile/` | **Subsection:** `ui-design-systems/`
**Alignment:** Material Design 3 | Apple HIG | W3C Design Tokens Community Group | WCAG 2.2 AA
**Audience:** Mobile Engineers · UX Engineers · Mobile Architects

---

## Overview

A mobile design system in 2026 is not a Figma file. It is a typed, versioned, cross-platform package that defines design tokens (colour, typography, spacing, elevation, shape, motion), exposes them to Figma variables and to native code through generated bindings, ships Compose and SwiftUI component libraries built on top of the tokens, and is governed by a small design-systems team that owns the contract between design and engineering. Programmes that treat the design system as Figma-only ship two-truth design — what Figma says and what the app actually does — and the gap widens with every release.

Material Design 3 ("Material You") and Apple's Human Interface Guidelines have converged on a few principles in 2026: design tokens as the abstraction layer, dynamic colour as user-controlled customisation, typography scales that honour platform conventions, dark mode as a first-class theme with its own asset variants, and component-driven development as the assembly model. The platforms diverge on the specific token taxonomies (Material's `primary`/`secondary`/`tertiary`/`error` vs Apple's `accent`/`label`/`fill` semantics) and on the rendering of motion (Material's stiffness-based springs vs Apple's `Animation.snappy` and `Animation.smooth`). Cross-platform design systems either reconcile the differences in a custom token taxonomy or accept the divergence as a feature of platform-native UX.

The architectural shift is not "we use Material Design." It is: **the design system is a typed cross-platform package with tokens as the contract, generated bindings into Compose and SwiftUI, component libraries on top, dark-mode parity audited per release, accessibility built into every component, and a small dedicated team owning the contract — not Figma export by goodwill.**

---

## Core Principles

### 1. Design tokens are the contract; Figma is one of two consumers

Tokens live in JSON or YAML (the W3C Design Tokens spec is finalising; Figma's Tokens Studio and Style Dictionary by Amazon are the practical tools). Figma variables are generated from tokens; Compose `Theme` and SwiftUI `Color.semantic` mappings are generated from tokens. Designers and engineers consume the same source of truth.

### 2. Component-driven development beats screen-driven development

Components are built and tested in isolation (Storybook on web, Showkase on Android, Swift Previews in Xcode) before composition into screens. Visual regression is caught at the component level; screen-level regression is caught at integration. Component-driven development is the assembly model.

### 3. Dark mode is a first-class theme, not a colour-invert hack

Every colour token has a dark-mode pair. Every raster asset has a dark-mode variant (vectors should be tinted via tokens; PNGs need dark-mode duplicates in Android `drawable-night` and iOS asset catalogues). Third-party SDK UIs (Google Maps, PayPal SDK) are audited for dark-mode behaviour and explicitly themed where the SDK supports it.

### 4. Typography scale is the platform's scale, mapped to tokens

Material 3's Display Large → Body Small scale and Apple's Large Title → Caption 2 scale do not align numerically. The design system either defines a unified scale that maps to each platform's nearest equivalent or maintains parallel scales with documented divergence. Honouring Dynamic Type on iOS and `sp` text-size scaling on Android is non-negotiable for accessibility.

### 5. Spacing is on a grid; the grid is documented

A four-point or eight-point grid (Material is 4 dp, Apple's HIG is roughly 8 pt) underpins every spacing token. Components specify spacing in tokens (`spacing.md`, `spacing.lg`), never in raw values. Engineering reviews flag any pixel literal in component code.

### 6. Motion is a token like colour

Material 3's spring-stiffness motion model and Apple's `Animation.snappy` / `Animation.smooth` / `Animation.bouncy` give consistent feel. The design system maps named motion tokens (`motion.fast`, `motion.standard`, `motion.emphasis`) to platform-native springs.

---

## Architecture Deep-Dive

**Material Design 3 (Material You)**

Material 3 brought dynamic colour: the system extracts a colour palette from the user's wallpaper using the Monet algorithm (Material You's colour engine) and applies it to apps that opt in via `DynamicColors.applyToActivitiesIfAvailable(application)`. Apps that opt out keep their fixed brand colours. The colour role taxonomy — `primary`, `onPrimary`, `primaryContainer`, `onPrimaryContainer`, `secondary`/`tertiary`/`error` variants, `surface` and `background` with elevation overlays — replaces the legacy Material 2 `colorPrimaryDark`. Elevation in Material 3 is expressed as tonal overlays on `surface`, not as drop shadows — a `surface` at elevation 4 dp is a tinted variant of the base surface colour. Typography uses the Material 3 type scale: Display Large (57 sp) through Label Small (11 sp), each with line height and tracking documented. Shape uses extra-small through extra-large rounded-corner tokens.

**Apple Human Interface Guidelines**

SF Symbols is Apple's icon library: over 5,000 symbols, automatic Dynamic Type scaling, multicolour and hierarchical rendering modes, support for variable weight. The library is updated each iOS release; new iOS-version-specific symbols degrade gracefully on older OS versions. Dynamic Type supports 12 text size categories from `extraSmall` through `accessibilityExtraExtraExtraLarge`; apps that use `Font.body`, `Font.title`, etc. respond automatically. Safe Area insets handle the notch, Dynamic Island, and home indicator — `safeAreaPadding(.top)` and friends are non-negotiable. Platform-native interaction patterns — swipe-back from the left edge, share sheets, the iOS keyboard contract with `keyboardType` and `textContentType` — are user expectations, not stylistic preferences.

**Design Tokens — The Abstraction Layer**

A token file:

```json
{
  "color": {
    "brand": { "primary": { "value": "#C96330", "type": "color" } },
    "semantic": {
      "text": { "primary": { "value": "{color.neutral.900}" } },
      "surface": { "background": { "value": "{color.neutral.50}" } }
    }
  },
  "spacing": {
    "xs": { "value": 4 }, "sm": { "value": 8 },
    "md": { "value": 16 }, "lg": { "value": 24 }, "xl": { "value": 32 }
  },
  "typography": {
    "body": { "value": { "fontFamily": "Inter", "fontWeight": 400, "fontSize": 16, "lineHeight": 24 } }
  }
}
```

Style Dictionary or Figma Tokens Studio generates the platform outputs. On Android, the output is a Compose `MaterialTheme` extension with `Colors`, `Typography`, `Shapes`, and `MotionTokens`. On iOS, the output is a Swift Package with `Color` extensions, `Font` factories, and `EdgeInsets` constants. The same token JSON is imported into Figma as Variables, allowing designers and engineers to reference the same names. The pipeline runs in CI; a PR that changes tokens regenerates both platforms' bindings and triggers visual-regression tests.

**Component Libraries**

The Compose component library lives in `core-design-system` as a Gradle module. Each component is a `@Composable` taking only tokens and content, never colours or sizes as parameters:

```kotlin
@Composable
fun PrimaryButton(
    label: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    enabled: Boolean = true,
) {
    Button(
        onClick = onClick,
        enabled = enabled,
        colors = ButtonDefaults.buttonColors(
            containerColor = MaterialTheme.colorScheme.primary,
        ),
        shape = AscendionShapes.medium,
        modifier = modifier,
    ) { Text(label, style = MaterialTheme.typography.labelLarge) }
}
```

The SwiftUI counterpart:

```swift
public struct PrimaryButton: View {
    let label: String
    let action: () -> Void

    public var body: some View {
        Button(action: action) {
            Text(label).font(.labelLarge).foregroundColor(.onPrimary)
        }
        .background(Color.primary)
        .cornerRadius(AscendionShape.medium)
    }
}
```

Both components consume only tokens; brand changes are token changes, not component edits.

**Dark Mode Implementation**

Android: `values-night/colors.xml` plus token-generated `darkColorScheme()`; `drawable-night/` for raster assets; vector icons tinted via `ColorFilter` from tokens. iOS: `Color.semantic` accessors that return `UIColor` initialised with `init(dynamicProvider:)` for light/dark variants; asset catalogue `Any Appearance` / `Dark Appearance` slots for raster assets; SF Symbols inherit automatically. Third-party SDKs (Google Maps `mapStyle`, WebView `prefers-color-scheme`) are explicitly themed in dark mode or flagged as a known gap.

**Figma to Code Pipeline**

The pipeline in CI: a designer commits a token change to the Figma file; Tokens Studio exports the JSON to a Git branch; CI validates the JSON against the W3C schema; Style Dictionary generates Compose and SwiftUI outputs; visual regression tests run against the generated themes; a PR is auto-opened with the diff for human review; merge regenerates the design-system package version. Designers see their changes in code within minutes; engineers see designer intent without translation loss.

---

## Implementation Guide

### Step 1: Define the token taxonomy

Decide the categories — colour (brand + semantic), typography (scale + weight + line height), spacing (4 or 8 point grid), elevation, shape, motion. Document each token's purpose in the design system spec.

### Step 2: Set up Style Dictionary and Tokens Studio

Token source of truth in JSON. Style Dictionary generates Compose `Theme` extension, SwiftUI `Color` and `Font` extensions, Figma Variables. CI pipeline runs on every token change.

### Step 3: Build the component library, component by component

Start with the highest-traffic components (Button, TextField, Card, AppBar, BottomSheet). Each component has a Compose Preview / SwiftUI Preview covering all states (default, pressed, disabled, focused). Components are versioned as a single design-system package.

### Step 4: Wire the dark-mode pipeline

Every colour token has a dark-mode variant. Every screen is reviewed in both modes per release. Third-party SDK UIs audited and either themed or flagged.

### Step 5: Establish the design-system governance team

A small team (1-3 engineers, 1-2 designers) owns the contract. Component requests follow a documented intake process; ad-hoc components in feature modules are flagged in code review.

### Step 6: Visual regression in CI

Paparazzi on Android (Compose preview rendered on JVM) and iOSSnapshotTestCase on iOS render each component in each state. Diffs against golden images fail the build. The team commits golden updates explicitly.

---

## Governance Checkpoints

| Checkpoint | Owner | Gate Criteria | Status |
|---|---|---|---|
| Token taxonomy ratified | Design Systems Lead | Categories named; each token has a documented purpose | Required |
| Style Dictionary pipeline live | Build Engineering | CI generates Compose and SwiftUI outputs from tokens on every change | Required |
| Component library v1 delivered | Design Systems Team | 15-20 highest-traffic components shipped with previews | Required |
| Dark-mode audit per release | QA + Design Systems | Every screen reviewed in light and dark per release; gaps tracked | Required |
| Visual regression in CI | Build Engineering | Paparazzi / SnapshotTestCase running on every PR | Required |
| Design system version bumped per breaking change | Design Systems Lead | Semantic version bump triggers consumer migration | Required |

---

## Security Considerations

- The design system's clipboard, share-sheet, and screenshot interactions must default to safe behaviours: sensitive fields (PINs, account numbers) opt out of clipboard auto-fill and screenshot capture.
- Third-party WebView UIs styled by the design system must inject CSP headers and disable JavaScript bridges by default — design-system-styled containers are not the same as design-system-safe containers.
- Asset bundles distributed by the design system are part of the supply chain; verify checksums and use lockfiles.

---

## Performance Considerations

- Compose recomposition: components consume tokens via `MaterialTheme.colorScheme.primary` (a snapshot read) rather than mutable globals; avoid passing colours as `Color` parameters when token references suffice (Compose is smarter about stability with tokens than with raw values).
- SwiftUI redraws: prefer `EnvironmentValues` for design-system context (theme, density, motion preferences) so child views read implicitly rather than being passed values that change identity.
- Vector icon rendering on Compose uses `ImageVector`; cache vectors at the design-system level via `rememberVectorPainter` to avoid re-parsing on each composition.
- Typography scale defined with explicit `lineHeight`; relying on the platform's default line height varies by font and OS version and produces inconsistent layout heights.

---

## Anti-Patterns to Avoid

### ⚠️ The Figma-Only Design System

Designers maintain a beautiful Figma library; engineers reimplement components from screenshots. The two truths drift; every release produces design-versus-engineering tickets. The fix is the token pipeline that makes Figma and code consume the same source.

### ⚠️ Pixel Literals in Components

A spacing of `16.dp` appears in 40 components; a brand decision to move to a 12-point grid requires touching every one. The fix is the token reference (`AscendionSpacing.md`) and the lint rule that fails the build on raw `.dp` / pixel values in design-system code.

### ⚠️ Dark Mode as a Colour Invert

Engineers swap white and black, ship the app, discover that elevations vanish, brand colours desaturate badly, and third-party widgets remain bright. The fix is the disciplined dark-mode token set with explicit values per token, audited per release.

### ⚠️ Component Inflation

Every feature team adds its own "slightly different" button to the design system. The component count grows from 30 to 200; nobody knows which button to use. The fix is the design-systems-team intake gate that says "no" by default and approves new components only with documented justification.

### ⚠️ Ignoring Dynamic Type

The iOS app's typography looks fine at the default size and breaks at `accessibilityExtraExtraExtraLarge`. App-Store accessibility reviewers flag it; older users cannot read it. The fix is the design-system requirement that every component is tested at all 12 Dynamic Type sizes, and CI fails the build on layout assertions broken by Dynamic Type scaling.

---

## AI Augmentation Extensions

### AI-Assisted Component Generation from Figma

Tools like Locofy, Anima, and Figma's own Dev Mode plus AI coding assistants generate Compose / SwiftUI code from Figma frames. The output is a starting point; the design-systems team integrates it into the token-driven architecture rather than accepting it verbatim.

### AI-Assisted Visual Regression Triage

Paparazzi / SnapshotTestCase produce diffs; AI classifies diffs as "expected change", "regression", or "needs human review" based on the PR context. The team's golden-update workflow accelerates without losing review rigour on suspicious diffs.

---

## References

1. [Material Design 3](https://m3.material.io/) — *m3.material.io*
2. [Apple Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/) — *developer.apple.com*
3. [W3C Design Tokens Community Group](https://www.w3.org/community/design-tokens/) — *w3.org*
4. [Style Dictionary by Amazon](https://amzn.github.io/style-dictionary/) — *amzn.github.io*
5. [Tokens Studio for Figma](https://tokens.studio/) — *tokens.studio*
6. [Now in Android — Design System Module](https://github.com/android/nowinandroid) — *github.com/android*
7. [Paparazzi — Android Snapshot Testing](https://github.com/cashapp/paparazzi) — *github.com/cashapp*
8. [SF Symbols](https://developer.apple.com/sf-symbols/) — *developer.apple.com*

---

*Last updated: 2026 | Maintained by: Ascendion Solutions Architecture Practice*
*Section: `technology/mobile/ui-design-systems/` | Aligned to Material 3 · Apple HIG · W3C Design Tokens*
