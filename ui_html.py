"""Pure HTML/CSS helpers for the spaceship-console look (no Streamlit import, so they are unit-testable)."""
import html
import math

from i18n import is_rtl, tr

CSS = """
<style>
:root{--blue:#1E6FF0;--deep:#0B5ED7;--ice:#CFE6FF;--sky:#EAF4FF;--yellow:#FFD84D}
html,body,[class*="css"],.stApp{font-family:'Trebuchet MS','Segoe UI',Arial,sans-serif!important;font-size:18px}
/* every text is black */
.stApp,.stApp p,.stApp li,.stApp span,.stApp label,.stApp div,.stApp h1,.stApp h2,.stApp h3,.stApp summary,.stApp button,
.stApp [data-testid="stMarkdownContainer"] *,.stApp [data-testid="stCaptionContainer"] *,.stApp [data-testid="stMetric"] *,
.stApp [data-testid="stAlert"] *{color:#000!important}
.stApp{background:linear-gradient(rgba(30,111,240,.08) 1px,transparent 1px) 0 0/30px 30px,
 linear-gradient(90deg,rgba(30,111,240,.08) 1px,transparent 1px) 0 0/30px 30px,
 linear-gradient(180deg,#A9D3FF 0,#CFE6FF 320px,#EAF4FF 100%)}
.block-container{max-width:1180px;padding-top:1rem}
[data-testid="stHeader"]{background:transparent}
/* header console */
.lb-header{position:relative;padding:16px 26px;border-radius:24px;border:4px solid var(--blue);
 background:linear-gradient(120deg,#8CC8FF,#CFE6FF 55%,#EAF4FF);box-shadow:0 0 0 4px #fff,0 10px 24px rgba(11,42,85,.25)}
.lb-header::before,.lb-header::after{content:"";position:absolute;top:10px;width:10px;height:10px;border-radius:50%;background:var(--blue);box-shadow:inset 0 0 0 2px #fff}
.lb-header::before{left:12px}.lb-header::after{right:12px}
.lb-brand{font-size:1.9rem;font-weight:800;letter-spacing:.08em}.lb-brand small{font-size:.95rem;letter-spacing:.2em;margin-left:6px}
.lb-hrow{display:flex;flex-wrap:wrap;gap:12px 34px;margin-top:8px}
.lb-label{font-size:.75rem;font-weight:800;letter-spacing:.14em}
.led{display:inline-block;width:18px;height:18px;border-radius:50%;border:2px solid #000;margin:4px 6px 0 0;background:#fff}
.led.done{background:var(--blue)}.led.now{background:var(--yellow);animation:blink 1.2s ease-in-out infinite}.led.fail{background:#E5484D}
@keyframes blink{50%{box-shadow:0 0 10px 4px rgba(255,216,77,.9)}}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
/* panels */
[class*="st-key-panel_"]{background:linear-gradient(180deg,#fff,var(--sky));border:4px solid var(--blue)!important;border-radius:22px;
 box-shadow:0 0 0 4px var(--ice),0 10px 22px rgba(11,42,85,.16);padding:14px 18px}
.lb-title{display:inline-block;background:#FFE066;border:2px solid #000;border-radius:8px;padding:2px 12px;font-weight:800;letter-spacing:.1em;margin-bottom:8px}
/* gauges */
.lb-gauges{display:flex;flex-wrap:wrap;gap:12px;justify-content:space-around}
.lb-gauge{text-align:center;min-width:128px;flex:1;background:#fff;border:3px solid var(--ice);border-radius:20px;padding:8px 6px;transition:transform .15s,border-color .15s}
.lb-gauge:hover{transform:translateY(-4px) scale(1.03);border-color:var(--blue)}
.lb-gauge .g-name{font-weight:800;font-size:.95rem;margin:2px 0 4px}
.lb-chip{display:inline-block;padding:2px 12px;border-radius:999px;font-weight:800;font-size:.85rem;border:2px solid #000}
.lb-ok{background:#BFF0D4}.lb-warn{background:#FFE9A6}.lb-bad{background:#FFC2C4}
/* screens */
.lb-screen{background:#E3F7FF;border:3px solid #000;border-radius:14px;padding:10px 14px;font-family:'Courier New',monospace;font-weight:700;
 box-shadow:inset 0 0 14px rgba(30,111,240,.4);line-height:1.45}
.lb-screen div{margin:3px 0}
/* buttons */
.stButton>button,.stDownloadButton>button{border-radius:18px;min-height:3.4rem;font-weight:800;font-size:1.02rem;background:#fff;border:3px solid var(--blue);
 box-shadow:0 5px 0 var(--blue);transition:transform .1s,box-shadow .1s,background .15s}
.stButton>button:hover,.stDownloadButton>button:hover{transform:translateY(-3px) scale(1.02);box-shadow:0 8px 0 var(--blue)}
.stButton>button:active,.stDownloadButton>button:active{transform:translateY(4px) scale(.97);box-shadow:0 1px 0 var(--blue)}
.stButton>button:focus-visible{outline:4px solid var(--yellow);outline-offset:2px}
.stButton>button:disabled{opacity:.5;box-shadow:none;transform:none}
.stButton>button[kind="primary"]{background:linear-gradient(120deg,#7CC4FF,#B3E0FF);border-color:var(--deep);box-shadow:0 5px 0 var(--deep)}
.st-key-act_recycle_water button{background:#BFE3FF}.st-key-act_produce_oxygen button{background:#C9F0FF}
.st-key-act_grow_food button{background:#D6F5D0}.st-key-act_solar_charge button{background:#FFF2B3}
.st-key-act_improve_shield button{background:#E2D9FF}.st-key-act_repair_system button{background:#FFD9C2}
.st-key-end_day button{background:linear-gradient(120deg,#FFE066,#FFC933);border:3px solid #000;box-shadow:0 6px 0 #000;font-size:1.25rem;min-height:4rem}
.st-key-end_day button:hover{box-shadow:0 9px 0 #000}
/* misc widgets */
[data-testid="stMetric"]{background:#fff;border-radius:18px;padding:10px 14px;border:3px solid var(--ice)}
[data-testid="stExpander"]{background:#fff;border-radius:16px;border:3px solid var(--ice)}
[data-testid="stAlert"]{border-radius:16px;border:2px solid var(--blue);background:#F4FAFF}
.stProgress>div>div>div>div{background:linear-gradient(90deg,#2F8CFF,#6FD0FF)}
[data-testid="stRadio"] label,[data-testid="stCheckbox"] label{padding:6px 10px;border-radius:12px}
[data-testid="stRadio"] label:hover,[data-testid="stCheckbox"] label:hover{background:#DDEEFF}
.stTabs [data-baseweb="tab-list"]{gap:6px}
.stTabs [data-baseweb="tab"]{font-weight:800;background:#fff;border:3px solid var(--ice);border-radius:14px 14px 0 0;padding:8px 16px}
.stTabs [aria-selected="true"]{background:#FFE066;border-color:#000}
.stTabs [data-baseweb="tab-highlight"]{display:none}
@media (max-width:640px){html,body,[class*="css"],.stApp{font-size:16px}.lb-brand{font-size:1.4rem}.lb-gauge{min-width:100px}}
/* welcome screen */
.lb-welcome{position:relative;overflow:hidden;text-align:center;padding:26px 22px 22px;border-radius:28px;border:4px solid var(--blue);
 background:radial-gradient(circle at 20% 15%,#fff 0 2px,transparent 3px),radial-gradient(circle at 80% 25%,#fff 0 2px,transparent 3px),
 radial-gradient(circle at 60% 8%,#fff 0 1.5px,transparent 2.5px),linear-gradient(180deg,#7FBFFF 0,#CFE6FF 62%,#EAF4FF 100%);
 box-shadow:0 0 0 4px #fff,0 12px 28px rgba(11,42,85,.28)}
.lb-welcome .w-astro{font-size:4.2rem;display:inline-block;animation:floaty 3s ease-in-out infinite}
.lb-welcome .w-moon{position:absolute;left:0;right:0;bottom:0;height:34px;background:radial-gradient(ellipse at 50% 100%,#E8E8E8 0 60%,transparent 61%)}
@keyframes floaty{50%{transform:translateY(-12px) rotate(4deg)}}
.lb-welcome h1{font-size:2rem;font-weight:800;margin:.2rem 0 .4rem;line-height:1.25}
.lb-welcome .w-lead{font-size:1.15rem;font-weight:700;margin:.2rem auto .8rem;max-width:760px}
.lb-welcome .w-steps{display:flex;flex-wrap:wrap;gap:10px;justify-content:center;margin:.6rem 0 1rem}
.lb-welcome .w-step{flex:1;min-width:200px;max-width:260px;background:#fff;border:3px solid var(--ice);border-radius:18px;padding:10px 12px;font-weight:700}
.lb-welcome .w-step b{display:block;font-size:1.6rem}
.lb-welcome .w-promise{display:inline-block;background:#FFE066;border:3px solid #000;border-radius:16px;padding:8px 16px;font-weight:800;margin:.2rem 0 1.2rem}
.lb-welcome .w-badge{display:block;margin-top:4px;font-weight:800;font-size:.95rem}
/* mission failed sign */
.lb-fail{position:relative;text-align:center;padding:18px 20px 16px;margin:12px 0;border-radius:24px;border:6px solid #E5484D;background:#FFF1F1;
 box-shadow:0 0 0 4px #fff,0 0 0 8px #000,0 12px 26px rgba(120,0,0,.3);animation:shake .6s ease-in-out 1}
.lb-fail::before{content:"";position:absolute;left:0;right:0;top:0;height:14px;border-radius:18px 18px 0 0;
 background:repeating-linear-gradient(45deg,#FFD84D 0 14px,#000 14px 28px)}
.lb-fail .f-badge{display:inline-block;margin-top:14px;padding:6px 22px;border-radius:12px;border:4px solid #000;background:#E5484D;font-size:1.9rem;font-weight:800;letter-spacing:.06em;
 animation:blink2 1.1s ease-in-out infinite}
.lb-fail .f-badge,.stApp .lb-fail .f-badge{color:#fff!important;text-shadow:0 2px 0 #000}
.lb-fail .f-patch{display:flex;align-items:center;justify-content:center;gap:14px;margin:12px 0 4px;flex-wrap:wrap}
.lb-fail .f-icon{font-size:3.4rem;line-height:1;background:#fff;border:4px solid #000;border-radius:50%;width:92px;height:92px;display:flex;align-items:center;justify-content:center;
 box-shadow:inset 0 0 0 4px #FFC2C4}
.lb-fail .f-title{font-size:1.35rem;font-weight:800}
.lb-fail .f-row{background:#fff;border:3px solid #000;border-radius:14px;padding:8px 14px;margin:8px auto;max-width:820px;font-weight:700;text-align:start}
.lb-fail .f-row b{display:block;font-size:.8rem;letter-spacing:.12em}
.lb-fail .f-crew{display:flex;flex-wrap:wrap;justify-content:center;gap:8px;margin:8px 0}
.lb-fail .f-crew span{background:#FFC2C4;border:2px solid #000;border-radius:999px;padding:2px 12px;font-weight:800;font-size:.9rem}
.lb-fail .f-hope{font-weight:800;font-size:1.1rem;margin-top:8px}
@keyframes shake{20%{transform:translateX(-8px)}40%{transform:translateX(8px)}60%{transform:translateX(-5px)}80%{transform:translateX(5px)}}
@keyframes blink2{50%{opacity:.78}}
[class*="st-key-close_box_"]{direction:ltr!important;display:flex;justify-content:flex-end;margin-bottom:-6px}
[class*="st-key-close_box_"] .stButton>button{min-height:1.8rem;width:1.8rem;padding:0;border-radius:50%;font-size:.9rem;border-width:2px;box-shadow:0 2px 0 var(--blue);background:#fff}
[class*="st-key-lang_box_"]{direction:ltr!important;text-align:left}
[class*="st-key-lang_box_"] .stButton>button{min-height:1.8rem;width:1.9rem;min-width:1.9rem;padding:0;font-size:.9rem;border-width:1.5px;box-shadow:0 2px 0 var(--blue);border-radius:999px}
.lb-gauge[data-critical="true"]{border-color:#E5484D;box-shadow:0 0 0 3px rgba(229,72,77,.16);animation:lbCriticalPulse 1.25s ease-in-out infinite}
.lb-danger-notice{display:flex;align-items:center;gap:12px;border:2px solid #B42318;border-left:8px solid #E5484D;border-radius:16px;background:#FFF1F0;padding:12px 16px;margin:10px 0;box-shadow:0 6px 18px rgba(120,0,0,.12);animation:lbNoticeIn .25s ease-out}
.lb-danger-notice .lb-danger-icon{font-size:1.8rem}
.lb-danger-notice .lb-danger-copy{font-weight:800}
.lb-danger-notice .lb-danger-sub{font-size:.88rem;font-weight:600;opacity:.86}
@keyframes lbCriticalPulse{50%{box-shadow:0 0 0 5px rgba(229,72,77,.22);transform:translateY(-2px)}}
@keyframes lbNoticeIn{from{opacity:0;transform:translateY(-8px)}to{opacity:1;transform:translateY(0)}}
.lb-audio-control{display:flex;justify-content:flex-start;align-items:center;gap:8px;margin:3px 0 8px;font-family:Arial,sans-serif}
.lb-audio-control button{border:1px solid #8CB7E8;background:rgba(255,255,255,.88);border-radius:999px;padding:5px 11px;font-size:12px;font-weight:700;cursor:pointer;color:#123!important}
.lb-audio-control button[aria-pressed="true"]{background:#D8F3E4;border-color:#27864B}
.lb-audio-control input{width:76px;accent-color:#1E6FF0}
.lb-audio-control .lb-audio-label{font-size:11px;color:#345!important}
/* scene selector: always ONE row (Streamlit would otherwise stack the 4 buttons on phones and push the scene down) */
.st-key-scene_tabs [data-testid="stHorizontalBlock"]{flex-wrap:nowrap!important;gap:.4rem!important}
.st-key-scene_tabs [data-testid="stColumn"],.st-key-scene_tabs [data-testid="column"]{min-width:0!important;width:auto!important;flex:1 1 0!important}
.st-key-scene_tabs .stButton>button{min-height:2.8rem}
@media (max-width:640px){.st-key-scene_tabs .stButton>button{min-height:2.6rem;padding:.2rem .25rem;font-size:.74rem;border-radius:12px;box-shadow:0 3px 0 var(--blue)}.st-key-scene_tabs .stButton>button p{font-size:.74rem;line-height:1.15}}
@media (max-width:640px){.lb-welcome h1{font-size:1.5rem}.lb-fail .f-badge{font-size:1.3rem}}
</style>
"""

