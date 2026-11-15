"""Transparent rule-based Mission Coach."""
from i18n import tr
from simulation.game_engine import ACTIONS,DAILY_USE,DIFFICULTIES

def get_coach_advice(game):
 r=game['resources']; L=game.get('lang','en'); T=lambda x,**k: tr(L,x,**k)
 if game['status']=='won': return {"summary":T("Mission complete! Your crew survived seven days."),"priority":T("Completed"),"recommendations":[T("Review the final score."),T("Try Hard difficulty or another crew specialist.")]}
 if game['status']=='lost': return {"summary":T("Mission ended. Learn from the first critical resource failure."),"priority":T("Mission ended"),"recommendations":[game.get('failure_reason') or T("Review strategy."),T("Restart and protect critical resources earlier.")]}
 mult=DIFFICULTIES[game['difficulty']]['mult']; burn={k:max(1,round(v*mult)) for k,v in DAILY_USE.items()}; runway={k:r[k]/v for k,v in burn.items()}; weakest=min(runway,key=runway.get)
 tips=[]
 limits={'water':42,'oxygen':42,'energy':32,'food':38,'protection':38}
 advice={'water':'Recycle water soon.','oxygen':'Produce oxygen or repair life support.','energy':'Charge batteries before expensive actions.','food':'Grow food before reserves become critical.','protection':'Improve the radiation shield when energy permits.'}
 for k,limit in limits.items():
  if r[k]<=limit: tips.append(T(advice[k]))
 from simulation.game_engine import dependency_warnings
 for w in dependency_warnings(game): tips.append(T('Chain reaction: {w}',w=w))
 if not tips: tips.append(T("{res} has the shortest estimated reserve based on simplified daily use.",res=T(weakest.title())))
 action={'water':'recycle_water','oxygen':'produce_oxygen','energy':'solar_charge','food':'grow_food','protection':'improve_shield'}[weakest]
 if r['energy']>=ACTIONS[action]['cost']: tips.append(T('Suggested action: {a}.',a=T(ACTIONS[action]['name'])))
 else: tips.append(T('Suggested action: Charge batteries to restore energy.'))
 summary=T("{n} action(s) left today. Prioritize the resource with the shortest estimated reserve.",n=game['actions_remaining'])
 gh=game.get('greenhouse')
 if gh and gh['status']=='active':
  from simulation.greenhouse_link import TASKS_PER_DAY,LOW_ENERGY,LOW_WATER
  if r['energy']<LOW_ENERGY: tips=tips[:3]+[T("Low energy will dim the greenhouse lights and shrink tonight's harvest.")]
  elif r['water']<LOW_WATER: tips=tips[:3]+[T("Low water will cut greenhouse irrigation and shrink tonight's harvest.")]
  elif gh['tasks_since_flow']<TASKS_PER_DAY: tips=tips[:3]+[T("Finish {n} more greenhouse task(s) before ending the day for a full harvest.",n=TASKS_PER_DAY-gh['tasks_since_flow'])]
 return {"summary":summary,"priority":T(weakest.title()),"recommendations":tips[:4]}
