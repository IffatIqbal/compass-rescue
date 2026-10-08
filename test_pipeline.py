import unittest,hashlib,json,csv
from dataclasses import replace
from pathlib import Path
import numpy as np
from model import Circuit,Config,wrap
ROOT=Path(__file__).resolve().parent
class PipelineTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.model=Circuit();cls.data=np.load(ROOT/'data/circuit.npz')
 def test_raw_provenance(self):
  p=json.loads((ROOT/'data/provenance.json').read_text());raw=ROOT/'data/hemibrain_conn_df_both.csv'
  self.assertEqual(hashlib.sha256(raw.read_bytes()).hexdigest(),p['raw_sha256'])
  with raw.open() as f:self.assertEqual(int(self.data['counts'].sum()),sum(int(r['weight']) for r in csv.DictReader(f)))
  self.assertEqual(len(set(self.data['ids'])),106)
 def test_adjacency_and_direction(self):
  ids=list(self.data['ids']);C=self.data['counts'];self.assertEqual(C[ids.index('387364605'),ids.index('387023620')],66)
  self.assertTrue(np.all(self.data['W'][C==0]==0));self.assertTrue(np.all(self.data['W']>=0));self.assertEqual(np.count_nonzero(C),1932)
 def test_replay_and_bounds(self):
  a=self.model.run();b=self.model.run();self.assertEqual(a['angle'],b['angle']);self.assertLessEqual(np.max(np.abs(a['u'])),.35)
  ts=np.array(a['time']);self.assertTrue(np.all(np.array(a['u'])[(ts>=7)&(ts<9)]==0))
 def test_zero_damage_zero_controller(self):
  c=Config(damage=0,gain=0);a=self.model.run(c,'intact');b=self.model.run(c,'rescue');self.assertEqual(a['angle'],b['angle'])
 def test_intact_numerical_refinement(self):
  c=Config(noise=0,sensor_noise=0);a=self.model.run(c,'intact');b=self.model.run(replace(c,dt=.015),'intact')
  self.assertLess(a['metrics']['mean_error_deg'],15);self.assertLess(abs(a['metrics']['mean_error_deg']-b['metrics']['mean_error_deg']),3)
 def test_fixed_nominal_controller(self):
  # Reconstruction and compensation maps are fixed across plant variations.
  original=self.model.lost.copy();self.model.run(Config(plant_gain=.98,lesion_angle=1.1),keep=False)
  np.testing.assert_array_equal(original,self.model.lost)
 def test_hold_memory_without_turns(self):
  r=self.model.run(Config(noise=0),'intact');self.assertLess(r['metrics']['hold_drift_deg'],5)
 def test_final_split(self):
  p=ROOT/'results/benchmark.json'
  if not p.exists():self.skipTest('Run experiment first')
  d=json.loads(p.read_text());self.assertFalse(set(d['train_seeds'])&set(d['heldout_seeds']))
if __name__=='__main__':unittest.main()