RTL_CSS = """
<style>
html,body,[class*="css"],.stApp{font-family:'Segoe UI',Tahoma,Arial,sans-serif!important;font-size:19px}
/* Arabic letters must stay joined: never add letter-spacing */
.stApp,.stApp *{letter-spacing:0!important}
.stApp{direction:rtl}
.stApp [data-testid="stMarkdownContainer"],.stApp [data-testid="stCaptionContainer"],.stApp [data-testid="stAlert"],
.stApp [data-testid="stMetric"],.stApp [data-testid="stExpander"] summary{text-align:right}
.lb-screen{font-family:'Segoe UI',Tahoma,Arial,sans-serif!important;direction:rtl;text-align:right}
.lb-header{direction:rtl}
.stButton>button p{text-align:center}
</style>
"""


def css(lang="en"):
    """Full stylesheet; adds the right-to-left rules and an Arabic font when lang is Arabic."""
    return CSS + (RTL_CSS if is_rtl(lang) else "")


def esc(x):
    return html.escape(str(x))


def status_of(val, lang="en"):
    """(label, css class, ring colour) - colour is never the only signal: text and icon too."""
    if val >= 50:
        return tr(lang, "✅ Good"), "lb-ok", "#1E6FF0"
    if val >= 25:
        return tr(lang, "⚠️ Watch"), "lb-warn", "#F5A300"
    return tr(lang, "🚨 Danger"), "lb-bad", "#E5484D"


