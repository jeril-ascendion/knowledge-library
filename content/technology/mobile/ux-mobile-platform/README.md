# UX and Mobile Platform Considerations

> **Section:** `technology/mobile/ux-mobile-platform/`
> **Alignment:** Apple Human Interface Guidelines | Google Material Design 3 | WCAG 2.2 | Nielsen Norman Group
> **Audience:** Mobile Engineers · UI/UX Designers · Architects · Product Managers

Mobile user experience is constrained by physical realities that web experience is not: a 5-6 inch screen, a glass interface operated by a finger (not a precision mouse pointer), ambient lighting conditions ranging from bright sunlight to darkness, one-handed operation scenarios, and users who are moving, distracted, or operating under time pressure. Platform-native UX guidelines from Apple and Google encode decades of research into these constraints. Engineering them correctly requires understanding the guidelines, the platform mechanisms that implement them, and the accessibility layer that makes them inclusive.

## Overview

UX and platform considerations span five domains: design system implementation (translating design tokens and component specifications into platform code), platform-native interaction patterns (following the conventions each platform's users expect), accessibility implementation (making the application usable by users with diverse abilities), motion and animation (using platform-appropriate animation curves and durations), and localisation (adapting layout, typography, and content for different languages and cultures).

## Design System Implementation

Design tokens are the canonical source of design decisions: colour, typography, spacing, elevation, and shape are defined once as platform-agnostic JSON and transformed to Android resource values (XML color, dimen, style files) and iOS Swift constants using Style Dictionary. A design token change propagates to all platforms and components automatically — no manual colour hunting.

Material Design 3 on Android: dynamic colour (Monet algorithm extracts five key colours from the device wallpaper and generates a harmonious 20-colour palette), colour roles (primary, on-primary, primary-container, secondary, tertiary, error, surface, outline), elevation as tonal colour overlay (not drop shadow). Compose Material3 library implements all tokens and components — do not re-implement Button, TextField, Scaffold, or NavigationBar.

Apple Human Interface Guidelines on iOS: SF Symbols (6000+ symbols with monochrome, hierarchical, palette, and multicolour rendering modes; support all Dynamic Type sizes automatically), semantic colours (`UIColor.label` adapts to light/dark mode without code change), Safe Area insets required on all screens for notch, Dynamic Island, and home indicator.

## Platform-Native Interaction Patterns

Users build muscle memory for the interaction patterns of their platform. Violating these patterns causes frustration even when the application is functionally correct. Critical patterns:

Android: predictive back gesture (Android 14+), bottom navigation for top-level navigation with 3-5 destinations, FAB for primary actions, bottom sheets for secondary options, swipe-to-dismiss on list items. Navigation Compose manages the back stack and transition animations correctly.

iOS: swipe-from-left-edge to go back (all modal and push navigation), tab bar for top-level navigation, pull-to-refresh on scrollable content, swipe actions on list rows, system context menus on long press. SwiftUI NavigationStack manages back navigation automatically with the correct animation.

## Accessibility Implementation

Accessibility is a legal requirement in regulated markets (ADA Title III, Philippines RA 10524) and an ethical obligation across all markets. Implementation requires testing, not just implementation — enable TalkBack (Android) and VoiceOver (iOS) and navigate the complete critical user journey with screen closed before each release.

Key implementation details: every interactive element has a meaningful `contentDescription` (Android) or `accessibilityLabel` (iOS) that describes its action, not its appearance. "Green button" is not a label. "Add to cart" is a label. Dynamic Type: all text uses semantic text styles (`Font.body`, `Font.headline`) not hardcoded sizes. Test at AX3 and AX5 size categories — text must not be clipped or truncated. Touch targets: minimum 48×48dp (Android), 44×44pt (iOS). Colour contrast: 4.5:1 ratio for normal text, verified with Colour Contrast Analyser tool.

## Anti-Patterns to Avoid

> **⚠ Hardcoded Colours and Sizes** — `Color(0xFF1E3A5F)` in Compose, `UIColor(red: 0.12, green: 0.23, blue: 0.37, alpha: 1.0)` in UIKit. Breaks dark mode, breaks dynamic colour, impossible to update globally.
> **CORRECT:** All colours from design tokens — `MaterialTheme.colorScheme.primary` in Compose, `UIColor.label` or named colour assets in iOS. All text sizes from semantic styles — `MaterialTheme.typography.bodyLarge`, `Font.body`.

> **⚠ Ignoring Dynamic Type** — All text displayed at fixed 16pt size. Users who set Large Text in Accessibility settings (affecting approximately 12% of iOS users) see unsized text that overflows its containers.
> **CORRECT:** Use semantic text styles exclusively. Test at all 12 Dynamic Type size categories. Layout must accommodate text that is 3× the default size at AX5.

## References

1. Apple — Human Interface Guidelines. developer.apple.com/design/human-interface-guidelines
2. Google — Material Design 3. m3.material.io
3. W3C — WCAG 2.2. w3.org/TR/WCAG22
4. Google — Compose Accessibility. developer.android.com/jetpack/compose/accessibility
5. Apple — Accessibility Developer Resources. developer.apple.com/accessibility
