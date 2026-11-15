"""Lightweight 2.5D lunar scene, rendered as self-contained SVG/CSS in Streamlit."""
from html import escape


def mission_scene_html(resources, lang="en"):
    ar = lang == "ar"
    labels = {
        "water": "الماء" if ar else "WATER",
        "oxygen": "الأكسجين" if ar else "OXYGEN",
        "energy": "الطاقة" if ar else "POWER",
        "food": "الغذاء" if ar else "FOOD",
        "protection": "الحماية" if ar else "SHIELD",
    }
    values = {k: max(0, min(100, int(resources.get(k, 0)))) for k in labels}
    critical = [k for k, v in values.items() if v <= 20]
    status = (("‼ خطر في " + "، ".join(labels[k] for k in critical)) if ar else
              ("‼ CRITICAL: " + ", ".join(labels[k] for k in critical) if critical else
               ("● جميع الأنظمة مستقرة" if ar else "● ALL SYSTEMS NOMINAL")))
    chips = "".join(
        '<span class="chip {low}"><i></i>{label} <b>{value}%</b></span>'.format(
            low="low" if values[k] <= 20 else "", label=escape(labels[k]), value=values[k])
        for k in labels
    )
    title = "قاعدة لونا · المشهد الخارجي" if ar else "LUNABASE · LUNAR OUTPOST"
    subtitle = "مركز القيادة · القمر" if ar else "MISSION VIEW · MOON"
    direction = "rtl" if ar else "ltr"

    template = r'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<style>