def gauge(label, val, lang="en"):
    icon, _, name = tr(lang, label).partition(" ")
    val = max(0, min(100, int(val)))
    text, cls, color = status_of(val, lang)
    c = 2 * math.pi * 42
    d = c * val / 100
    key = {"💧": "water", "🫁": "oxygen", "⚡": "energy", "🥬": "food", "🛡️": "protection"}.get(icon, "system")
    danger_attr = "true" if val <= 20 else "false"
    return (
        f"<div id='lb-system-{key}' data-resource='{key}' data-critical='{danger_attr}' class='lb-gauge'>"
        f"<svg viewBox='0 0 100 100' width='108' height='108' role='img' aria-label='{esc(name)} {val} {esc(tr(lang, "out of 100"))}'>"
        "<circle cx='50' cy='50' r='42' fill='none' stroke='#CFE6FF' stroke-width='11'/>"
        f"<circle cx='50' cy='50' r='42' fill='none' stroke='{color}' stroke-width='11' stroke-linecap='round' "
        f"stroke-dasharray='{d:.1f} {c:.1f}' transform='rotate(-90 50 50)'/>"
        f"<text x='50' y='52' text-anchor='middle' font-size='26' font-weight='800' fill='#000'>{val}</text>"
        "</svg>"
        f"<div class='g-name'>{esc(icon)} {esc(name)}</div><span class='lb-chip {cls}'>{text}</span></div>"
    )


