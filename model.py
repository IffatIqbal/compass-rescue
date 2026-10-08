"""Dynamics use 106 real neuron IDs and only observed excitatory edge locations.
Supplemental population inhibition and sensory encoding are explicit model assumptions.
"""
from dataclasses import dataclass
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent
@dataclass(frozen=True)
class Config:
 seed:int=202
 duration:float=12.
 dt:float=.03
 initial:float=.2
 damage:float=.65
 lesion_angle:float=1.
 plant_gain:float=1.
 tau_scale:float=1.
 noise:float=.004
 sensor_noise:float=.008
 sensor_delay:float=.06
 gain:float=1.
 max_stim:float=.35
 blackout:bool=True

def wrap(x):return np.angle(np.exp(1j*x))
class Circuit:
 def __init__(self):
  d=np.load(ROOT/'data/circuit.npz');self.W=d['W'];self.inh=d['inhibition'];self.bias=d['bias'];self.phi=d['phi'];self.epg=d['epg'];self.gating=d['gating'];self.ids=d['ids'];self.types=d['types'];self.tau=float(d['tau']);self.n=len(self.ids)
  self.bins=np.mod(np.round(self.phi/(2*np.pi/8)).astype(int),8)
  # One EPG reporter per sector; selected by smallest body ID, without outcomes.
  self.sensors=np.array([min(np.flatnonzero(self.epg&(self.bins==k)),key=lambda i:int(self.ids[i])) for k in range(8)])
  basis=np.column_stack([np.ones(self.n),np.cos(self.phi),np.sin(self.phi)])
  self.reconstruct=basis@np.linalg.pinv(basis[self.sensors])
  self.decode=np.linalg.pinv(basis[self.epg])
  self.B=(self.bins[:,None]==np.arange(8)[None,:]).astype(float)
  # Nominal damage is fixed. Actual damage/gain may differ without controller knowledge.
  self.nom_damage=.65*np.exp(-.5*(wrap(self.phi-1.)/.55)**2)*(self.types=='PENa')
  self.lost=self.W*self.nom_damage[None,:]
 def run(self,c=Config(),mode='rescue',targets=(0,1,2),keep=True):
  if mode not in ['intact','damaged','rescue','constant','random']:raise ValueError(mode)
  rng=np.random.default_rng(c.seed);ts=np.arange(0,c.duration,c.dt)
  velocity=.28*np.sin(.9*ts+c.seed*.003)+.16*np.sin(1.7*ts+.4)
  velocity[(ts>=7)&(ts<9)]=0
  truth=wrap(c.initial+np.cumsum(velocity)*c.dt)
  r=.45+.3*np.cos(c.initial-self.phi)
  damage=c.damage*np.exp(-.5*(wrap(self.phi-c.lesion_angle)/.55)**2)*(self.types=='PENa')
  W=self.W*c.plant_gain*(1-(damage if mode!='intact' else 0))
  B=self.B[:,targets];proj=np.linalg.solve(B.T@B+.1*np.eye(len(targets)),B.T)
  delay=[r[self.sensors].copy() for _ in range(max(0,round(c.sensor_delay/c.dt)))]
  angles=[];error=[];coh=[];energy=[];rates=[];active=[];us=[];norms=[]
  for i,t in enumerate(ts):
   obs=r[self.sensors]+rng.normal(0,c.sensor_noise,len(self.sensors));delay.append(obs);obs=delay.pop(0)
   on=mode in ['rescue','constant','random'] and not(c.blackout and 7<=t<9)
   u=np.zeros(len(targets))
   if on:
    if mode=='constant':u[:]=.06
    else:u=np.clip(c.gain*proj@self.lost@np.maximum(0,self.reconstruct@obs),-c.max_stim,c.max_stim)
   drive=W@(r*(1+velocity[i]*self.gating))-self.inh*r.mean()+self.bias+B@u
   r=np.clip(r+c.dt/(self.tau*c.tau_scale)*(-r+np.maximum(0,drive))+np.sqrt(c.dt)*rng.normal(0,c.noise,self.n),0,3)
   fit=self.decode@r[self.epg];angle=float(np.arctan2(fit[2],fit[1]));amplitude=float(np.hypot(fit[1],fit[2]))
   angles.append(angle);error.append(float(abs(wrap(angle-truth[i]))*180/np.pi));coh.append(amplitude);energy.append(float(u@u));rates.append(r.copy());active.append(bool(on));us.append(u.copy());norms.append(float(r.max()))
  hold=(ts>=7)&(ts<9);err=np.array(error);ang=np.array(angles);hold_indices=np.flatnonzero(hold)
  metrics={'mean_error_deg':float(err.mean()),'hold_error_deg':float(err[hold].mean()),'hold_drift_deg':float(abs(wrap(ang[hold_indices[-1]]-ang[hold_indices[0]]))*180/np.pi),'energy':float(np.sum(energy)*c.dt),'mean_coherence':float(np.mean(coh)),'max_rate':max(norms),'low_amplitude_fraction':float(np.mean(np.array(coh)<.05))}
  if not keep:return metrics
  s=3
  return {'mode':mode,'config':c.__dict__,'targets':list(targets),'metrics':metrics,'time':ts[::s].tolist(),'truth':truth[::s].tolist(),'angle':angles[::s],'error':error[::s],'coherence':coh[::s],'energy':energy[::s],'rates':np.array(rates)[::s].tolist(),'active':active[::s],'u':np.array(us)[::s].tolist()}
if __name__=='__main__':
 model=Circuit()
 for mode in ['intact','damaged','rescue']:print(mode,model.run(mode=mode,keep=False))