*{box-sizing:border-box}html,body{margin:0;padding:0;background:transparent;font-family:Arial,sans-serif;color:#fff}
.scene{height:340px;position:relative;overflow:hidden;border-radius:22px;background:linear-gradient(180deg,#07152f 0%,#17345d 58%,#71849a 100%);border:1px solid #496b98;box-shadow:0 12px 30px #07152f30}
.scene:before{content:"";position:absolute;inset:0;z-index:1;background:radial-gradient(ellipse at 75% 12%,#416da866,transparent 28%),linear-gradient(90deg,#08152c66,transparent 45%,#08152c44);pointer-events:none}
.top{position:absolute;z-index:4;top:13px;left:16px;right:16px;display:flex;justify-content:space-between;gap:8px;direction:__DIR__}
.name{font-size:12px;font-weight:900;letter-spacing:1.5px;text-shadow:0 2px 8px #000}.sub{font-size:10px;opacity:.8;margin-top:4px}
.status{padding:7px 10px;border:1px solid #7ba5d888;border-radius:999px;background:#06162bbd;font-size:10px;font-weight:800;white-space:nowrap}
.status.danger{background:#7d1f2acc;border-color:#ff7777;animation:pulse 1.1s infinite}
.art{position:absolute;inset:0;width:100%;height:100%}.stars circle{animation:twinkle 3s ease-in-out infinite alternate}.earth{animation:glow 5s ease-in-out infinite}.astro{animation:float 4s ease-in-out infinite;transform-box:fill-box;transform-origin:center}.rover{animation:bob 5s ease-in-out infinite}
.hud{position:absolute;z-index:3;left:12px;right:12px;bottom:10px;display:flex;flex-wrap:wrap;gap:5px;direction:__DIR__}
.chip{display:inline-flex;align-items:center;gap:5px;padding:5px 8px;border-radius:999px;background:#07182bd9;border:1px solid #83a9cf77;font-size:9px;color:#e9f4ff;backdrop-filter:blur(6px)}
.chip i{width:6px;height:6px;border-radius:50%;background:#55e2a0;box-shadow:0 0 8px #55e2a0}.chip b{color:#fff}.chip.low{border-color:#ff7777;background:#541c2ddd}.chip.low i{background:#ff5b64;box-shadow:0 0 9px #ff5b64}
@keyframes twinkle{to{opacity:.25;transform:scale(.7)}}@keyframes glow{50%{filter:drop-shadow(0 0 12px #65bfff)}}@keyframes float{50%{transform:translateY(-5px) rotate(2deg)}}@keyframes bob{50%{transform:translateY(-2px)}}@keyframes pulse{50%{box-shadow:0 0 15px #ff555577}}
@media(max-width:520px){.scene{height:300px;border-radius:16px}.top{top:10px;left:10px;right:10px}.name{font-size:10px}.sub{font-size:9px}.status{font-size:9px;padding:6px 8px}.hud{left:7px;right:7px;bottom:7px;gap:4px}.chip{font-size:8px;padding:4px 6px}}
@media(prefers-reduced-motion:reduce){*{animation:none!important}}
</style></head><body><section class="scene" role="img" aria-label="LunaBase lunar habitat scene">
<div class="top"><div><div class="name">🌕 __TITLE__</div><div class="sub">__SUBTITLE__</div></div><div class="status __DANGER__">__STATUS__</div></div>
<svg class="art" viewBox="0 0 1000 360" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
<defs><linearGradient id="ground" x2="0" y2="1"><stop stop-color="#b7c0cc"/><stop offset="1" stop-color="#596b82"/></linearGradient><linearGradient id="glass" x2="1" y2="1"><stop stop-color="#8de0ff"/><stop offset="1" stop-color="#245b91"/></linearGradient><linearGradient id="panel" x2="0" y2="1"><stop stop-color="#3b82b8"/><stop offset="1" stop-color="#102d52"/></linearGradient><filter id="shine"><feGaussianBlur stdDeviation="5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
<g class="stars" fill="#fff" opacity=".9"><circle cx="70" cy="72" r="2"/><circle cx="145" cy="42" r="1"/><circle cx="220" cy="96" r="1.5"/><circle cx="310" cy="48" r="1"/><circle cx="385" cy="82" r="1.6"/><circle cx="475" cy="35" r="1"/><circle cx="560" cy="90" r="1.4"/><circle cx="650" cy="48" r="1"/><circle cx="720" cy="110" r="1.2"/><circle cx="875" cy="48" r="1.7"/><circle cx="940" cy="104" r="1"/><circle cx="90" cy="150" r="1"/><circle cx="420" cy="145" r="1"/><circle cx="580" cy="155" r="1"/></g>
<g class="earth" filter="url(#shine)"><circle cx="790" cy="88" r="38" fill="#2e78b7"/><path d="M766 62l17-8 11 9-5 11-14 3-8 12-9-7 4-12zM800 96l16-8 12 8-7 16-14 7-10-11z" fill="#7cc79b"/></g>
<path d="M0 245Q170 205 330 245T660 238T1000 230V360H0Z" fill="#77899e" opacity=".7"/><path d="M0 278Q190 238 390 275T760 265T1000 270V360H0Z" fill="url(#ground)"/>
<!-- Habitat dome and crew module -->
<g transform="translate(330 145)"><ellipse cx="130" cy="145" rx="178" ry="18" fill="#26394f" opacity=".45"/><path d="M35 75Q35 8 130 8Q225 8 225 75Z" fill="url(#glass)" stroke="#e8f6ff" stroke-width="5"/><path d="M130 10V76M50 47H210" stroke="#e8f6ff" stroke-width="3" opacity=".7"/><rect x="20" y="74" width="220" height="75" rx="17" fill="#dbe8f2" stroke="#f7fbff" stroke-width="4"/><rect x="42" y="91" width="42" height="32" rx="5" fill="#234d72" stroke="#d8f2ff" stroke-width="3"/><rect x="101" y="91" width="42" height="32" rx="5" fill="#234d72" stroke="#d8f2ff" stroke-width="3"/><rect x="160" y="91" width="42" height="32" rx="5" fill="#234d72" stroke="#d8f2ff" stroke-width="3"/><path d="M0 149H260" stroke="#e9f5ff" stroke-width="7" stroke-linecap="round"/><circle cx="130" cy="138" r="5" fill="#53e4b2" filter="url(#shine)"/></g>
<!-- Solar farm -->
<g transform="translate(95 218)"><path d="M78 0L98 73" stroke="#e4edf6" stroke-width="5"/><path d="M0 4L95 4L115 55L20 55Z" fill="url(#panel)" stroke="#b6dfff" stroke-width="3"/><path d="M25 5L43 55M55 5L73 55M5 29H105" stroke="#79bce9" stroke-width="2"/></g>
<g transform="translate(745 224)"><path d="M30 5L48 75" stroke="#e4edf6" stroke-width="5"/><path d="M0 0L115 0L105 47L-10 47Z" fill="url(#panel)" stroke="#b6dfff" stroke-width="3"/><path d="M25 0L20 47M55 0L50 47M85 0L80 47M-2 23H110" stroke="#79bce9" stroke-width="2"/></g>
<!-- Rover -->
<g class="rover" transform="translate(620 263)"><rect x="0" y="0" width="94" height="34" rx="9" fill="#e6edf3" stroke="#40566d" stroke-width="4"/><rect x="18" y="-19" width="44" height="24" rx="5" fill="#b9d7e9" stroke="#40566d" stroke-width="3"/><rect x="27" y="-14" width="25" height="12" fill="#2f638c"/><circle cx="19" cy="36" r="12" fill="#1e2c3c" stroke="#aebdcb" stroke-width="4"/><circle cx="76" cy="36" r="12" fill="#1e2c3c" stroke="#aebdcb" stroke-width="4"/></g>
<!-- Junior astronaut -->
<g class="astro" transform="translate(255 230)"><ellipse cx="22" cy="68" rx="29" ry="7" fill="#25384c" opacity=".4"/><rect x="4" y="27" width="37" height="39" rx="13" fill="#f2f6fa" stroke="#71869c" stroke-width="3"/><circle cx="22" cy="14" r="20" fill="#f8fbff" stroke="#71869c" stroke-width="3"/><ellipse cx="23" cy="15" rx="13" ry="10" fill="#24547a" stroke="#bde9ff" stroke-width="2"/><path d="M5 37L-7 52M40 37L52 49M11 63L8 79M34 63L38 79" stroke="#f8fbff" stroke-width="9" stroke-linecap="round"/><rect x="14" y="34" width="17" height="12" rx="3" fill="#4d9bd0"/></g>
<path d="M20 195Q500 150 980 190" fill="none" stroke="#9bdcff" stroke-width="1.5" stroke-dasharray="7 9" opacity=".4"/>
</svg><div class="hud">__CHIPS__</div></section></body></html>'''
    replacements = {
        "__DIR__": direction, "__TITLE__": escape(title), "__SUBTITLE__": escape(subtitle),
        "__DANGER__": "danger" if critical else "", "__STATUS__": escape(status), "__CHIPS__": chips,
    }
    for key, value in replacements.items():
        template = template.replace(key, value)
    return template
