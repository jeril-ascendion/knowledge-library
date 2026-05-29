# Mobile Accessibility

WCAG 2.2 Level AA compliance — TalkBack and VoiceOver semantics, Dynamic Type and scalable text, 48 dp / 44 pt touch targets, 4.5:1 colour contrast, the legal regime that makes accessibility a binding requirement, and the automated tools that catch the easy cases before users do.

**Section:** `technology/mobile/` | **Subsection:** `accessibility/`
**Alignment:** WCAG 2.2 Level AA | ADA Title III | EN 301 549 | RA 10524 (Philippines) | Apple Accessibility | Android Accessibility
**Audience:** Mobile Engineers · UX Engineers · Compliance Officers

---

## Overview

Mobile accessibility in 2026 is a regulated discipline, not a charitable one. The 2019 US Supreme Court decision in *Robles v. Domino's Pizza* established that mobile apps are subject to ADA Title III, opening US enterprises to lawsuits for accessibility failures. The EU's EN 301 549 standard, derived from WCAG, is mandatory for public-sector apps and increasingly for private-sector consumer apps under the European Accessibility Act (in force June 2025). The Philippines' Republic Act 10524 mandates accessible digital services for government interactions. Compliance is no longer optional; the only question is whether the team builds accessibility in or pays for it under legal pressure later.

WCAG 2.2 Level AA is the practical compliance target for enterprise applications — Level A is too weak (essential failures are AA-only requirements like 4.5:1 contrast, resize text to 200 percent, dragging movements alternative). Level AAA is too costly to achieve uniformly. AA is the negotiated middle. Apple's accessibility stack (VoiceOver, Dynamic Type, Switch Control, Voice Control) and Android's accessibility stack (TalkBack, Accessibility Scanner, Switch Access) implement WCAG-aligned platform semantics; the mobile engineer's job is to expose the right semantics and to test against the assistive technology.

The architectural shift is not "we made it accessible." It is: **mobile accessibility is a WCAG 2.2 Level AA discipline with platform-specific implementations (TalkBack / VoiceOver semantics, Dynamic Type, scalable text, touch-target sizing, contrast ratios) baked into the design system, validated by automated scanners on every release, and tested with real assistive technology by a real screen-reader user before any major release.**

---

## Core Principles

### 1. Accessibility is built into the design system, not bolted on

Every design-system component ships with accessibility semantics: `contentDescription` on icons, `accessibilityLabel` on SwiftUI views, semantic roles on buttons, focus order, group semantics. The feature engineer composes accessible components; bespoke accessibility per screen does not scale.

### 2. Touch targets meet platform minima

48 dp by 48 dp on Android (Material 3 guidance); 44 pt by 44 pt on iOS (HIG guidance). Targets below the minimum fail accessibility scanners; targets at the minimum are usable by users with motor impairments. Visible bounds may be smaller; touch bounds match the minimum.

### 3. Text scales with the user's preference

