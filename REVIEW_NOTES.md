# LunaBase review notes

Review date: 15 November 2026 (updated after the drag & drop / autoplay-music fix pass)

## Automated checks performed

- Python compilation: all 38 source files passed.
- Unit tests: 133 unit/flow tests pass, plus 7 real-Chromium tests (music autoplay, drag & drop, phone layout) — see ADDITIONS_NOTES.md, section "Review & fix pass (2026-11-15)".
- Node.js syntax check: the custom Streamlit component bridge and generated scene script passed.
- Source inspection: app entry point, mission engine, NASA data fetcher, greenhouse data/model, theme, panels, translations, and deployment documentation.

## Corrections included in this review package

1. Replaced the stale, contradictory README history with a single current description of the shipped prototype and its current validation status.
2. Added the NASA OSDR study record (OSD-895 / ALSDA LSDS-160) and dataset DOI alongside the EDEN ISS publication DOI.
3. Clarified that the current crop-yield constants are transcribed from the published paper; the app does not download or parse OSD-895 archive files at runtime.
4. Clarified in the NASA tab that live DONKI flare observations are informational and do not alter the simulator's separate randomized solar-storm events.
5. Updated the deployment checklist to include the OSDR study citation and corrected the folder name used in deployment instructions.
6. Removed Python cache files from this review ZIP.

## Remaining checks before submission

- Install the dependencies from `requirements.txt` and run `streamlit run app.py`.
- Test the complete player journey in a real browser: welcome, language switch, all four scenes, drag/drop interactions, actions, end-day, food challenge, greenhouse, science missions, emergency drills, NASA lookup, quiz, report download, and certificate download.
- Check layout and touch behavior on at least one phone and one desktop browser, especially Arabic RTL, small screens, scrolling, and the nested scene iframe.
- Test the NASA DONKI button both online and offline, and verify deployment secrets are not committed.
- Confirm the public deployment and GitHub repository are accessible without login.
- Confirm project-page content, challenge selection, team registration, AI-tool disclosure, and submission deadline against the current official participant instructions.

## Important scientific limitations

- EDEN ISS is an Antarctic space-greenhouse analog, not a lunar greenhouse.
- Several simulation quantities (bed area, energy/water use, resource conversions, care effects, and climate thresholds) are explicitly game assumptions, not measured EDEN ISS or lunar engineering data.
- The live DONKI display is not yet connected to game-state calculations.
- The prototype is not an official NASA product and its emergency/landing activities are educational only.
