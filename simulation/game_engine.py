"""LunaBase game rules: simplified educational simulation."""
import random
from i18n import num, tr
from simulation.food_challenge import CAUSES,generate_food_challenge
from simulation.greenhouse_link import apply_greenhouse_flows
from simulation.life_support import (daily_consumption, initial_subsystem_health, repair_subsystems, wear_subsystems)
CHALLENGE_DAYS=(3,5)
MAX_DAYS=7
RESOURCE_LABELS={"water":"💧 Water","oxygen":"🫁 Oxygen","energy":"⚡ Energy","food":"🥬 Food","protection":"🛡️ Radiation protection"}
DIFFICULTIES={
 "Easy":{"mult":.8,"severity":.75,"start":{"water":90,"oxygen":90,"energy":90,"food":90,"protection":80}},
 "Normal":{"mult":1.0,"severity":1.0,"start":{"water":75,"oxygen":80,"energy":75,"food":70,"protection":65}},
 "Hard":{"mult":1.9,"severity":2.0,"start":{"water":60,"oxygen":65,"energy":60,"food":55,"protection":45}},
}
ACTIONS={
 "recycle_water":{"name":"Recycle water","emoji":"💧","description":"+18 water; costs 5 energy","cost":5,"changes":{"water":18},"lesson":"Water recovery reduces the need for resupply."},
 "produce_oxygen":{"name":"Produce oxygen","emoji":"🫁","description":"+18 oxygen; costs 7 energy","cost":7,"changes":{"oxygen":18},"lesson":"Life-support systems maintain a breathable atmosphere."},
 "grow_food":{"name":"Grow food","emoji":"🥬","description":"+16 food; costs 6 energy","cost":6,"changes":{"food":16},"lesson":"Controlled agriculture may supplement food supplies."},
 "solar_charge":{"name":"Charge batteries","emoji":"☀️","description":"+20 energy","cost":0,"changes":{"energy":20},"lesson":"Solar arrays generate power in suitable sunlight."},
 "improve_shield":{"name":"Improve radiation shield","emoji":"🛡️","description":"+18 protection; costs 8 energy","cost":8,"changes":{"protection":18},"lesson":"Shielding helps reduce radiation exposure."},
 "repair_system":{"name":"Repair life-support","emoji":"🔧","description":"+8 water and oxygen; repairs 3 systems by 18%; costs 12 energy","cost":12,"changes":{"water":8,"oxygen":8},"lesson":"Maintenance helps keep critical systems reliable."},
}
ASTRONAUTS=[
 {"id":"commander","name":"Commander Alex","role":"Mission commander","skill":"Leadership","bonus":"35% chance to neutralize one harmful event once per mission.","description":"Coordinates the crew and mission decisions."},
 {"id":"engineer","name":"Engineer Sam","role":"Systems engineer","skill":"Maintenance","bonus":"Repair action restores 4 extra water and oxygen.","description":"Maintains power and life-support equipment."},
 {"id":"botanist","name":"Dr. Noor","role":"Plant scientist","skill":"Food production","bonus":"Growing food restores 6 extra food.","description":"Studies plants and controlled-environment agriculture."},
 {"id":"life_support","name":"Specialist Riley","role":"Life-support specialist","skill":"Air and water","bonus":"Water recycling and oxygen production each restore 4 extra units.","description":"Monitors the habitat atmosphere and water systems."},
]
# What the "MISSION FAILED" sign tells the player when a resource reaches zero (kid friendly: the crew is safe).
FAILURE_INFO={
 "water":{"emoji":"💧","story":"The water tanks ran dry. Without water the crew cannot drink, cook or cool the machines.","tip":"Real crews recycle almost every drop of water on the International Space Station, including water from the air."},
 "oxygen":{"emoji":"🫁","story":"The oxygen ran out. The crew had to put on their suits and leave the base.","tip":"Real astronauts watch the air all the time: sensors check oxygen and carbon dioxide every second."},
 "energy":{"emoji":"⚡","story":"The batteries went flat. Lights, heaters and life-support machines all stopped.","tip":"Real missions keep spare power so that one bad day of sunlight never switches everything off."},
 "food":{"emoji":"🥬","story":"The food stores ran empty and the crew had no energy left to work.","tip":"Real crews plan meals for every single day and add extra supplies as a safety margin."},
 "protection":{"emoji":"🛡️","story":"The radiation shield failed and the crew had to leave for safety.","tip":"Real crews check space weather and go to a shielded shelter when a solar storm arrives."},
}
EVENTS=[
 ("Solar storm",{"protection":-14,"energy":-6},"A solar storm passed near the base.","Space weather can create radiation risks."),
 ("Water leak",{"water":-13},"A pipe leak reduced water reserves.","Monitoring and maintenance matter in a closed habitat."),
 ("Equipment maintenance",{"energy":-10},"A component required extra maintenance energy.","Complex systems need maintenance and spare capacity."),
 ("Greenhouse success",{"food":12},"The greenhouse produced extra food.","Controlled plant growth is an active research area."),
 ("Oxygen filter issue",{"oxygen":-12},"An oxygen filter issue reduced reserves.","Atmosphere monitoring is vital for crew safety."),
 ("Solar panel boost",{"energy":13},"Favorable sunlight increased energy production.","Power generation depends on environmental conditions."),
 ("Dust on solar panels",{"energy":-9},"Dust reduced solar panel performance.","Dust is an operational challenge for surface equipment."),
 ("Micrometeorite impact",{"protection":-8,"oxygen":-6},"A tiny meteoroid struck the hull; the crew sealed the leak.","Even tiny fast-moving particles can damage surface equipment."),
 ("Ice deposit survey",{"water":12},"Scouts located a small ice deposit near the base.","Water ice in shadowed lunar regions is studied as a possible resource."),
 ("Crew teamwork bonus",{"energy":8,"food":4},"Good teamwork saved energy and reduced waste.","Good teamwork and planning improve mission efficiency."),
 ("Quiet day",{},"No major incident occurred today.","Planning ahead creates resilience."),
]
# Systems depend on each other: when one resource is low it drags another one down.
DEPENDENCIES=[
 ('energy',20,{'oxygen':-3,'water':-3},'Low energy: life-support machines slow down, so oxygen and water drop faster.'),
 ('protection',35,{'energy':-3},'Weak radiation shielding damages electronics, so energy drains faster.'),
 ('water',25,{'food':-3},'Low water: the plants are thirsty, so less food grows.'),
]
DAILY_USE={'water':6,'oxygen':5,'energy':7,'food':6}
def _lang(game): return game.get('lang','en')
def dependency_warnings(game):
 """Texts for every dependency that is active right now (used by the app and the tests)."""
 return [tr(_lang(game),msg) for res,limit,_,msg in DEPENDENCIES if game['resources'][res]<limit]
