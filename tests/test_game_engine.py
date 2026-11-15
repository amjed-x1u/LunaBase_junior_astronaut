import unittest
from simulation.game_engine import create_new_game,perform_action,advance_day,clamp,MAX_DAYS,get_final_evaluation,build_report
from ai.mission_coach import get_coach_advice
import random
from simulation.food_challenge import generate_food_challenge,CAUSES
from simulation.game_engine import resolve_food_challenge
class TestLunaBase(unittest.TestCase):
 def test_two_actions_per_day(self):
  g=create_new_game(seed=3); self.assertTrue(perform_action(g,'grow_food')['ok']); self.assertTrue(perform_action(g,'produce_oxygen')['ok']); self.assertFalse(perform_action(g,'recycle_water')['ok'])
 def test_resource_cap(self):
  g=create_new_game(seed=1); g['resources']['water']=98; perform_action(g,'recycle_water'); self.assertEqual(g['resources']['water'],100)
 def test_clamp(self): self.assertEqual(clamp(-3),0); self.assertEqual(clamp(200),100)
 def test_difficulty(self): self.assertGreater(create_new_game('Easy')['resources']['water'],create_new_game('Hard')['resources']['water'])
 def test_botanist_bonus(self):
  g=create_new_game(astronaut_id='botanist'); before=g['resources']['food']; perform_action(g,'grow_food'); self.assertEqual(g['resources']['food'],min(100,before+22))
 def test_seeded_events_reproducible(self):
  a=create_new_game(seed=44); b=create_new_game(seed=44); advance_day(a); advance_day(b); self.assertEqual(a['last_event'],b['last_event'])
 def test_evaluation_shape(self):
  e=get_final_evaluation(create_new_game()); self.assertIn('score',e); self.assertIn('grade',e)
 def test_not_enough_energy(self):
  g=create_new_game(seed=1); g['resources']['energy']=2; self.assertFalse(perform_action(g,'improve_shield')['ok'])
 def test_loss_on_zero_resource(self):
  g=create_new_game(seed=1); g['resources']['water']=3; advance_day(g); self.assertEqual(g['status'],'lost'); self.assertEqual(len(g['history']),1)
 def test_full_run_ends_in_win_or_loss(self):
  g=create_new_game('Easy',seed=5)
  for _ in range(20):
   if g['status']!='active': break
   if g['pending_challenge']: resolve_food_challenge(g,g['pending_challenge']['cause'],g['pending_challenge']['cause'])
   if g['resources']['energy']<40: perform_action(g,'solar_charge')
   advance_day(g)
  self.assertIn(g['status'],('won','lost')); self.assertLessEqual(g['day'],MAX_DAYS)
 def test_commander_shield_restores_resources(self):
  import simulation.game_engine as ge
  g=create_new_game(astronaut_id='commander',seed=2); g['rng'].random=lambda:0.0
  orig=ge.EVENTS; ge.EVENTS=[("Water leak",{"water":-13},"d","l")]
  try:
   before=g['resources']['water']-6; advance_day(g)
  finally: ge.EVENTS=orig
  self.assertEqual(g['resources']['water'],before); self.assertTrue(g['used_commander_shield'])
 def test_coach_uses_difficulty(self):
  g=create_new_game('Hard',seed=1); self.assertIn('priority',get_coach_advice(g))
 def test_report_text(self):
  g=create_new_game(seed=1); perform_action(g,'grow_food'); self.assertIn('LUNABASE MISSION REPORT',build_report(g))
 def test_challenge_data_supports_cause(self):
  col={'temperature':'Temp (°C)','humidity':'Humidity (%)','water':'Microbes (CFU/g)','ethylene':'Ethylene (ppm)'}
  for cause in CAUSES:
   for seed in range(20):
    ch=generate_food_challenge(random.Random(seed),cause); bad=[r for r in ch['rows'] if r['Spoiled (%)']>=30]; good=[r for r in ch['rows'] if r['Spoiled (%)']<30]
    self.assertEqual([r['Bin'] for r in bad],ch['affected_bins']); c=col[cause]
    self.assertGreater(min(r[c] for r in bad),max(r[c] for r in good))
    if cause!='water': self.assertTrue({r['Water tank'] for r in bad}=={'Tank 1','Tank 2'} or len(bad)==2)
 def test_challenge_is_reproducible(self):
  self.assertEqual(generate_food_challenge(random.Random(9)),generate_food_challenge(random.Random(9)))
 def test_alert_triggers_on_day_three_and_blocks(self):
  g=create_new_game('Easy',seed=1)
  for _ in range(2): advance_day(g)
  self.assertEqual(g['day'],3); self.assertIsNotNone(g['pending_challenge'])
  r=advance_day(g); self.assertEqual(g['day'],3); self.assertIn('Solve',r['messages'][0])
 def test_resolve_outcomes(self):
  def setup():
   g=create_new_game('Easy',seed=1); g['resources']['food']=50; g['pending_challenge']=generate_food_challenge(random.Random(2),'humidity'); return g
  g=setup(); r=resolve_food_challenge(g,'humidity','humidity'); self.assertTrue(r['correct']); self.assertEqual(g['resources']['food'],62); self.assertEqual(g['challenges_solved'],1); self.assertIsNone(g['pending_challenge'])
  g=setup(); r=resolve_food_challenge(g,'humidity','water'); self.assertFalse(r['correct']); self.assertEqual(g['resources']['food'],46)
  g=setup(); resolve_food_challenge(g,'water','water'); self.assertEqual(g['resources']['food'],40)
  g=setup(); resolve_food_challenge(g,'humidity','humidity',hint_used=True); self.assertEqual(g['score'],15)
  self.assertFalse(resolve_food_challenge(g,'humidity','humidity')['ok'])
 def test_alert_message_reports_real_food_change(self):
  g=create_new_game('Easy',seed=1); g['resources']['food']=95; g['pending_challenge']=generate_food_challenge(random.Random(2),'humidity')
  r=resolve_food_challenge(g,'humidity','humidity'); self.assertEqual(g['resources']['food'],100); self.assertEqual(r['food_change'],5); self.assertIn('food +5',r['message'])
 def test_resolve_returns_keep_fresh_tip(self):
  g=create_new_game('Easy',seed=1); g['pending_challenge']=generate_food_challenge(random.Random(2),'water')
  self.assertIn('clean water',resolve_food_challenge(g,'water','water')['keep_fresh'].lower())
if __name__=='__main__': unittest.main()
