# LunaBase — Junior Astronaut Mission Trainer

LunaBase is a bilingual (English/Arabic) educational lunar-outpost simulator built with Python and Streamlit. Players manage a seven-day mission by balancing water, oxygen, energy, food, and radiation protection while completing science and safety activities.

## NASA Space Apps Challenge 2026

**Selected challenge:** [Build a Junior Astronaut Mission Trainer](https://www.spaceappschallenge.org/2026/challenges/junior-astronaut-mission-trainer/)

The challenge asks for an interactive game or app that lets students operate a lunar or Martian outpost and experience trade-offs involving life support, radiation shielding, power, and food production. LunaBase addresses those systems through connected resource decisions, short learning activities, and an explorable lunar-base scene.

## Run on Windows

1. Extract the ZIP file to a folder (the folder name may contain spaces).
2. Open the extracted folder.
3. Double-click **RUN_LUNABASE.bat**. It launches Streamlit using the correct quoted path.

If this is the first run and dependencies are not installed, open a terminal in `LunaBase_phase1` and run:

```bat
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

If you run from another directory, quote the full path to `app.py`, for example:

```bat
python -m streamlit run "C:\Users\Dell\OneDrive\Desktop\LunaBase V1.0\LunaBase_phase1\app.py"
```

## What the prototype includes

- Seven-day lunar-base resource-management game with Easy, Normal, and Hard difficulty.
- Five linked resource gauges, two actions per day, random educational events, and a rule-based Mission Coach.
- Four responsive 2.5D scenes (exterior, habitat, emergency, rover) with touch/mouse drag interactions.
- Greenhouse mission connected to base energy, water, food, and oxygen.
- EDEN ISS crop-yield reference values and greenhouse operating context (see **Scientific data and assumptions**).
- Adjustable greenhouse temperature, humidity, light-period, and nutrient-solution pH controls.
- Surface-science activities, assessed emergency drills, learning cards, quiz, mission report, and educational certificate.
- Live NASA DONKI solar-flare lookup, with an offline-friendly fallback.
- English and Arabic interface, including right-to-left presentation.

## Scientific data and assumptions

### EDEN ISS

The greenhouse crop rates and environmental context are transcribed into `simulation/eden_iss_data.py` from the published EDEN ISS 2018 experiment paper:

Zabel, P., Zeidler, C., Vrakking, V., Dorn, M., & Schubert, D. (2020). *Biomass Production of the EDEN ISS Space Greenhouse in Antarctica During the 2018 Experiment Phase*. Frontiers in Plant Science, 11, 656. https://doi.org/10.3389/fpls.2020.00656

The corresponding NASA Open Science Data Repository (OSDR) study is **OSD-895** (ALSDA ID **LSDS-160**): [NASA OSDR — OSD-895](https://osdr.nasa.gov/bio/repo/data/studies/OSD-895). Its record lists the study metadata and supplementary PDF. Dataset DOI: https://doi.org/10.26030/8556-mr78.

**Important distinction:** the current prototype uses values manually transcribed from the published paper's tables; it does not download, parse, or query the OSD-895 archive files at runtime. The paper is the direct source for the crop-yield values in the code. The NASA OSDR record is included as the corresponding repository record.

### NASA space-weather data

The NASA tab can request recent solar-flare observations from NASA DONKI through https://api.nasa.gov. The live DONKI feed is shown as contextual learning data; it does **not** currently drive the simulator's random solar-storm events or change game resources. The game event is a simplified educational mechanic.

### Model limitations

- EDEN ISS was an Antarctic space-greenhouse analog, not a lunar greenhouse.
- Bed areas, resource costs/returns, food-point conversion, care multipliers, and greenhouse climate target ranges are simplified game assumptions.
- The climate-control ranges are teaching thresholds, not validated lunar-agriculture engineering limits.
- The game does not claim that newly planted crops mature into fruit within seven days.
- Lunar landing, ice investigation, and emergency activities are educational exercises, not operational procedures or certifications.
- LunaBase is an independent educational prototype and is **not an official NASA product**.

## Run locally

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

python -m pip install -r requirements.txt
streamlit run app.py
```

Open the local URL printed by Streamlit (normally http://localhost:8501).

To increase NASA API rate limits, set `NASA_API_KEY` in the environment or Streamlit secrets. Without it, the app uses NASA's `DEMO_KEY`, which is rate-limited. The app continues to work when NASA's service is unavailable.

## Run automated tests

```bash
python -m unittest discover -s tests -v
```

Latest archive validation:
- **115/115 automated unit tests passed.**
- All 38 Python source files passed Python compilation.
- The standalone custom-component bridge JavaScript and generated scene JavaScript passed Node.js syntax checks.
- A live Streamlit server and end-to-end browser/device test were **not** run in the review environment because Streamlit was not installed. Run the app locally and test it on desktop and mobile before submission.

## Project structure

```text
LunaBase_phase1/
├── app.py
├── panels.py
├── theme.py
├── ui_html.py
├── scene_explorer.py
├── scene_component/
├── simulation/
│   ├── game_engine.py
│   ├── life_support.py
│   ├── greenhouse_mission.py
│   ├── greenhouse_link.py
│   ├── greenhouse_controls.py
│   ├── eden_iss_data.py
│   └── nasa_data.py
├── education/
├── ai/
├── tests/
├── requirements.txt
└── DEPLOY_AND_SUBMIT.md
```

## Submission checklist

See [DEPLOY_AND_SUBMIT.md](DEPLOY_AND_SUBMIT.md) for deployment steps, the final submission checklist, and a short demo outline. Confirm the public app and source-code links, cite all data sources, disclose any AI assistance as required by the current Terms & Conditions, and accurately describe when the work was created.
