---
version: alpha
name: FastAPIGuide
description: A documentation tutor with a source-attributed, copyable Python snippet card.
omitted:
  - section: colors
    reason: Streamlit's built-in theme owns all surface, text, border, and focus colors.
  - section: typography
    reason: Streamlit owns sans-serif interface and monospace code typography.
  - section: rounded
    reason: Native Streamlit widgets own their geometry.
  - section: spacing
    reason: Native Streamlit wide layout and vertical blocks own spacing.
  - section: components
    reason: Streamlit components are used without independent styling overrides.
---

# FastAPIGuide design context

## Overview

This English-language product helps Python beginners learn FastAPI from
official documentation. The teacher's Day 10 feedback is the feature brief:
replace the unrelated scheme-profile UI with a copyable code card and source
attribution. Its signature is a real tutorial source file next to the example,
so learners can connect an answer to runnable code. Preserve the existing chat
workflow and Streamlit visual identity; do not introduce a landing-page redesign.

## Colors

Runtime ownership is Streamlit's theme. Both tabs consume native widgets;
this document introduces no manually duplicated color tokens or CSS adapters.

## Typography

Use native headings/captions for hierarchy and st.code for Python. Never render
retrieved text as unsafe HTML. Preserve complete code and source paths.

## Layout

One wide page, with Documentation chat and Snippet card tabs. Content scrolls
naturally on phones. No fixed-height shell or clipped actions. Only the small
bundled topic list is rendered; chat state remains session-local by design.

## Elevation & Depth

Use Streamlit's bordered container for the source/code card, without shadows.

## Shapes

Delegate widget and container radius to Streamlit.

## Components

- Tabs, radio groups and the labeled selectbox use Streamlit's existing
  accessible primitives and keyboard behavior; popup geometry is framework-owned.
- Copy is Streamlit's code-block copy action. Downloads use st.download_button.
  Docs and source navigation use st.link_button with explicit action labels.
- Latest cited docs shows only matching examples for the latest assistant reply.
  Browsing is explicitly labeled as browsing, not a citation.
- Missing catalog and absent citations have inline recovery instructions.
- Chat citations and thumbs feedback keep their existing behavior.
- Motion, focus, hover and disabled states remain framework-owned.

## Do's and Don'ts

- Keep source code pinned to an upstream revision and include its license.
- Verify desktop, narrow-screen, select, copy/download and empty/error states.
- Do not substitute unrelated code for an unsupported citation.
- Do not mix government-scheme eligibility into this FastAPI tutor.
