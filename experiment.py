"""Deterministic ensemble selection and untouched held-out evaluation."""
from pathlib import Path
from dataclasses import replace
import itertools,json,csv,time
import numpy as np
from model import Circuit,Config
ROOT=Path(__file__).resolve().parent

def main():
 start=time.time();model=Circuit()
 train=[Config(seed=310+i*23,initial=a,damage=d,plant_gain=g,tau_scale=t,lesion_angle=l) for i,(a,d,g,t,l) in enumerate([(-2.6,.55,1.,1.,.9),(-1.6,.65,1.01,1.05,1.),(-.5,.75,.99,.95,1.1),(.5,.6,1.,1.1,.95),(1.5,.7,1.01,1.,1.05),(2.6,.8,.99,1.05,1.)])]
 search=[]
 for subset in itertools.combinations(range(8),3):
  for gain in [.5,1.,1.5,2.]:
   scores=[model.run(replace(c,gain=gain),'rescue',subset,False) for c in train]
   errors=[s['mean_error_deg'] for s in scores]
   objective=float(np.mean(errors)+.5*np.std(errors)+np.mean([s['energy'] for s in scores]))
   search.append({'targets':list(subset),'gain':gain,'objective':objective,'training_error_deg':float(np.mean(errors))})
 best=min(search,key=lambda x:x['objective']);targets=best['targets'];gain=best['gain']
 # Held-out data is never used to choose target sets, gain, or fitted weights.
 test=[Config(seed=8001+i*31,initial=a,damage=d,plant_gain=g,tau_scale=t,lesion_angle=l,gain=gain) for i,(a,d,g,t,l) in enumerate([(-2.9,.6,1.005,1.03,.95),(-2.,.7,.995,.97,1.05),(-1.,.75,1.,1.08,1.),(0.,.55,1.005,1.1,1.1),(.9,.8,.995,1.,.9),(1.8,.65,1.,.95,1.),(2.5,.7,1.005,1.05,1.05),(3.,.6,.995,1.,.95)])]
 rand=np.random.default_rng(700).choice(8,3,replace=False).tolist();traces=[];rows=[]
 for k,c in enumerate(test):
  for mode in ['intact','damaged','constant','random','rescue']:
   result=model.run(c,mode,rand if mode=='random' else targets);result['trial']=k;traces.append(result)
   rows.append({'trial':k,'seed':c.seed,'mode':mode,**result['metrics']})
 summary={mode:{metric:float(np.mean([r[metric] for r in rows if r['mode']==mode])) for metric in result['metrics']} for mode in ['intact','damaged','constant','random','rescue']}
 # Random-target distribution, same bounded feedback policy and gain; not energy matched.
 allsets=list(itertools.combinations(range(8),3));choices=np.random.default_rng(701).choice(len(allsets),12,replace=False)
 random_ensemble=[]
 for i in choices:
  subset=allsets[i];scores=[model.run(c,'random',subset,False) for c in test]
  random_ensemble.append({'targets':list(subset),'mean_error_deg':float(np.mean([s['mean_error_deg'] for s in scores])),'energy':float(np.mean([s['energy'] for s in scores]))})
 grid=[]
 for damage in [.2,.4,.6,.8,.95]:
  for plant_gain in [.98,.995,1.005,1.02]:
   c=Config(seed=9501,initial=.8,damage=damage,plant_gain=plant_gain,gain=gain)
   grid.append({'lesion':damage,'recurrent_gain':plant_gain,'damaged':model.run(c,'damaged',targets,False)['mean_error_deg'],'rescue':model.run(c,'rescue',targets,False)['mean_error_deg']})
 # On/off intervention ablation keeps targets and gain frozen.
 continuously_on=[model.run(replace(c,blackout=False),'rescue',targets,False) for c in test]
 payload={'status':'REAL HEMIBRAIN CONNECTIVITY / TASK-FITTED MODEL / NO BIOLOGICAL VALIDATION','provenance':json.loads((ROOT/'data/provenance.json').read_text()),'neurons':json.loads((ROOT/'data/neurons.json').read_text()),'sensor_ids':model.ids[model.sensors].tolist(),'target_ids':{str(k):model.ids[model.bins==k].tolist() for k in targets},'selected_targets':targets,'gain':gain,'train_seeds':[c.seed for c in train],'heldout_seeds':[c.seed for c in test],'random_targets':rand,'search':search,'summary':summary,'trials':rows,'traces':traces,'grid':grid,'random_ensemble':random_ensemble,'continuous_stimulation_mean_error':float(np.mean([s['mean_error_deg'] for s in continuously_on])),'runtime_seconds':time.time()-start}
 counts=np.load(ROOT/'data/circuit.npz')['counts'];post,pre=np.nonzero(counts)
 payload['edges']=[[int(i),int(j),int(counts[i,j])] for i,j in zip(post,pre)];payload['max_edge_count']=int(counts.max())
 (ROOT/'results/benchmark.json').write_text(json.dumps(payload))
 with (ROOT/'results/trials.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
 if (ROOT/'viewer.template.html').exists():(ROOT/'Compass-Rescue.html').write_text((ROOT/'viewer.template.html').read_text().replace('__BENCHMARK_DATA__',json.dumps(payload)))
 print(json.dumps({'selected':best,'summary':summary,'continuous_error':payload['continuous_stimulation_mean_error'],'random_set_errors':[x['mean_error_deg'] for x in random_ensemble],'seconds':time.time()-start},indent=2))
if __name__=='__main__':main()
