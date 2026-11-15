"""Interactive 2.5D scene set for LunaBase. Pure presentation layer; no simulation rules."""
import json
from html import escape

RESOURCE_LABELS = {
    "water": ("الماء", "WATER"),
    "oxygen": ("الأكسجين", "OXYGEN"),
    "energy": ("الطاقة", "POWER"),
    "food": ("الغذاء", "FOOD"),
    "protection": ("الحماية", "SHIELD"),
}

SCENE_NAMES = {
    "exterior": ("المشهد الخارجي", "EXTERIOR OUTPOST"),
    "interior": ("داخل القاعدة", "HABITAT INTERIOR"),
    "emergency": ("مركز الطوارئ", "EMERGENCY CONTROL"),
    "rover": ("مركبة الاستكشاف", "ROVER EXPLORATION"),
}


# Browser-side behaviour of the scene (plain string, not an f-string, so braces need no escaping).
SCENE_JS = r"""
(()=>{
  const view='__VIEW__', L=__LABELS__, INIT=__INIT__;
  const scene=document.querySelector('.scene'), svg=scene.querySelector('svg.art'), toast=scene.querySelector('.scene-toast');
  let toastTimer=0;
  const say=m=>{toast.textContent=m;toast.classList.add('show');clearTimeout(toastTimer);toastTimer=setTimeout(()=>toast.classList.remove('show'),2300)};
  const post=msg=>{try{window.parent.postMessage(msg,'*')}catch(e){}};

  // ---- Fit: on phones show the WHOLE world (never a cropped middle slice) and tell the host the real height.
  const fit=()=>{
    const w=document.documentElement.clientWidth||scene.clientWidth||1000, narrow=w<640;
    scene.classList.toggle('narrow',narrow);
    if(narrow){
      const art=Math.round(w*0.36), h=Math.max(250,art+56+80);
      scene.style.height=h+'px';
      svg.style.cssText='position:absolute;left:0;right:0;top:auto;bottom:56px;width:100%;height:'+art+'px';
      svg.setAttribute('preserveAspectRatio','xMidYMax meet');
    }else{
      scene.style.height='';svg.removeAttribute('style');
      svg.setAttribute('preserveAspectRatio','xMidYMid slice');
    }
    post({lunabaseFrameHeight:scene.offsetHeight+16});
  };
  fit();window.addEventListener('resize',fit);

  // ---- Drop zones: centre of the actor must be inside the ring AND the actor must really have been dragged.
  const ZONES={
    exterior:[{type:'astro_door',kind:'astro',x:460,y:280,r:62,note:'door',msg:L.astroDoor},
              {type:'astro_sample',kind:'astro',x:180,y:290,r:58,note:'sample',msg:L.astroSample},
              {type:'rover_scan',kind:'rover',x:620,y:255,r:66,note:'scan',msg:L.roverScan}],
    rover:[{type:'rover_scan',kind:'rover',x:620,y:255,r:72,note:'scan',msg:L.roverScan}],
    interior:[],emergency:[]
  }[view]||[];
  const CENTER={astro:[22,35],rover:view==='rover'?[125,30]:[52,16]};
  const MIN_DRAG=14;
  let seq=0;
  const sendEvent=(type,actor,offset)=>post({lunabaseSceneEvent:{type,actor,offset,event_id:Date.now()+'-'+(++seq)}});

  const actors=[];let frame=0;
  const addActor=(selector,kind)=>{
    const el=svg.querySelector(selector);if(!el)return;
    const m=(el.getAttribute('transform')||'').match(/translate\(([-0-9.]+)[ ,]+([-0-9.]+)/);if(!m)return;
    // The server already baked the saved offset into the transform: recover the TRUE base position,
    // so offsets sent back are absolute (this is what keeps the position after a rerun).
    const ox=INIT[kind][0],oy=INIT[kind][1],baseX=Number(m[1])-ox,baseY=Number(m[2])-oy;
    const cx=CENTER[kind][0],cy=CENTER[kind][1];
    const a={el,kind,baseX,baseY,cx,cy,x:ox,y:oy,tx:ox,ty:oy,drag:false,last:null,startTx:ox,startTy:oy,notice:'',timer:0,
             minX:Math.max(-260,40-(baseX+cx)),maxX:Math.min(260,960-(baseX+cx))};
    el.setAttribute('tabindex','0');el.setAttribute('role','button');el.setAttribute('aria-label',L[kind]);
    el.style.pointerEvents='all';el.style.touchAction='none';
    actors.push(a);return a;
  };
  addActor('.astro','astro');addActor('.rover','rover');
  const point=e=>{const pt=svg.createSVGPoint();pt.x=e.clientX;pt.y=e.clientY;return pt.matrixTransform(svg.getScreenCTM().inverse())};
  const clampA=a=>{a.tx=Math.max(a.minX,Math.min(a.maxX,a.tx));a.ty=Math.max(-85,Math.min(75,a.ty))};
  const render=a=>a.el.setAttribute('transform','translate('+(a.baseX+a.x).toFixed(2)+' '+(a.baseY+a.y).toFixed(2)+')');
  const animate=()=>{
    let moving=false;
    actors.forEach(a=>{const dx=a.tx-a.x,dy=a.ty-a.y;
      if(Math.abs(dx)>.08||Math.abs(dy)>.08){a.x+=dx*.28;a.y+=dy*.28;moving=true}else{a.x=a.tx;a.y=a.ty}
      render(a)});
    frame=moving?requestAnimationFrame(animate):0;
  };
  const kick=()=>{if(!frame)frame=requestAnimationFrame(animate)};

  const hideGuide=()=>{scene.classList.remove('guided');scene.classList.add('guide-hide');
    const h=scene.querySelector('.drag-hint');if(h&&h.dataset.plain)h.textContent=h.dataset.plain};
  const finish=a=>{
    const moved=Math.hypot(a.tx-a.startTx,a.ty-a.startTy);
    const x=a.baseX+a.tx+a.cx,y=a.baseY+a.ty+a.cy;
    let type='actor_moved';
    a.notice='';
    if(moved>=MIN_DRAG){
      const z=ZONES.find(z=>z.kind===a.kind&&Math.hypot(x-z.x,y-z.y)<=z.r);
      if(z){type=z.type;a.notice=z.note;say(z.msg)}
    }
    sendEvent(type,a.kind,{x:Math.round(a.tx),y:Math.round(a.ty)});
  };

  actors.forEach(a=>{
    const el=a.el;
    el.addEventListener('pointerdown',e=>{
      e.preventDefault();hideGuide();
      post({lunabaseUnlockAudio:true});   // a touch inside the scene frame also unlocks the music
      a.drag=true;a.last=point(e);a.startTx=a.tx;a.startTy=a.ty;
      try{el.setPointerCapture(e.pointerId)}catch(_){}
      el.style.cursor='grabbing';
    });
    el.addEventListener('pointermove',e=>{
      if(!a.drag)return;e.preventDefault();
      const p=point(e);a.tx+=p.x-a.last.x;a.ty+=p.y-a.last.y;a.last=p;clampA(a);kick();
    });
    const up=e=>{if(!a.drag)return;a.drag=false;el.style.cursor='grab';
      try{el.releasePointerCapture(e.pointerId)}catch(_){}
      finish(a)};
    el.addEventListener('pointerup',up);
    el.addEventListener('pointercancel',up);
    // Keyboard access: arrow keys nudge the actor, the move is committed shortly after the last key press.
    el.addEventListener('keydown',e=>{
      const step=e.shiftKey?40:16,d={ArrowLeft:[-step,0],ArrowRight:[step,0],ArrowUp:[0,-step],ArrowDown:[0,step]}[e.key];
      if(!d)return;e.preventDefault();hideGuide();post({lunabaseUnlockAudio:true});
      if(!a.timer){a.startTx=a.tx;a.startTy=a.ty}
      a.tx+=d[0];a.ty+=d[1];clampA(a);kick();
      clearTimeout(a.timer);a.timer=setTimeout(()=>{a.timer=0;finish(a)},500);
    });
  });
  scene.addEventListener('pointerdown',()=>post({lunabaseUnlockAudio:true}),true);
  const hint=scene.querySelector('.drag-hint');
  if(hint)hint.dataset.plain=(document.documentElement.lang==='ar'?'اسحب رائد الفضاء أو المركبة بإصبعك':'Drag the astronaut or rover with your finger');
  // Animation runs only while an actor is moving, keeping idle devices cool.
})();
"""