def gauges_html(resources, labels, lang="en"):
    return "<div class='lb-gauges'>" + "".join(gauge(labels[k], resources[k], lang) for k in labels) + "</div>"


def header_html(g, max_days, lang="en"):
    status = g["status"]
    leds = []
    for d in range(1, max_days + 1):
        if status == "won" or d < g["day"]:
            cls = "done"
        elif d == g["day"]:
            cls = "fail" if status == "lost" else "now"
        else:
            cls = "off"
        leds.append(f"<span class='led {cls}' title='{esc(tr(lang, "Day {d}", d=d))}'></span>")
    bulbs = "".join(
        f"<span class='led {'now' if i < g['actions_remaining'] else 'off'}'></span>" for i in range(g["actions_per_day"])
    )
    return (
        f"<div class='lb-header'><div class='lb-brand'>🌕 {esc(tr(lang, 'LUNABASE'))} <small>{esc(tr(lang, 'MISSION CONSOLE'))}</small></div><div class='lb-hrow'>"
        f"<div><span class='lb-label'>{esc(tr(lang, 'MISSION DAY {d} / {m}', d=min(g['day'], max_days), m=max_days))}</span><br>{''.join(leds)}</div>"
        f"<div><span class='lb-label'>{esc(tr(lang, 'ACTIONS LEFT TODAY'))}</span><br>{bulbs}</div>"
        f"<div><span class='lb-label'>{esc(tr(lang, 'CREW'))}</span><br><b>{esc(tr(lang, g['astronaut']['name']))}</b></div>"
        f"<div><span class='lb-label'>{esc(tr(lang, 'LEVEL'))}</span><br><b>{esc(tr(lang, g['difficulty']))}</b></div></div></div>"
    )


