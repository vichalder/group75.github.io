# ZONE 1: FIXED INSTRUCTIONS (DO NOT MODIFY)

**Project Name:** Group 75 data visualisation website
**Tech Stack:** HTML on GitHub Pages

## Core Project Directives
> **CRITICAL:** All agents interacting with this repository must strictly adhere to the following behavioral and technical rules. Failure to comply will break the project architecture.

### YOU MUST ALWAYS:
1. Follow the theme of the rest of this project.
2. Create visually impressive front-ends.
3. Only generate standalone HTML files (CSS and JS must be embedded).
4. Update `index.html` to reflect new changes.
5. Update `README.md` to reflect the current file tree.

### YOU MUST NEVER:
1. Generate code that cannot be embedded directly in HTML. No external build steps, frameworks, or separated assets unless strictly required by a new, overriding prompt.
2. Pick a completely new theme for a page (besides changing the color scheme) unless explicitly told to do so.

---

# ZONE 2: DYNAMIC SECTIONS (AGENT WRITABLE)

## Context & State
*Agents: Update this section to reflect the current reality of the codebase so newly instantiated agents have immediate context.*

* **Current Primary Goal:** Develop and expand the SF Crime Analytics data visualisation website for Group 75
* **Latest Major Change:** Added `pages/larceny-story.html` — Data story "The Larceny Wave" with 3 embedded Chart.js visualisations (yearly bar chart, district risk horizontal bar, day×hour heatmap)
* **Known Architectural Quirks:**
  - CSS theme variables (`--bg`, `--accent`, `--text-primary`, etc.) are defined in the `<head>` of each standalone page — no shared stylesheet
  - The `interactive_plots/` directory holds raw Plotly/Folium HTML embeds; the `pages/` directory holds the styled wrapper pages that iframe or include them
  - All CSS and JS should generally be embedded inline — no external build steps or separated asset files.
  - Exception: `js/theme.js` is a shared asset used for the light/dark mode toggle across all pages.
  - Google Fonts (`Inter`) is loaded via `<link>` in `index.html` (this is an approved external resource)

## Execution Plan
*Agents: Move tasks through these stages as you work. Always mark your current task as "In-Progress".*

### 🔴 Pending
- [ ] No pending tasks — awaiting new instructions

### 🟡 In-Progress
- [ ] (none)

### 🟢 Completed
- [x] Created `index.html` landing page (SF Crime Analytics theme, dark background, blue accent)
- [x] Added `pages/interactive-hourly.html` — Crime by Category & Year line chart
- [x] Added `pages/interactive-heatmap.html` — Geographic Crime Heatmap (Folium embed)
- [x] Added `pages/interactive-risk.html` — Hourly Crime Patterns choropleth map
- [x] Added `pages/static-crime-ratio.html` — Crime Ratio by District (Matplotlib image)
- [x] Light/Dark mode toggle added to the site
- [x] Added `pages/interactive-heatmap-animated.html` — Animated Crime Heatmap wrapping `interactive_plots/crime_heatmap.html`
- [x] Added `pages/larceny-story.html` — Data story "The Larceny Wave" (Chart.js bar chart, horizontal bar, day×hour heatmap; red accent theme)

## Agent Hand-off Notes
*Agents: Use this scratchpad to document known bugs, blockers, context limitations, or specific instructions for the next agent that picks up the task.*

* **2026-03-24 - Claude Sonnet 4.6:** Added data story page "The Larceny Wave".
    * *Notes:* Created `pages/larceny-story.html` — fully self-contained narrative page with 3 Chart.js visualizations (annual timeseries bar chart, district risk ratio horizontal bar with reference line plugin, day×hour heatmap grid). Uses Chart.js 4.4.4 CDN. Red/crimson accent scheme (`--accent: #ef4444`). All data is embedded (extracted/approximated from notebook narrative). Theme-reactive charts via MutationObserver. Added crimson card to `index.html`. Updated nav in all 6 pages + `index.html`. Updated `README.md` and `agents.md`.
    * *Blockers:* None

* **2026-03-24 - Claude Sonnet 4.6:** Added animated heatmap page.
    * *Notes:* Created `pages/interactive-heatmap-animated.html` wrapping `interactive_plots/crime_heatmap.html` (Leaflet, year slider 2003–2025, crime-type dropdown). Added sky-blue card to `index.html`. Updated nav in all 5 pages + `index.html`.
    * *Blockers:* None

* **2026-03-17 - Claude Sonnet 4.6:** Initialised this file with current project state.
    * *Notes:* Project is a static GitHub Pages site. All pages follow a dark-mode-first design. The `AI_rulebook.md` file has been deleted (tracked as `D` in git status) — it has been superseded by this `agents.md` file.
    * *Blockers:* None