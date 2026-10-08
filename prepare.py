"""Load measured hemibrain edges; fit an explicitly task-constrained rate model."""
from pathlib import Path
import csv,json,hashlib
import numpy as np
from scipy.optimize import lsq_linear
ROOT=Path(__file__).resolve().parent
SOURCE='https://github.com/aplbrain/seismic'
COMMIT='1a789eefc2ca03c1f79e283069e41d20d12ed91f'
def prepare():
 p=ROOT/'data/hemibrain_conn_df_both.csv'; rows=list(csv.DictReader(p.open())); meta={}
 for r in rows:
  for side in ['pre','post']:
   nid=r['bodyId_'+side];m={k:r[k+'_'+side] for k in ['type','instance','hemisphere','index_fix']}
   if nid in meta and meta[nid]!=m: raise ValueError('Inconsistent neuron metadata')
   meta[nid]=m
 ids=sorted(meta,key=lambda x:(meta[x]['type'],meta[x]['hemisphere'],int(meta[x]['index_fix']),int(x)));idx={x:i for i,x in enumerate(ids)};n=len(ids)
 C=np.zeros((n,n))
 for r in rows:
  count=int(r['weight']);assert count>=0
  C[idx[r['bodyId_post']],idx[r['bodyId_pre']]]+=count
 types=np.array([meta[x]['type'] for x in ids]);hemi=np.array([meta[x]['hemisphere'] for x in ids]);epg=types=='EPG'
 # Coordinate is an assumed anatomical phase map, not a measured tuning curve.
 phi=np.array([(int(meta[x]['index_fix'])-1)%8*2*np.pi/8 for x in ids])
 # Align other cells with their recorded EPG input preference.
 for i in np.flatnonzero(~epg):
  z=np.sum(C[i,epg]*np.exp(1j*phi[epg]));
  if abs(z)>0:phi[i]=np.angle(z)
 # Angular-velocity gating on PENa: an explicit phenomenological input model.
 g=np.where(types=='PENa',np.where(hemi=='L',1.,-1.),0.)
 phase=np.linspace(-np.pi,np.pi,96,endpoint=False)
 phases=np.tile(phase,5);v=np.repeat(np.array([-.6,-.3,0,.3,.6]),len(phase))
 R=.45+.3*np.cos(phases[:,None]-phi)
 derivative=-.3*np.sin(phases[:,None]-phi)
 tau=.15
 X=R*(1+v[:,None]*g)
 Y=R+tau*v[:,None]*derivative
 W=np.zeros_like(C);inh=np.zeros(n);bias=np.zeros(n);errors=[]
 for i in range(n):
  js=np.flatnonzero(C[i]);prior=C[i,js]/max(C[i].sum(),1)*1.6
  A=np.column_stack((X[:,js],-R.mean(axis=1),np.ones(len(R))))
  # Count-informed ridge prior; an assumption, not a physiological fit.
  lam=.03
  Aaug=np.vstack([A,np.column_stack([lam*np.eye(len(js)),np.zeros((len(js),2))]),np.r_[np.zeros(len(js)),.03,0][None,:],np.r_[np.zeros(len(js)+1),.03][None,:]])
  yaug=np.r_[Y[:,i],lam*prior,.03*1.,0.]
  fit=lsq_linear(Aaug,yaug,bounds=(np.r_[np.zeros(len(js)+1),-2],np.r_[np.full(len(js),5),5,2]),tol=1e-8,max_iter=100)
  W[i,js]=fit.x[:len(js)];inh[i]=fit.x[-2];bias[i]=fit.x[-1];errors.append(np.mean((A@fit.x-Y[:,i])**2))
 np.savez_compressed(ROOT/'data/circuit.npz',counts=C,W=W,inhibition=inh,bias=bias,phi=phi,epg=epg,gating=g,ids=np.array(ids),types=types,tau=tau)
 neurons=[{'id':x,**meta[x],'phase_rad':float(phi[i])} for i,x in enumerate(ids)]
 (ROOT/'data/neurons.json').write_text(json.dumps(neurons,indent=2))
 provenance={'dataset':'Janelia hemibrain v1.2.1','extract_source':SOURCE,'commit':COMMIT,'raw_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'neurons':n,'roi_rows':len(rows),'directed_pairs':int(np.count_nonzero(C)),'synapses':int(C.sum()),'types':{t:int(sum(types==t)) for t in sorted(set(types))},'regions':['EB','PB'],'selection':'SEISMIC published extract; traced, noncropped selected EPG/PEN/PEG; Delta7 removed upstream; upstream request min_total_weight=4. Upstream pull_data.py records parameters but has filename formatting bug; archived CSV is canonical for this run.','model_fit':'nonnegative count-regularized least squares to idealized heading and turn dynamics, not physiological recordings','fit_mean_mse':float(np.mean(errors)),'anatomical_edges_added':0,'supplemental_mechanism':'phenomenological population-mean inhibition with fitted per-cell coefficients; not reconstructed inhibitory synapses','license':'SEISMIC archive distributed under MIT; preserved notice; cite hemibrain source as well','matrix_convention':'row postsynaptic; column presynaptic'}
 (ROOT/'data/provenance.json').write_text(json.dumps(provenance,indent=2));print(json.dumps(provenance,indent=2))
if __name__=='__main__':prepare()