def apply_dependencies(game,mult=1.0):
 msgs=[]
 for res,limit,drag,msg in DEPENDENCIES:
  if game['resources'][res]<limit:
   for k,v in drag.items(): game['resources'][k]=clamp(game['resources'][k]+min(-1,round(v*mult)))
   msgs.append('🔗 '+tr(_lang(game),msg))
 return msgs
def clamp(x): return max(0,min(100,int(round(x))))
def create_new_game(difficulty="Normal",astronaut_id="commander",seed=None,lang="en"):
 if difficulty not in DIFFICULTIES: difficulty="Normal"
 crew=next((a for a in ASTRONAUTS if a['id']==astronaut_id),ASTRONAUTS[0])
 return {"day":1,"resources":dict(DIFFICULTIES[difficulty]['start']),"difficulty":difficulty,"astronaut":crew,"actions_remaining":2,"actions_per_day":2,"score":0,"status":"active","failure_reason":"","events_log":[],"history":[],"used_commander_shield":False,"rng":random.Random(seed),"learning_points":0,"decisions_count":0,"events_survived":0,"last_event":None,"pending_challenge":None,"challenges_seen":0,"challenges_solved":0,"greenhouse":None,"lang":lang if lang in ("en","ar") else "en","failure_resource":"","subsystem_health":initial_subsystem_health()}
