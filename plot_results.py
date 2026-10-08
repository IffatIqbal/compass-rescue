from pathlib import Path
import json,numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
root=Path(__file__).resolve().parent
d=json.loads((root/'results/benchmark.json').read_text())
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
fig,ax=plt.subplots(1,2,figsize=(12,4.4),layout='constrained')
colors={'intact':'#5077c7','damaged':'#d45a73','rescue':'#168d7d','random':'#8f70bd','constant':'#9a794b'}
for m in ['intact','damaged','rescue']:
 r=next(x for x in d['traces'] if x['trial']==0 and x['mode']==m)
 ax[0].plot(r['time'],r['error'],label=m,color=colors[m])
ax[0].axvspan(7,9,color='gray',alpha=.12,label='stimulation off / hold')
ax[0].set(xlabel='Model time',ylabel='Absolute heading error (degrees)',title='One held-out trajectory',ylim=(0,180));ax[0].legend(frameon=False,fontsize=8)
for i,m in enumerate(['intact','damaged','constant','random','rescue']):
 vals=[r['mean_error_deg'] for r in d['trials'] if r['mode']==m]
 ax[1].bar(i,np.mean(vals),color=colors[m],alpha=.4)
 ax[1].scatter(np.arange(len(vals))*.04+i-.1,vals,color=colors[m],s=22)
ax[1].set_xticks(range(5),['Intact','Damaged','Constant','Random','Rescue']);ax[1].set(ylabel='Trial mean error (degrees)',title='Eight held-out trials; dots are individual trials')
fig.suptitle('Compass Rescue | Hemibrain connectivity, task-fitted dynamics',fontsize=14)
fig.savefig(root/'results/benchmark.png',dpi=180)