def _resource_data(resources, lang):
    data = {}
    for key, names in RESOURCE_LABELS.items():
        try:
            value = max(0, min(100, int(resources.get(key, 0))))
        except (TypeError, ValueError):
            value = 0
        data[key] = {"label": names[0 if lang == "ar" else 1], "value": value}
    return data


def scene_html(resources, lang="en", view="exterior", scan_index=0, astronaut_offset=(0, 0), rover_offset=(0, 0),
               guide=False):
    """Return a responsive illustrated scene with movable astronaut and rover actors.

    guide=True adds the first-play tutorial (animated hand + arrow pointing at the habitat door).
    """
    ar = lang == "ar"
    view = view if view in SCENE_NAMES else "exterior"
    data = _resource_data(resources, lang)
    critical = [(k, v) for k, v in data.items() if v["value"] <= 20]
    title = SCENE_NAMES[view][0 if ar else 1]
    direction = "rtl" if ar else "ltr"
    if critical:
        status = ("‼ خطر: " if ar else "‼ CRITICAL: ") + "، ".join(v["label"] for _, v in critical)
    else:
        status = "● جميع الأنظمة مستقرة" if ar else "● ALL SYSTEMS NOMINAL"
    chips = "".join(
        f'<span class="chip {"low" if v["value"] <= 20 else ""}"><i></i>{escape(v["label"])} <b>{v["value"]}%</b></span>'
        for v in data.values()
    )

    # The artwork is intentionally inline SVG: no external assets, trackers, or network calls.
    art = {
        "exterior": r'''<g class="stars" fill="#fff"><circle cx="80" cy="65" r="2"/><circle cx="190" cy="35" r="1"/><circle cx="320" cy="78" r="1.5"/><circle cx="520" cy="40" r="1"/><circle cx="690" cy="75" r="1.5"/><circle cx="900" cy="38" r="2"/><circle cx="960" cy="115" r="1"/></g>
        <g class="earth"><circle cx="820" cy="86" r="43" fill="#2878b8"/><path d="M790 62l22-12 17 11-8 16-18 2-13 17-12-11zM830 99l18-10 15 10-8 18-16 8-13-14z" fill="#78c99b"/></g>
        <path d="M0 250Q170 210 340 250T680 240T1000 238V360H0Z" fill="#73869c"/><path d="M0 290Q240 250 480 288T1000 280V360H0Z" fill="#aab6c5"/>
        <g transform="translate(335 142)"><ellipse cx="125" cy="150" rx="180" ry="17" fill="#26394f" opacity=".5"/><path d="M35 78Q35 8 125 8Q215 8 215 78Z" fill="#397eae" stroke="#e8f6ff" stroke-width="5"/><path d="M125 10V78M50 48H200" stroke="#d7f2ff" stroke-width="3"/><rect x="20" y="77" width="210" height="78" rx="18" fill="#e3ebf3" stroke="#fff" stroke-width="4"/><rect x="42" y="96" width="42" height="34" rx="5" fill="#204b70"/><rect x="102" y="96" width="42" height="34" rx="5" fill="#204b70"/><rect x="162" y="96" width="42" height="34" rx="5" fill="#204b70"/><circle cx="125" cy="145" r="5" fill="#5ae2b1"/></g>
        <g transform="translate(90 230)"><path d="M60 0L80 76" stroke="#eaf2fa" stroke-width="5"/><path d="M0 5H105L120 58H15Z" fill="#17416c" stroke="#a9d9fa" stroke-width="3"/><path d="M25 5L38 58M55 5L68 58M5 30H112" stroke="#78bce9" stroke-width="2"/></g>
        <g class="rover" transform="translate(700 265)"><rect x="0" y="0" width="105" height="33" rx="9" fill="#edf2f6" stroke="#40566d" stroke-width="4"/><rect x="23" y="-20" width="45" height="24" rx="5" fill="#9ec7df" stroke="#40566d" stroke-width="3"/><circle cx="22" cy="36" r="12" fill="#202e40" stroke="#aebdcb" stroke-width="4"/><circle cx="84" cy="36" r="12" fill="#202e40" stroke="#aebdcb" stroke-width="4"/></g>
        <g class="astro" transform="translate(260 235)"><ellipse cx="20" cy="69" rx="30" ry="7" fill="#25384c" opacity=".5"/><rect x="3" y="28" width="38" height="40" rx="13" fill="#f5f8fb" stroke="#71869c" stroke-width="3"/><circle cx="22" cy="15" r="21" fill="#f8fbff" stroke="#71869c" stroke-width="3"/><ellipse cx="22" cy="15" rx="14" ry="10" fill="#24547a"/><path d="M5 40L-7 53M40 40L52 52M12 66L8 80M34 66L39 80" stroke="#f8fbff" stroke-width="9" stroke-linecap="round"/><rect x="14" y="37" width="17" height="12" rx="3" fill="#4d9bd0"/></g>''',
        "interior": r'''<defs><linearGradient id="wall" x2="0" y2="1"><stop stop-color="#24466b"/><stop offset="1" stop-color="#0a1c34"/></linearGradient></defs>
        <rect x="35" y="42" width="930" height="270" rx="32" fill="url(#wall)" stroke="#8bb9dc" stroke-width="5"/>
        <path d="M65 260H935" stroke="#7f9bb5" stroke-width="8"/><path d="M500 45V310" stroke="#6b91b5" stroke-width="4" opacity=".5"/>
        <rect x="90" y="88" width="250" height="125" rx="16" fill="#122b49" stroke="#78c5ef" stroke-width="4"/><text x="215" y="118" text-anchor="middle" fill="#bfeaff" font-size="18">LIFE SUPPORT</text>
        <g class="screen"><rect x="115" y="135" width="85" height="55" rx="8" fill="#123e58" stroke="#6ad9c5" stroke-width="2"/><path d="M125 174l18-18 14 9 24-22" fill="none" stroke="#6ad9c5" stroke-width="4"/><rect x="215" y="135" width="100" height="55" rx="8" fill="#123e58" stroke="#6ad9c5" stroke-width="2"/><circle cx="265" cy="162" r="18" fill="none" stroke="#6ad9c5" stroke-width="5"/></g>
        <rect x="390" y="95" width="220" height="118" rx="14" fill="#18395a" stroke="#9bd7ff" stroke-width="4"/><text x="500" y="125" text-anchor="middle" fill="#d6f1ff" font-size="18">COMMAND DESK</text><path d="M420 150H580M420 172H545M420 194H565" stroke="#5cb7e9" stroke-width="6" stroke-linecap="round"/>
        <rect x="675" y="78" width="235" height="140" rx="70" fill="#133b5d" stroke="#9bd7ff" stroke-width="5"/><circle cx="790" cy="148" r="54" fill="#2c78ad"/><path d="M752 132l27-22 20 12-7 18-20 6-12 19zM800 164l24-12 18 14-15 23-21-4z" fill="#8ac89b"/><path d="M675 148H910" stroke="#c8eaff" stroke-width="3" opacity=".5"/>
        <g class="astro" transform="translate(130 225)"><rect width="95" height="45" rx="8" fill="#dce8f2"/><path d="M15 0V-18H80V0" fill="#9dd9ed" stroke="#dce8f2" stroke-width="4"/><path d="M48 -17v-28" stroke="#dce8f2" stroke-width="4"/><circle cx="48" cy="-49" r="12" fill="#f7fbff"/><ellipse cx="48" cy="-49" rx="8" ry="6" fill="#27628e"/></g>
        <g transform="translate(720 235)"><rect width="120" height="45" rx="8" fill="#294e6e" stroke="#8cbad8" stroke-width="3"/><path d="M18 10H100M18 25H100" stroke="#58d8ad" stroke-width="5" stroke-linecap="round"/></g>''',
        "emergency": r'''<path d="M0 0H1000V360H0Z" fill="#291d35"/><path d="M0 260L200 190 400 255 620 175 820 245 1000 195V360H0Z" fill="#59445c"/>
        <g transform="translate(500 175)"><circle r="112" fill="#672d3d" opacity=".55"/><circle r="82" fill="#321f32" stroke="#ff7d83" stroke-width="5"/><path d="M0 -52V18" stroke="#ff9296" stroke-width="13" stroke-linecap="round"/><circle cy="48" r="8" fill="#ff9296"/><path d="M-150 0H-95M95 0H150M0 -150V-95M0 95V150" stroke="#ff7d83" stroke-width="5" stroke-linecap="round"/></g>
        <g transform="translate(95 85)"><rect width="240" height="150" rx="15" fill="#271c31" stroke="#ff858b" stroke-width="4"/><text x="120" y="35" fill="#ffd8dc" text-anchor="middle" font-size="18">SYSTEM ALERT</text><path d="M25 62H215M25 91H175M25 120H195" stroke="#ff7d83" stroke-width="8" stroke-linecap="round"/></g>
        <g transform="translate(690 85)"><rect width="220" height="150" rx="15" fill="#271c31" stroke="#ff858b" stroke-width="4"/><text x="110" y="35" fill="#ffd8dc" text-anchor="middle" font-size="18">MISSION CONTROL</text><circle cx="110" cy="92" r="31" fill="none" stroke="#ff7d83" stroke-width="6"/><path d="M110 70V94L127 105" fill="none" stroke="#ffb0b4" stroke-width="5" stroke-linecap="round"/></g>
        <g class="beacon"><path d="M460 290L480 250H520L540 290Z" fill="#ff777e"/><rect x="475" y="290" width="50" height="18" rx="5" fill="#f0dce2"/><circle cx="500" cy="245" r="13" fill="#ffb2b5"/></g>''',
        "rover": r'''<g class="stars" fill="#fff"><circle cx="80" cy="65" r="2"/><circle cx="250" cy="35" r="1"/><circle cx="420" cy="75" r="1.5"/><circle cx="680" cy="42" r="1"/><circle cx="900" cy="85" r="2"/></g>
        <circle cx="835" cy="92" r="48" fill="#d5e3f0" opacity=".9"/><path d="M0 220Q180 180 350 230T700 210T1000 225V360H0Z" fill="#9aa8b9"/><path d="M0 285Q220 245 450 286T1000 270V360H0Z" fill="#657a91"/>
        <g fill="#7b8ca0"><path d="M90 245l70-85 78 88zM700 235l95-112 95 115zM850 265l48-60 62 65z"/></g>
        <g class="rover" transform="translate(330 180)"><path d="M0 65L25 0H210L250 65Z" fill="#e7edf3" stroke="#344c65" stroke-width="5"/><rect x="70" y="-42" width="100" height="68" rx="18" fill="#b7d8eb" stroke="#344c65" stroke-width="5"/><rect x="90" y="-28" width="60" height="38" rx="8" fill="#245b80"/><path d="M20 25H230" stroke="#5c91b9" stroke-width="7"/><circle cx="52" cy="75" r="27" fill="#1b2938" stroke="#c1ced9" stroke-width="7"/><circle cx="198" cy="75" r="27" fill="#1b2938" stroke="#c1ced9" stroke-width="7"/><path d="M118 -45L145 -100" stroke="#e8eff6" stroke-width="6"/><circle cx="146" cy="-103" r="10" fill="#78d9ff"/></g>
        <path d="M450 80Q520 120 620 90" fill="none" stroke="#76d7ff" stroke-width="3" stroke-dasharray="8 8"/><circle cx="620" cy="90" r="8" fill="#76d7ff"/>'''
    }[view]

    # Movement is applied to the SVG actors; offsets are clamped by the caller.
    ax, ay = astronaut_offset
    rx, ry = rover_offset
    art = art.replace('translate(260 235)', f'translate({260 + int(ax)} {235 + int(ay)})')
    art = art.replace('translate(130 225)', f'translate({130 + int(ax)} {225 + int(ay)})')
    art = art.replace('translate(700 265)', f'translate({700 + int(rx)} {265 + int(ry)})')
    art = art.replace('translate(330 180)', f'translate({330 + int(rx)} {180 + int(ry)})')


    if view == "exterior":
        zones_svg = ('<g class="drop-zones" aria-hidden="true">'
                     '<circle cx="180" cy="290" r="42"/><text x="180" y="236" text-anchor="middle">' + ('عينة' if ar else 'SAMPLE') + '</text>'
                     '<circle cx="460" cy="280" r="48"/><text x="460" y="222" text-anchor="middle">' + ('باب القاعدة' if ar else 'HABITAT') + '</text>'
                     '<circle cx="620" cy="255" r="48"/><text x="620" y="197" text-anchor="middle">' + ('مسح' if ar else 'SCAN') + '</text></g>')
    elif view == "rover":
        zones_svg = ('<g class="drop-zones" aria-hidden="true"><circle cx="620" cy="255" r="52"/>'
                     '<text x="620" y="190" text-anchor="middle">' + ('منطقة المسح' if ar else 'SCAN AREA') + '</text></g>')
    else:
        zones_svg = ""
    guide_svg = ""
    if guide and view == "exterior":
        guide_svg = ('<g class="guide" aria-hidden="true"><path class="guide-path" d="M318 305C360 330 410 330 436 300"/>'
                     '<path class="guide-head" d="M424 292L440 297L430 311"/>'
                     '<text class="guide-hand" x="300" y="322">👆</text></g>')
    hint_text = (("👆 اسحب رائد الفضاء إلى الدائرة المضيئة «باب القاعدة»!" if ar else "👆 Drag the astronaut into the glowing HABITAT circle!")
                 if guide and view == "exterior" else
                 ("اسحب رائد الفضاء أو المركبة بإصبعك" if ar else "Drag the astronaut or rover with your finger"))
    labels_js = json.dumps({
        "astroDoor": "اقتربت من باب القاعدة — يمكنك الدخول إلى المحطة." if ar else "You reached the habitat door — welcome inside.",
        "astroSample": "عينة قمرية مكتشفة! أحسنت الاستكشاف." if ar else "Lunar sample found! Great exploring.",
        "roverScan": "تم الوصول إلى منطقة الفحص — المركبة جاهزة للمسح." if ar else "Survey area reached — the rover is ready to scan.",
        "astro": "رائد الفضاء — اسحبه" if ar else "Astronaut — drag me",
        "rover": "المركبة — اسحبها" if ar else "Rover — drag me",
    }, ensure_ascii=False)
    scene_js = (SCENE_JS.replace("__VIEW__", view).replace("__LABELS__", labels_js)
                .replace("__INIT__", json.dumps({"astro": [int(ax), int(ay)], "rover": [int(rx), int(ry)]})))

    emergency_rows = "".join(
        f'<div class="alertrow"><span class="dot"></span><span>{escape(v["label"])}</span><b>{v["value"]}%</b></div>'
        for _, v in critical
    )
    if view == "emergency" and not critical:
        emergency_rows = f'<div class="safe">{"لا توجد أنظمة حرجة حالياً. تابع مراقبة المؤشرات." if ar else "No critical systems right now. Keep monitoring your gauges."}</div>'
    scan_texts = (
        [("اكتشاف: صخور قمرية ذات طبقات مختلفة. سجّل الملاحظة لفريق العلوم.", "اكتشاف: منطقة مظللة قد تستحق فحصاً إضافياً."),
         ("اكتشاف: آثار حفر نيزكية قديمة. لاحظ شكل الحواف.", "اكتشاف: تربة ناعمة؛ خفّف سرعة المركبة.")]
        if ar else
        [("Discovery: layered lunar rocks. Record the observation for the science team.", "Discovery: a shadowed region may deserve a closer survey."),
         ("Discovery: ancient impact craters. Observe the shape of their rims.", "Discovery: soft regolith detected; reduce rover speed.")]
    )
    scan_slot = max(0, scan_index - 1)
    scan_message = scan_texts[(scan_slot // 2) % 2][scan_slot % 2]
    panel = ""
    if view == "emergency":
        panel = f'<div class="scene-panel emergency-panel"><strong>{"الأنظمة التي تحتاج انتباهك" if ar else "SYSTEMS NEEDING ATTENTION"}</strong>{emergency_rows}</div>'
    elif view == "rover":
        panel = f'<div class="scene-panel scan-panel"><strong>{"مهمة الاستكشاف" if ar else "SURFACE SURVEY"}</strong><span>{escape(scan_message) if scan_index else ("اضغط زر المسح أسفل المشهد لاكتشاف ما حولك." if ar else "Use the scan control below to discover your surroundings.")}</span></div>'

    return rf'''<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>
    *{{box-sizing:border-box}}html,body{{margin:0;padding:0;background:transparent;font-family:Arial,sans-serif;color:#fff}}
    .scene{{height:380px;position:relative;overflow:hidden;border-radius:22px;border:1px solid #52769a;background:linear-gradient(180deg,#07152e 0%,#193b60 60%,#8392a5 100%);box-shadow:0 14px 34px #07152f35}}
    .scene.interior{{background:linear-gradient(180deg,#102b49,#09182c)}}.scene.emergency{{background:linear-gradient(180deg,#24192f,#5c3549)}}.scene.rover{{background:linear-gradient(180deg,#07152e,#536982)}}
    .top{{position:absolute;z-index:4;top:14px;left:16px;right:16px;display:flex;justify-content:space-between;align-items:flex-start;gap:8px;direction:{direction}}}.name{{font-size:13px;font-weight:900;letter-spacing:1px;text-shadow:0 2px 8px #000}}.sub{{font-size:10px;opacity:.8;margin-top:4px}}
    .status{{padding:7px 10px;border:1px solid #7ba5d888;border-radius:999px;background:#06162bc9;font-size:10px;font-weight:800;white-space:normal;text-align:center;max-width:48%}}.status.danger{{background:#7d1f2acc;border-color:#ff7777;animation:pulse 1.1s infinite}}
    .art{{position:absolute;inset:0;width:100%;height:100%}}.drop-zones{{pointer-events:none;opacity:.72}}.drop-zones circle{{fill:#67d8ff12;stroke:#9be8ff;stroke-width:2;stroke-dasharray:7 7;filter:drop-shadow(0 0 5px #58cfff);animation:zonePulse 2.2s ease-in-out infinite alternate}}.drop-zones text{{fill:#e8f8ff;font:700 12px Arial;letter-spacing:1px;paint-order:stroke;stroke:#0b2038;stroke-width:4px;stroke-linejoin:round}}.stars circle{{animation:twinkle 3s ease-in-out infinite alternate}}.earth{{animation:glow 5s ease-in-out infinite}}.astro,.rover{{cursor:grab;touch-action:none;user-select:none;-webkit-user-select:none}}.astro:active,.rover:active{{cursor:grabbing}}.beacon{{animation:beacon 1.2s ease-in-out infinite alternate}}
    .hud{{position:absolute;z-index:3;left:12px;right:12px;bottom:10px;display:flex;flex-wrap:wrap;gap:5px;direction:{direction}}}.chip{{display:inline-flex;align-items:center;gap:5px;padding:5px 8px;border-radius:999px;background:#07182bd9;border:1px solid #83a9cf77;font-size:9px;color:#e9f4ff;backdrop-filter:blur(6px)}}.chip i{{width:6px;height:6px;border-radius:50%;background:#55e2a0;box-shadow:0 0 8px #55e2a0}}.chip.low{{border-color:#ff7777;background:#541c2ddd}}.chip.low i{{background:#ff5b64;box-shadow:0 0 9px #ff5b64}}
    .scene-panel{{position:absolute;z-index:3;left:50%;transform:translateX(-50%);bottom:62px;width:min(420px,calc(100% - 28px));padding:10px 13px;border-radius:13px;background:#07182be8;border:1px solid #8cb7d8aa;display:flex;flex-direction:column;gap:6px;font-size:11px;direction:{direction}}}.scene-panel strong{{font-size:10px;letter-spacing:.7px;color:#aee5ff}}.alertrow{{display:flex;align-items:center;gap:8px;padding:3px 0}}.alertrow b{{margin-inline-start:auto;color:#ff8b91}}.dot{{width:8px;height:8px;border-radius:50%;background:#ff5b64;box-shadow:0 0 9px #ff5b64}}.safe{{color:#9fe8c4}}.scan-panel span{{line-height:1.5}}
    @keyframes zonePulse{{to{{opacity:.35;stroke-width:3}}}}@keyframes twinkle{{to{{opacity:.25;transform:scale(.7)}}}}@keyframes glow{{50%{{filter:drop-shadow(0 0 12px #65bfff)}}}}@keyframes float{{50%{{transform:translateY(-6px) rotate(2deg)}}}}@keyframes bob{{50%{{transform:translateY(-3px)}}}}@keyframes pulse{{50%{{box-shadow:0 0 15px #ff555577}}}}@keyframes beacon{{to{{opacity:.4;filter:drop-shadow(0 0 14px #ff6a75)}}}}
    @media(max-width:520px){{.scene{{height:340px;border-radius:16px}}.top{{top:10px;left:10px;right:10px}}.name{{font-size:10px}}.sub{{font-size:9px}}.status{{font-size:9px;padding:6px 8px}}.hud{{left:7px;right:7px;bottom:7px;gap:4px}}.chip{{font-size:8px;padding:4px 6px}}.scene-panel{{bottom:62px;font-size:10px}}}}
    @media(prefers-reduced-motion:reduce){{*{{animation:none!important}}}}
    </style></head><body><section class="scene {view}{" guided" if (guide and view == "exterior") else ""}" role="group" aria-label="LunaBase {escape(title)}">
    <div class="top"><div><div class="name">🌕 {escape(title)}</div><div class="sub">{"مركز القيادة · القمر" if ar else "MISSION VIEW · MOON"}</div></div><div class="status {"danger" if critical else ""}">{escape(status)}</div></div>
    <div class="drag-hint">{escape(hint_text)}</div>
    <div class="scene-toast" aria-live="polite"></div>
    <svg class="art" viewBox="0 0 1000 360" preserveAspectRatio="xMidYMid slice"><defs><linearGradient id="ground" x2="0" y2="1"><stop stop-color="#b7c0cc"/><stop offset="1" stop-color="#596b82"/></linearGradient></defs>{art}{zones_svg}{guide_svg}</svg>{panel}<div class="hud">{chips}</div></section>
    <style>.drag-hint{{position:absolute;z-index:5;left:50%;top:48px;transform:translateX(-50%);padding:6px 11px;border:1px solid #72cfff88;border-radius:999px;background:#06182dcc;color:#eaf8ff;font-size:10px;white-space:nowrap;pointer-events:none}}.scene-toast{{position:absolute;z-index:8;left:50%;bottom:48px;transform:translateX(-50%);max-width:90%;padding:8px 13px;border-radius:12px;background:#06213beF;border:1px solid #67d6ff;color:#fff;font-size:11px;text-align:center;opacity:0;transition:opacity .2s;pointer-events:none}}.scene-toast.show{{opacity:1}}.astro,.rover{{will-change:transform;cursor:grab;outline:none}}.astro:focus-visible,.rover:focus-visible{{filter:drop-shadow(0 0 8px #ffe066)}}.guide-path{{fill:none;stroke:#ffe066;stroke-width:4;stroke-dasharray:9 8;stroke-linecap:round;animation:dash 1s linear infinite}}.guide-head{{fill:none;stroke:#ffe066;stroke-width:5;stroke-linecap:round;stroke-linejoin:round}}.guide-hand{{font-size:34px;animation:handMove 1.8s ease-in-out infinite}}.scene.guided .astro{{animation:astroCall 1.4s ease-in-out infinite}}@keyframes dash{{to{{stroke-dashoffset:-34}}}}@keyframes handMove{{0%{{transform:translate(0,0);opacity:0}}15%{{opacity:1}}80%{{transform:translate(120px,-18px);opacity:1}}100%{{transform:translate(130px,-18px);opacity:0}}}}@keyframes astroCall{{50%{{filter:drop-shadow(0 0 12px #ffe066)}}}}.guide-hide .guide{{display:none}}.narrow .drop-zones text{{font-size:27px;stroke-width:8px}}.narrow .drop-zones circle{{stroke-width:4px}}.narrow .guide-hand{{font-size:46px}}@media(max-width:520px){{.drag-hint{{top:43px;font-size:9px}}}}</style>
    <script>
    {scene_js}
    </script></body></html>'''