def get_status(game): return game['status']
def perform_action(game,action_id):
 L=_lang(game)
 if game['status']!='active': return {"ok":False,"message":tr(L,"Mission is not active.")}
 if game['actions_remaining']<=0: return {"ok":False,"message":tr(L,"No actions remain today.")}
 if action_id not in ACTIONS: return {"ok":False,"message":tr(L,"Unknown action.")}
 a=ACTIONS[action_id]; res=game['resources']
 if res['energy']<a['cost']: return {"ok":False,"message":tr(L,"Not enough energy.")}
 res['energy']=clamp(res['energy']-a['cost']); changes=dict(a['changes']); crew=game['astronaut']['id']; bonus=""
 if crew=='engineer' and action_id=='repair_system': changes['water']+=4; changes['oxygen']+=4; bonus=' '+tr(L,'Engineer bonus applied.')
 if crew=='botanist' and action_id=='grow_food': changes['food']+=6; bonus=' '+tr(L,'Botanist bonus applied.')
 if crew=='life_support' and action_id=='recycle_water': changes['water']+=4; bonus=' '+tr(L,'Life-support bonus applied.')
 if crew=='life_support' and action_id=='produce_oxygen': changes['oxygen']+=4; bonus=' '+tr(L,'Life-support bonus applied.')
 if action_id == 'repair_system':
  restored = repair_subsystems(game.setdefault('subsystem_health', initial_subsystem_health()), 18)
  repaired = sum(1 for amount in restored.values() if amount > 0)
  bonus += ' ' + tr(L, 'Subsystem maintenance restored {n} systems.', n=repaired)
 applied=[]
 for k,v in changes.items():
  before=res[k]; res[k]=clamp(before+v); applied.append(f"{tr(L,k)} {num(L,res[k]-before,True)}")
 game['actions_remaining']-=1; game['score']+=5; game['learning_points']+=1; game['decisions_count']+=1
 msg=tr(L,"{name} completed ({changes}; energy -{cost}).",name=tr(L,a['name']),changes=tr(L,", ").join(applied),cost=num(L,a['cost']))+bonus
 game['events_log'].append({"day":game['day'],"message":msg})
 return {"ok":True,"message":msg,"lesson":tr(L,a['lesson'])}
def check_failure(game):
 for k in ('water','oxygen','energy','food','protection'):
  if game['resources'][k]<=0:
   game['status']='lost'; game['failure_resource']=k; game['failure_reason']=tr(_lang(game),"{res} reserves reached zero.",res=tr(_lang(game),k.title())); return True
 return False