def screen_html(lines):
    return "<div class='lb-screen'>" + "".join(f"<div>{esc(x)}</div>" for x in lines) + "</div>"


def welcome_html(name="", lang="en"):
    """Welcome card shown before the game starts: greets the child hero as a future astronaut."""
    hero = esc(name.strip()) if name and name.strip() else esc(tr(lang, "Little Hero"))
    steps = [("🎯", tr(lang, "Pick 2 actions every day to keep your crew safe.")),
             ("🌅", tr(lang, "Press END DAY and see what surprise the Moon has for you.")),
             ("🏅", tr(lang, "Keep all 5 gauges above 0 for 7 days to win!"))]
    step_html = "".join(f"<div class='w-step'><b>{i}</b>{esc(t)}</div>" for i, t in steps)
    return (
        "<div class='lb-welcome'><div class='w-astro' aria-hidden='true'>🧑‍🚀</div>"
        f"<h1>{tr(lang, 'Welcome to the Moon, {hero}!', hero=hero)}</h1>"
        f"<div class='w-lead'>{esc(tr(lang, 'You are a future astronaut! Here at LunaBase, a real-looking base on the lunar surface, your crew is counting on you for water, air, power, food and protection from space radiation.'))}</div>"
        f"<div class='w-steps'>{step_html}</div>"
        f"<div class='w-promise'>📜 {esc(tr(lang, 'Astronaut promise: I learn, I think, I help my crew, and I never give up!'))}"
        f"<span class='w-badge'>🏅 {esc(tr(lang, 'Your badge: Junior Astronaut'))}</span></div>"
        "<div class='w-moon' aria-hidden='true'></div></div>"
    )


def loss_sign_html(game, lang="en", name=""):
    """The big 'MISSION FAILED' sign shown to the player when the mission is lost (kid friendly: the crew is safe)."""
    from simulation.game_engine import FAILURE_INFO, MAX_DAYS, RESOURCE_LABELS
    res = game.get("failure_resource") or ""
    info = FAILURE_INFO.get(res, {"emoji": "🚨", "story": "The mission could not be completed.",
                                  "tip": "Real astronauts train again and again."})
    label = tr(lang, RESOURCE_LABELS.get(res, "🚨 System")).partition(" ")[2]
    hero = esc(name.strip()) if name and name.strip() else esc(tr(lang, "Little Hero"))
    crew = [game["astronaut"]["name"]]
    crew_html = "".join(f"<span>🧑‍🚀 {esc(tr(lang, c))} · {esc(tr(lang, 'returned safely to Earth'))}</span>" for c in crew)
    return (
        "<div class='lb-fail' role='alert'>"
        f"<div class='f-badge'>🚨 {esc(tr(lang, 'MISSION FAILED'))} 🚨</div>"
        f"<div class='f-patch'><div class='f-icon' aria-hidden='true'>{info['emoji']}</div>"
        f"<div class='f-title'>{esc(tr(lang, 'MISSION CONTROL: ABORT'))}<br>{esc(tr(lang, '{res} FAILURE', res=label.upper() if lang == 'en' else label))}</div></div>"
        f"<div class='f-crew'>{crew_html}</div>"
        f"<div class='f-row'><b>{esc(tr(lang, 'WHAT HAPPENED'))}</b>{esc(tr(lang, info['story']))} "
        f"{esc(tr(lang, 'Reached day {day} of {max}.', day=min(game['day'], MAX_DAYS), max=MAX_DAYS))}</div>"
        f"<div class='f-row'><b>{esc(tr(lang, 'WHAT REAL ASTRONAUTS DO'))}</b>{esc(tr(lang, info['tip']))}</div>"
        f"<div class='f-hope'>💪 {esc(tr(lang, 'Do not give up, {hero}! Every astronaut trains again and again. Try again!', hero=hero))}</div>"
        "</div>"
    )