`sp` units on Android (text scales with the user's font-size preference); `Font.body`, `Font.title`, etc. on iOS (text honours Dynamic Type). Hardcoded `dp` on Android text or fixed point sizes on iOS break accessibility and break the layout when scaled.

### 4. Colour is never the only signal

A red error border without an icon, an "approved" badge with no label, a chart that uses red and green to distinguish series — all fail users with colour blindness (8 percent of men). Pair every colour with a redundant signal: icon, label, pattern.

### 5. Screen-reader announcements are intentional

VoiceOver and TalkBack speak the screen left-to-right top-to-bottom by default. Custom announcements (`accessibilityLiveRegion` on Android, `AccessibilityNotification.Announcement` on iOS) for dynamic content updates. Focus management on navigation transitions (announce the new screen name, focus the first meaningful element).

### 6. Test with real assistive technology, not only with scanners

Accessibility Scanner on Android and Accessibility Inspector on iOS catch programmatic issues — missing labels, contrast violations, target size. They do not catch experiential issues — bad reading order, confusing announcements, focus traps. A screen-reader-using tester (internal employee, contracted user, accessibility consultancy) catches what scanners cannot.

---

## Architecture Deep-Dive

**Android — TalkBack Semantics**

TalkBack reads the UI through the AccessibilityService API. Compose exposes semantics via the `semantics { }` modifier:

```kotlin
IconButton(
    onClick = onFavourite,
    modifier = Modifier.semantics {
        contentDescription = if (isFavourite) "Remove from favourites" else "Add to favourites"
        role = Role.Button
        stateDescription = if (isFavourite) "On" else "Off"
    }
) {
    Icon(if (isFavourite) Icons.Filled.Favorite else Icons.Outlined.FavoriteBorder, contentDescription = null)
}
```

Note the inner `Icon` has `contentDescription = null` — the parent IconButton owns the semantics. Setting both produces double announcements.

`accessibilityTraversalBefore` and `accessibilityTraversalAfter` adjust the focus order when the visual layout does not match the intended reading order. Live regions announce dynamic content changes — toast messages, validation errors — without requiring focus.

**iOS — VoiceOver Semantics**

```swift
Image(systemName: heartSymbol)
    .accessibilityLabel(isFavourite ? "Remove from favourites" : "Add to favourites")
    .accessibilityAddTraits(.isButton)
    .accessibilityValue(isFavourite ? "On" : "Off")
```

`accessibilityLabel` is the spoken label; `accessibilityHint` is the longer description; `accessibilityValue` communicates state; `accessibilityTraits` describes the element kind. SF Symbols have accessible names built in; custom icons require explicit labels.

`UIAccessibility.post(notification: .announcement, argument: "Transfer complete")` produces a one-off announcement; `.screenChanged` notifies VoiceOver of a navigation event.

**Dynamic Type on iOS**

```swift
Text("Account balance")
    .font(.headline)
    .dynamicTypeSize(.medium ... .accessibility3)
Text("$1,234.56")
    .font(.title)
    .minimumScaleFactor(0.5)
```

`font(.headline)`, `.title`, `.body` etc. honour Dynamic Type automatically. The `dynamicTypeSize` modifier clamps the range — at very large accessibility sizes, some content may need to truncate or scale. `minimumScaleFactor` allows the text to shrink rather than truncate.

Test at all five accessibility extra-large sizes — accessibilityMedium through accessibility5 — in SwiftUI Previews or in the simulator with the Accessibility Inspector's Dynamic Type slider. Layouts that work at default sizes routinely break at accessibility5.

**Android — Scalable Text**

`sp` (scale-independent pixels) units honour the user's text-size preference. Use `sp` for every Text composable; `dp` is reserved for non-text dimensions. The user's setting can go up to 200 percent on Android 14 and beyond; layouts must handle this gracefully.

**Touch Targets**

Compose:

```kotlin
IconButton(onClick = onClick, modifier = Modifier.size(48.dp)) { ... }
```

`IconButton` defaults to 48 dp; do not shrink it below. For non-IconButton interactables, ensure the `Modifier.size(48.dp)` or `Modifier.minimumInteractiveComponentSize()`.

SwiftUI:

```swift
Button(action: {}) { Image(systemName: "heart") }
    .frame(minWidth: 44, minHeight: 44)
```

Apple's HIG specifies 44 by 44; the `frame` modifier enforces.

**Colour Contrast**

WCAG 2.2 AA requires 4.5:1 contrast for normal text (under 18 pt or under 14 pt bold), 3:1 for large text. UI components and graphical objects require 3:1. Tools: Colour Contrast Analyser (free, Android and iOS), Stark for Figma, Polypane for design-system audits. The design-system colour tokens must be vetted for AA compliance before being committed.

**Legal Regime**

- **US — ADA Title III**: *Robles v. Domino's Pizza* (9th Circuit 2019) and the Domino's settlement established that mobile apps providing access to public-accommodation services are subject to ADA. Lawsuits target inaccessible mobile apps at consumer-facing US enterprises; settlements range from $50,000 to seven figures.
- **EU — EN 301 549 / European Accessibility Act**: Mandatory for public sector since 2018; mandatory for private sector consumer apps in scope (banking, e-commerce, transport, telecoms) since June 2025.
- **Philippines — RA 10524**: Section 32A requires accessibility for government digital services; consumer requirements emerging through DICT regulations.
- **UK — Equality Act 2010**: Equivalent to ADA; private enforcement via the Equality Advisory and Support Service.
- **Canada — Accessible Canada Act**: Federally regulated entities (banking, telecoms, transport) subject to escalating accessibility standards through 2040.

**Automated Tools**

- **Accessibility Scanner** (Google, Android): scan a screen, get a report — missing labels, low contrast, small touch targets.
- **Accessibility Inspector** (Apple, iOS / macOS): live inspection plus automated audit; integrates with Xcode.
- **Espresso Accessibility Checks**: enable via `AccessibilityChecks.enable()` in instrumented tests; failures break the build.
- **XCUITest accessibility audit**: `app.performAccessibilityAudit()` in Xcode 15+; failures break the build.

---

## Implementation Guide

### Step 1: Audit the current state with platform scanners

Run Accessibility Scanner on every Android screen; Accessibility Inspector on every iOS screen. Document violations as tickets prioritised by severity.

### Step 2: Bake semantics into the design system

Every Button, IconButton, TextField, Card, BottomSheet, AppBar in the design system has documented accessibility behaviour. Component previews include accessibility variants.

### Step 3: Enforce automated checks in CI

Espresso Accessibility Checks on Android; XCUITest accessibility audit on iOS. PRs that introduce violations fail the build.

### Step 4: Test with Dynamic Type and font-size scaling

Every screen tested at the five accessibility extra-large sizes. SwiftUI Previews parameterise over Dynamic Type; Android XML preview supports font scaling.

### Step 5: Engage real screen-reader testing

A contracted screen-reader user or internal employee tests every release on TalkBack and VoiceOver. Findings documented; remediated before release.

### Step 6: Train the team

Engineers shadow a screen-reader user once per quarter. The empathy is the engineering input that scanners cannot provide.

---

## Governance Checkpoints

| Checkpoint | Owner | Gate Criteria | Status |
|---|---|---|---|
| WCAG 2.2 AA control matrix | Accessibility Lead | Each AA success criterion has documented mobile implementation | Required |
| Design-system component a11y | Design Systems Lead | Every component has semantics and Dynamic Type behaviour ratified | Required |
| Automated accessibility CI | Build Engineering | Espresso a11y checks and XCUITest audit running and gating | Required |
| Dynamic Type / font-scale testing | QA Lead | Per-release screen audit at accessibility extra-large sizes | Required |
| Screen-reader testing | QA + Accessibility | Real assistive-technology user tests per release | Required |
| Legal compliance attestation | Compliance Officer | Annual attestation against ADA / EAA / RA 10524 as applicable | Required |

---

## Security Considerations

- VoiceOver and TalkBack can speak sensitive content (passwords, OTPs); ensure `accessibilityLabel` on password fields says "password" not the actual content; iOS UITextField with `isSecureTextEntry` handles this automatically.
- Custom accessibility actions can introduce unexpected paths into sensitive flows; review the custom-action surface against threat models.
- Accessibility services on Android run with elevated permissions; do not test app builds with arbitrary accessibility services installed.

---

## Performance Considerations

- Accessibility semantics are evaluated on every focus change; nesting deep semantic trees causes TalkBack and VoiceOver to lag. Flat semantic trees announce faster.
- Dynamic Type layout recomputation happens on every text-size preference change; layouts that re-compute heavily can drop frames. Pre-compute where appropriate.
- Espresso accessibility checks add 5-10 ms per test; XCUITest audits add 200-500 ms per test; budget the additional CI time.

---

## Anti-Patterns to Avoid

### ⚠️ Hardcoded Text Sizes Bypass Dynamic Type

Engineers use `.font(.system(size: 14))` because "the design says 14 pt." Users at accessibility5 see 14-pt text everywhere; the design fails. The fix is `Font.body`, `Font.title`, etc., and the lint rule that flags raw `.system(size:)` calls in feature code.

### ⚠️ Decorative Icons Without `contentDescription = null`

An icon next to a text label has its own contentDescription; TalkBack reads the label, the icon's description, and the label again. The fix is the convention that decorative icons inside a labelled parent have `contentDescription = null` (Android) or `accessibilityHidden(true)` (iOS).

### ⚠️ Touch Targets Below 48 dp / 44 pt

A close-button icon is 24 dp because "it looks better." The user with motor impairment cannot reliably tap it. The fix is the design-system rule that interactable surfaces are 48 dp / 44 pt minimum regardless of visual icon size — the visible icon is centred in a touch target that meets the minimum.

### ⚠️ Colour as the Only Signal

A status badge is green for "approved" and red for "rejected" with no label or icon. Colour-blind users cannot distinguish. The fix is paired-signal discipline in the design system: every status colour has an accompanying label and / or icon.

### ⚠️ Skipping the Real-User Test

Scanners pass; the team ships; the screen-reader user discovers a focus trap on the checkout screen. Cart-conversion rates drop measurably among VoiceOver users. The fix is the budget line for real-user accessibility testing per release, treated as non-optional.

---

## AI Augmentation Extensions

### AI-Assisted Accessibility Label Generation

LLM coding assistants generate `contentDescription` and `accessibilityLabel` text from component context — IconButton with a heart icon gets "Add to favourites" or "Remove from favourites" depending on state. The engineer reviews and accepts; the typing is compressed.

### AI-Assisted A11y Audit Triage

Scanner output (hundreds of findings on legacy codebases) is triaged by an LLM that classifies by remediation effort, business impact, and screen criticality. The accessibility team's backlog is prioritised meaningfully rather than alphabetically.

---

## References

1. [WCAG 2.2 Guidelines](https://www.w3.org/TR/WCAG22/) — *w3.org*
2. [Android Accessibility — Build Accessible Apps](https://developer.android.com/guide/topics/ui/accessibility) — *developer.android.com*
3. [Apple Accessibility — App Development](https://developer.apple.com/accessibility/) — *developer.apple.com*
4. [Robles v. Domino's Pizza — 9th Circuit](https://cdn.ca9.uscourts.gov/datastore/opinions/2019/01/15/17-55504.pdf) — *uscourts.gov*
5. [EN 301 549 — European Accessibility Standard](https://www.etsi.org/standards) — *etsi.org*
6. [Accessibility Scanner — Google](https://support.google.com/accessibility/android/answer/6376570) — *support.google.com*
7. [Accessibility Inspector — Apple Xcode](https://developer.apple.com/documentation/accessibility/accessibility-inspector) — *developer.apple.com*
8. [SF Symbols — Accessible Icon Library](https://developer.apple.com/sf-symbols/) — *developer.apple.com*

---

*Last updated: 2026 | Maintained by: Ascendion Solutions Architecture Practice*
*Section: `technology/mobile/accessibility/` | Aligned to WCAG 2.2 AA · ADA · EN 301 549 · RA 10524*