def advance_day(game):
 L=_lang(game)
 if game['status']!='active': return {"messages":[tr(L,"Mission already ended.")],"event":None}
 if game.get('pending_challenge'): return {"messages":[tr(L,"Solve the food spoilage alert before ending the day.")],"event":None}
 mult=DIFFICULTIES[game['difficulty']]['mult']; messages=[]
 use = daily_consumption(mult, game.setdefault('subsystem_health', initial_subsystem_health()))
 for k,n in use.items():
  game['resources'][k]=clamp(game['resources'][k]-n); messages.append(tr(L,"{res} daily use: {n}.",res=tr(L,k.title()),n=num(L,-n)))
 worn = wear_subsystems(game['subsystem_health'])
 if worn:
  messages.append(tr(L, 'Subsystems need attention: {systems}.', systems=', '.join(tr(L, x) for x in worn)))
 messages+=apply_greenhouse_flows(game,mult); messages+=apply_dependencies(game,mult)
 if check_failure(game):
  messages.append(game['failure_reason']); game['history'].append({"Day":game['day'],**game['resources']}); return {"messages":messages,"event":None}
 name,changes,desc,lesson=game['rng'].choice(EVENTS); severity=DIFFICULTIES[game['difficulty']]['severity']; before_event=dict(game['resources'])
 for k,v in changes.items(): game['resources'][k]=clamp(game['resources'][k]+round(v*severity))
 if game['astronaut']['id']=='commander' and not game['used_commander_shield'] and any(v<0 for v in changes.values()) and game['rng'].random()<.35:
  for k,v in changes.items():
   if v<0: game['resources'][k]=before_event[k]
  game['used_commander_shield']=True; desc=tr(L,"Commander skill neutralized the harmful event: {name}.",name=tr(L,name))
 else: desc=tr(L,desc)
 lesson=tr(L,lesson)
 game['last_event']=name; event={"name":name,"description":desc,"lesson":lesson}; messages += [desc,tr(L,"Learning point: {lesson}",lesson=lesson)]
 if check_failure(game): messages.append(game['failure_reason'])
 else:
  game['events_survived']+=1; game['score']+=sum(game['resources'].values())//25
 game['history'].append({"Day":game['day'],**game['resources']})
 if game['status']=='active':
  if game['day']>=MAX_DAYS: game['status']='won'; messages.append(tr(L,'Seven days completed. Mission success!'))
  else:
   game['day']+=1; game['actions_remaining']=game['actions_per_day']; messages.append(tr(L,"Welcome to day {day}.",day=num(L,game['day'])))
   if game['day'] in CHALLENGE_DAYS:
    game['pending_challenge']=generate_food_challenge(random.Random(game['rng'].random())); game['challenges_seen']+=1; messages.append(tr(L,'🚨 Food spoilage alert! Investigate the data.'))
 return {"messages":messages,"event":event}
def resolve_food_challenge(game,cause_id,fix_id,hint_used=False):
 """Check the player's diagnosis (cause) and fix, then apply the outcome."""
 L=_lang(game); ch=game.get('pending_challenge')
 if not ch: return {"ok":False,"message":tr(L,"No food alert is active.")}
 true=ch['cause']; info=CAUSES[true]; res=game['resources']
 cause_ok=cause_id==true; fix_ok=fix_id==true
 if cause_ok and fix_ok:
  food=12; pts=max(10,20-(5 if hint_used else 0)); lp=3; game['challenges_solved']+=1
  tpl="Correct! {label}. Fix applied: food saved (food {delta})."
 elif cause_ok:
  food=-4; pts=8; lp=1
  tpl="Right cause, but that fix will not solve it. Best fix: {fix}. (food {delta})"
 else:
  food=-10; pts=0; lp=1
  tpl="Not quite. The data pointed to: {label}. Best fix: {fix}. (food {delta})"
 before=res['food']; res['food']=clamp(before+food); food=res['food']-before
 msg=tr(L,tpl,label=tr(L,info['label']),fix=tr(L,info['fix']),delta=num(L,food,True)); game['score']+=pts; game['learning_points']+=lp
 game['events_log'].append({"day":game['day'],"message":tr(L,"Food alert: {msg}",msg=msg)}); game['pending_challenge']=None; check_failure(game)
 return {"ok":True,"message":msg,"lesson":tr(L,info['lesson']),"keep_fresh":tr(L,info['keep_fresh']),"correct":cause_ok and fix_ok,"food_change":food,"points":pts}
def get_final_evaluation(game):
 avg=sum(game['resources'].values())/5
 survival=50 if game['status']=='won' else int(50*game['day']/MAX_DAYS)
 score=min(100,survival+int(avg*.25)+min(15,game['decisions_count']*2)+min(10,game['learning_points']*2))
 grade='Mission Expert' if game['status']=='won' and score>=85 else ('Successful Commander' if game['status']=='won' else ('Promising Trainee' if score>=50 else 'Needs More Training'))
 return {"score":score,"grade":grade,"average_resources":round(avg,1),"decisions":game['decisions_count'],"learning_points":game['learning_points'],"feedback":"Great work balancing survival and learning." if game['status']=='won' else "Review the resource that failed first and plan earlier next time."}