AUDIO_TEMPLATE = r"""
<style>
  html,body{margin:0;padding:0;background:transparent;font-family:Arial,sans-serif}
  .lb-audio-control{display:flex;justify-content:flex-start;align-items:center;gap:8px;padding:2px 0;flex-wrap:wrap}
  .lb-audio-control button{border:1px solid #8CB7E8;background:rgba(255,255,255,.94);border-radius:999px;padding:5px 11px;font-size:12px;font-weight:700;cursor:pointer;color:#123}
  .lb-audio-control button[aria-pressed="true"]{background:#D8F3E4;border-color:#27864B}
  .lb-audio-control button.blocked{background:#FFF3C4;border-color:#D9A400;animation:lbNudge 1.3s ease-in-out infinite}
  .lb-audio-control input{width:76px;accent-color:#1E6FF0}
  .lb-audio-label{font-size:11px;color:#345}
  @keyframes lbNudge{50%{box-shadow:0 0 0 4px rgba(255,200,0,.35)}}
  @media (prefers-reduced-motion:reduce){*{animation:none!important}}
</style>
<div class="lb-audio-control" dir="__DIR__">
  <button id="lb-music-toggle" type="button" aria-pressed="false" title="__MUSIC__">♫ __MUSIC__</button>
  <span class="lb-audio-label">__VOLUME__</span>
  <input id="lb-music-volume" type="range" min="0" max="100" value="45" aria-label="__VOLUME__">
</div>
<script>
(function(){
  const p=window.parent, VERSION=4;
  const TXT={music:'__MUSIC__',on:'__ON__',off:'__OFF__',tap:'__TAP__'};

  // ================= one shared audio engine for the whole page (survives Streamlit reruns) =================
  if(!p.__lbAudio||p.__lbAudio.version!==VERSION){
    if(p.__lbAudio&&p.__lbAudio.destroy){try{p.__lbAudio.destroy()}catch(e){}}
    const state={version:VERSION,ctx:null,musicBus:null,sfxBus:null,want:true,vol:.45,timer:null,next:0,step:0,ui:[],lastClick:0,listening:false};
    try{
      if(p.localStorage.getItem('lb_music')==='off')state.want=false;       // the child (or parent) switched it off before
      const v=p.localStorage.getItem('lb_music_vol');if(v!==null&&!isNaN(Number(v)))state.vol=Math.max(0,Math.min(1,Number(v)));
    }catch(e){}

    const mtof=m=>440*Math.pow(2,(m-69)/12);
    const getCtx=()=>{
      if(state.ctx)return state.ctx;
      const C=p.AudioContext||p.webkitAudioContext;if(!C)return null;
      const c=new C();
      const comp=c.createDynamicsCompressor();comp.threshold.value=-18;comp.ratio.value=4;comp.connect(c.destination);
      state.musicBus=c.createGain();state.musicBus.gain.value=state.vol;state.musicBus.connect(comp);
      state.sfxBus=c.createGain();state.sfxBus.gain.value=state.vol;state.sfxBus.connect(comp);
      c.onstatechange=()=>state.refresh();
      state.ctx=c;return c;
    };
    const running=()=>!!(state.ctx&&state.ctx.state==='running');

    // ---- one note: soft "music box" bell = fundamental + a quieter octave, with a gentle attack and a long decay
    const note=(bus,f,t,dur,vol,type,partial)=>{
      const c=state.ctx,o=c.createOscillator(),g=c.createGain();
      o.type=type||'sine';o.frequency.setValueAtTime(f,t);
      g.gain.setValueAtTime(.0001,t);g.gain.linearRampToValueAtTime(vol,t+.012);
      g.gain.exponentialRampToValueAtTime(.0001,t+dur);
      o.connect(g);g.connect(bus);o.start(t);o.stop(t+dur+.05);
      if(partial){const o2=c.createOscillator(),g2=c.createGain();o2.type='sine';o2.frequency.setValueAtTime(f*2,t);
        g2.gain.setValueAtTime(.0001,t);g2.gain.linearRampToValueAtTime(vol*partial,t+.01);g2.gain.exponentialRampToValueAtTime(.0001,t+dur*.55);
        o2.connect(g2);g2.connect(bus);o2.start(t);o2.stop(t+dur*.55+.05);}
    };
    const pad=(bus,f,t,dur,vol)=>{
      const c=state.ctx,o=c.createOscillator(),g=c.createGain();
      o.type='triangle';o.frequency.setValueAtTime(f,t);
      g.gain.setValueAtTime(.0001,t);g.gain.linearRampToValueAtTime(vol,t+dur*.35);g.gain.linearRampToValueAtTime(.0001,t+dur);
      o.connect(g);g.connect(bus);o.start(t);o.stop(t+dur+.05);
    };

    // ---- "Moon Lullaby": an original 8-bar loop (Am - F - C - G - Am - F - G - C), 92 BPM.
    const BPM=92,E=60/BPM/2;                       // one eighth note, in seconds
    const MEL=[[76,0,72,0,74,76,72,0],[69,0,72,0,77,0,76,72],[76,0,79,0,76,0,74,72],[74,0,67,71,74,0,0,0],
               [72,0,76,0,81,0,79,76],[77,0,76,72,69,0,72,0],[71,0,74,0,79,0,77,74],[72,0,0,0,76,0,0,0]];
    const CHORD=[[57,60,64],[53,57,60],[55,60,64],[55,59,62],[57,60,64],[53,57,60],[55,59,62],[55,60,64]];
    const BASS=[45,41,48,43,45,41,43,48];
    const playStep=(s,t)=>{
      const bar=(s>>3)%8,e=s&7,m=MEL[bar][e];
      if(m>0){let hold=1;while(hold<6&&MEL[bar][(e+hold)&7]===0&&e+hold<8)hold++;
        note(state.musicBus,mtof(m),t,Math.max(.5,hold*E*1.5),.20,'sine',.28);}
      if(e===0||e===4)note(state.musicBus,mtof(BASS[bar]),t,E*4*.95,.30,'sine',.15);
      if(e===0)CHORD[bar].forEach(n=>pad(state.musicBus,mtof(n),t,E*8,.05));
      if(e&1){const ch=CHORD[bar];note(state.musicBus,mtof(ch[(e>>1)%3]+24),t,.35,.035,'sine',0);}   // soft twinkles
    };
    const schedule=()=>{
      const c=state.ctx;if(!c||c.state!=='running')return;
      if(state.next<c.currentTime)state.next=c.currentTime+.05;
      while(state.next<c.currentTime+.9){playStep(state.step,state.next);state.next+=E;state.step=(state.step+1)&63;}
    };
    const startScheduler=()=>{if(state.timer)return;state.next=0;state.timer=p.setInterval(schedule,150);schedule();};
    const stopScheduler=()=>{if(state.timer){p.clearInterval(state.timer);state.timer=null;}};

    // ---- state shown to the child: playing | blocked (browser waiting for a first touch) | off
    state.mode=()=>!state.want?'off':(running()?'playing':'blocked');
    state.refresh=()=>{state.ui=state.ui.filter(fn=>{try{fn(state.mode());return true}catch(e){return false}})};
    state.bind=fn=>{state.ui.push(fn);try{fn(state.mode())}catch(e){}};

    state.start=()=>{
      state.want=true;try{p.localStorage.setItem('lb_music','on')}catch(e){}
      const c=getCtx();if(!c){state.refresh();return;}
      startScheduler();
      if(c.state!=='running'){const r=c.resume();if(r&&r.then)r.then(()=>{schedule();state.refresh();state.stopListening()},()=>state.refresh());}
      state.refresh();
    };
    state.stopMusic=()=>{
      state.want=false;try{p.localStorage.setItem('lb_music','off')}catch(e){}
      stopScheduler();state.step=0;state.refresh();
    };
    state.toggle=()=>{if(state.want)state.stopMusic();else state.start();return state.want;};
    state.volume=v=>{
      state.vol=Math.max(0,Math.min(1,v));try{p.localStorage.setItem('lb_music_vol',String(state.vol))}catch(e){}
      if(state.ctx){state.musicBus.gain.setTargetAtTime(state.vol,state.ctx.currentTime,.05);state.sfxBus.gain.setTargetAtTime(state.vol,state.ctx.currentTime,.05);}
    };

    // ---- button / alarm sound effects
    state.click=()=>{
      if(!running())return;const now=Date.now();if(now-state.lastClick<65)return;state.lastClick=now;
      const t=state.ctx.currentTime;note(state.sfxBus,620,t,.07,.16,'sine',0);note(state.sfxBus,880,t+.025,.06,.06,'sine',0);
    };
    state.danger=()=>{
      if(!state.ctx)return;const t=state.ctx.currentTime;
      note(state.sfxBus,740,t,.18,.32,'sine',0);note(state.sfxBus,520,t+.2,.22,.28,'triangle',0);note(state.sfxBus,740,t+.46,.18,.25,'sine',0);
    };

    // ---- AUTOPLAY: try right now; if the browser refuses, the very first touch / click / key press anywhere starts the song.
    state.unlock=()=>{
      if(!state.want)return;
      const c=getCtx();if(!c)return;
      startScheduler();
      if(c.state!=='running'){const r=c.resume();if(r&&r.then)r.then(()=>{schedule();state.refresh();state.stopListening()},()=>{});}
      else state.stopListening();
    };
    const EVENTS=['pointerdown','mousedown','touchstart','touchend','keydown','click'];
    const gesture=()=>state.unlock();
    state.listen=()=>{if(state.listening)return;state.listening=true;EVENTS.forEach(ev=>p.document.addEventListener(ev,gesture,{capture:true,passive:true}))};
    state.stopListening=()=>{if(!state.listening||!running())return;state.listening=false;EVENTS.forEach(ev=>p.document.removeEventListener(ev,gesture,{capture:true}))};
    const onVis=()=>{
      if(!state.ctx)return;
      if(p.document.hidden){if(state.ctx.state==='running')state.ctx.suspend().catch(()=>{})}
      else if(state.want)state.unlock();
    };
    p.document.addEventListener('visibilitychange',onVis);
    // sound on every enabled button
    const onClick=e=>{const b=e.target&&e.target.closest&&e.target.closest('button');
      if(b&&!b.disabled&&!b.closest('.lb-audio-control'))state.click()};
    p.document.addEventListener('click',onClick,true);
    state.destroy=()=>{stopScheduler();state.listening&&EVENTS.forEach(ev=>p.document.removeEventListener(ev,gesture,{capture:true}));
      p.document.removeEventListener('visibilitychange',onVis);p.document.removeEventListener('click',onClick,true);
      try{state.ctx&&state.ctx.close()}catch(e){}};
    p.__lbAudio=state;

    state.listen();
    if(state.want)state.start();      // <- autoplay attempt on entry
  }

  // ================= this iframe's controls =================
  const A=p.__lbAudio,b=document.getElementById('lb-music-toggle'),v=document.getElementById('lb-music-volume');
  if(b){
    A.bind(mode=>{
      b.classList.toggle('blocked',mode==='blocked');
      b.setAttribute('aria-pressed',String(mode==='playing'));
      b.textContent='♫ '+(mode==='blocked'?TXT.tap:TXT.music+' · '+(mode==='playing'?TXT.on:TXT.off));
    });
    b.onclick=()=>{
      if(A.mode()==='blocked'){A.unlock();return;}   // the first tap simply lets the song start
      A.toggle();
    };
  }
  if(v){v.value=Math.round(A.vol*100);v.oninput=()=>A.volume(Number(v.value)/100);}
})();
</script>
"""


