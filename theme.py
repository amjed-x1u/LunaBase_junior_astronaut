"""Spaceship-console theme for LunaBase (blue panels, black text, kid friendly)."""
import streamlit as st
from i18n import tr
from ui_html import css


def apply_theme(lang="en"):
    st.markdown(css(lang), unsafe_allow_html=True)


def how_to_play(lang="en"):
    with st.expander(tr(lang, "🎮 How to play (30 seconds)")):
        st.markdown(tr(lang, "1. **Pick 2 actions** each day (recycle water, make oxygen, grow food…).\n"
                             "2. Press **🌅 END DAY** — the crew uses resources and a surprise event happens.\n"
                             "3. Keep all 5 gauges above **0** for **7 days** to win. Watch the 🔗 chain-reaction warnings, "
                             "and on days 3 and 5 solve the **food mystery** with data!"))