def build_report(game):
 """Plain-text mission report for download (in the language of the game)."""
 L=_lang(game); T=lambda x,**k: tr(L,x,**k)
 ev=get_final_evaluation(game)
 lines=[T("LUNABASE MISSION REPORT"),"="*24,T("Crew: {name} ({role})",name=T(game['astronaut']['name']),role=T(game['astronaut']['role'])),T("Difficulty: {d}",d=T(game['difficulty'])),T("Status: {s}",s=T(game['status'].upper())),T("Days reached: {day} / {max}",day=game['day'],max=MAX_DAYS)]
 if game['failure_reason']: lines.append(T("Failure: {r}",r=T("{res} reserves reached zero.",res=T(game['failure_resource'].title())) if game.get('failure_resource') else game['failure_reason']))
 lines+=[T("Food alerts solved: {a} / {b}",a=game['challenges_solved'],b=game['challenges_seen']),T("Score: {score}/100 - {grade}",score=ev['score'],grade=T(ev['grade'])),T("Decisions: {d} | Learning points: {lp}",d=ev['decisions'],lp=ev['learning_points']),"",T("Final resources:")]
 gh=game.get('greenhouse')
 if gh: lines.insert(-1,T("Greenhouse: linked {days} day(s), {kg:.2f} kg harvested (EDEN ISS yield rates), status {status}.",days=gh['linked_days'],kg=gh['harvest_kg'],status=T(gh['status'])))
 if gh and gh.get("environment_history"):
  latest=gh["environment_history"][-1]
  lines.insert(-1,T("Greenhouse climate on base day {day}: {status}, simulated growth factor {factor:.0%}.",day=latest["base_day"],status=T(latest["status"]),factor=latest["growth_factor"]))
 lines+=[f"  {T(k.title())}: {v}/100" for k,v in game['resources'].items()]
 lines += ["", T("Life-support equipment health:")]
 lines += [f"  {T(label)}: {game.get('subsystem_health', {}).get(key, 100)}%" for key, label in (("water_recycler", "Water recycler"), ("oxygen_generator", "Oxygen generator"), ("solar_array", "Solar array"))]
 science = game.get("science", {})
 lines += ["", T("Surface science objectives:")]
 lines += [f"  {T(label)}: {T('Completed') if science.get(key) else T('Not completed')}" for key, label in (("sample", "Lunar sample"), ("rover", "Rover survey"), ("ice", "Water-ice investigation"), ("landing", "Landing-site assessment"))]
 from simulation.science_missions import SCIENCE_ANALYSIS
 for key in ("ice", "landing"):
  if science.get(key):
   answer_id = game.get("science_answers", {}).get(key)
   answer_text = SCIENCE_ANALYSIS.get(key, {}).get("choices", {}).get(answer_id, T("Not submitted"))
   lines.append(T("Recorded analysis: {answer}", answer=T(answer_text)))
 emergency_drills = game.get("emergency_drills", [])
 lines += ["", T("Emergency training:")]
 lines += [f"  {T(label)}: {T('Completed') if drill_id in emergency_drills else T('Not completed')}" for drill_id, label in (("shelter", "Radiation shelter scenario"), ("isolate", "Habitat leak scenario"), ("backup", "Power failure scenario"))]
 from simulation.emergency_training import DRILLS
 for drill_id, answer_id in game.get("emergency_answers", {}).items():
  answer_text = DRILLS.get(drill_id, {}).get("choices", {}).get(answer_id, answer_id)
  lines.append(T("Emergency decision saved: {answer}", answer=T(answer_text)))
 lines+=["",T("Activity log:")]+[T("  Day {day}: {msg}",day=e['day'],msg=e['message']) for e in game['events_log']]
 lines+=["",T("Note: values are simplified game assumptions, not real mission data.")]
 return "\n".join(lines)