def audio_controls_html(lang="en"):
    """Space-music control. The song starts by itself on entry (autoplay); if the browser blocks that,
    the first touch/click/key press anywhere on the page starts it. Also provides button/alarm sound effects."""
    ar = is_rtl(lang)
    return (AUDIO_TEMPLATE
            .replace("__DIR__", "rtl" if ar else "ltr")
            .replace("__MUSIC__", esc("موسيقى الفضاء" if ar else "Space ambience"))
            .replace("__ON__", esc("تشغيل" if ar else "On"))
            .replace("__OFF__", esc("إيقاف" if ar else "Off"))
            .replace("__TAP__", esc("المس أي مكان لبدء الموسيقى 🎵" if ar else "Tap anywhere to start the music 🎵"))
            .replace("__VOLUME__", esc("الصوت" if ar else "Volume")))


def danger_sound_html():
    """Plays a short warning cue and scrolls the first newly critical gauge into view."""
    return """<script>(function(){const p=window.parent;const run=()=>{try{if(p.__lbAudio)p.__lbAudio.danger();const d=p.document.querySelector('.lb-gauge[data-critical=\"true\"]');if(d)d.scrollIntoView({behavior:'smooth',block:'center'});}catch(e){}};if(p.requestAnimationFrame)p.requestAnimationFrame(run);else run();})();</script>"""
