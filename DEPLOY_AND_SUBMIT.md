# Publish and submit LunaBase (NASA Space Apps 2026)

## 1. Before you submit - be honest about the timeline
Space Apps rules say teams must not start work on a challenge before the hackathon (Nov 14-15, 2026).
Fill in and keep this note in your submission (do NOT claim approval you do not have):

- Date work on this project started: ____________
- What existed before Nov 14 (code / ideas): ____________
- Local Lead / organizer asked on: ______ ; their written answer: ____________
- What was built or changed during the hackathon: ____________

If the organizers say pre-built work is not allowed, rebuild or substantially extend it during the event and say so.

## 2. Minors
Anyone under 18 must be registered by a parent/guardian and accompanied during the event.
Do not show recognizable names, voices or faces of under-18s in videos or the project page.

## 3. Publish on Streamlit Community Cloud (free)
1. Create a GitHub repository and upload the contents of the extracted `LunaBase_phase1` folder to the repository root (keep `app.py`, `theme.py`, `.streamlit/config.toml`, `requirements.txt`).
2. Go to https://share.streamlit.io , sign in with GitHub, click **Create app**.
3. Choose the repo, branch `main`, main file `app.py`, then **Deploy**.
4. (Optional) In **Advanced settings > Secrets** add: `NASA_API_KEY = "your-free-key"`
   (get one at https://api.nasa.gov). Without it the app uses DEMO_KEY, which is rate-limited.
5. Open the public link on a phone and a laptop and play one full mission.

## 3b. Run locally
```
py -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
streamlit run app.py
```

## 4. Submission checklist (on spaceappschallenge.org, team project page)
- [ ] Correct challenge selected: Build a Junior Astronaut Mission Trainer
- [ ] Public app link works without login
- [ ] Public GitHub link + this README
- [ ] Sources listed: NASA DONKI (api.nasa.gov), NASA OSDR study OSD-895 (dataset DOI 10.26030/8556-mr78), and EDEN ISS paper (DOI 10.3389/fpls.2020.00656)
- [ ] Clear statement: values are simplified, not real NASA mission data; not an official NASA product
- [ ] Timeline note from section 1
- [ ] Follow the official Project Submission Guide (published Nov 13) for exact fields, video and file limits
- [ ] If you used AI tools to help build it, check the Terms & Conditions for what you must disclose

## 5. 3-minute demo script
1. (20s) Problem: space STEM is either too simple or too hard for kids.
2. (40s) Play 2 days: pick actions, end day, show a chain reaction warning (low energy -> oxygen/water drop).
3. (40s) Day 3 food alert: read the data table, find the cause, apply the fix.
4. (30s) Greenhouse: real EDEN ISS yields, shared energy/water.
5. (20s) Click "Load latest solar flares" to show live NASA data.
6. (30s) Learning center, quiz, downloadable mission report.
