import sys,os,json,hashlib
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
import argparse
ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,required=True);ap.add_argument('--output-dir',type=Path,required=True);args=ap.parse_args();r=Path(__file__).parent;dest=args.output_dir;dest.mkdir(parents=True,exist_ok=False)
plt.rcParams['font.family']='DejaVu Sans'
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none'})
data=json.loads(args.input.read_text());manifest={'matplotlib_version':matplotlib.__version__,'input_sha256':hashlib.sha256(args.input.read_bytes()).hexdigest(),'figures':[]}
for dataset in ['Plymouth','Brest']:
 configs=[c for c in data['configs'] if c['dataset']==dataset];assert len(configs)==4
 fig,axes=plt.subplots(4,2,figsize=(11,15));fig.subplots_adjust(left=.10,right=.96,top=.91,bottom=.105,hspace=.55,wspace=.30)
 fig.suptitle(dataset+' - empirical GEV diagnostics',fontsize=18,y=.98)
 for row,c in enumerate(configs):
  label=('Adjusted' if c['adjust'] else 'Naive')+' · '+('selected years removed' if c['remove'] else 'all years')+f" · n={c['n']}"
  color='#087f8c' if c['adjust'] else '#b55d24'
  for j in range(2):
   ax=axes[row,j];xm=c['model_uniform' if j==0 else 'model_gev'];ym=c['empirical_uniform' if j==0 else 'empirical_gev'];lo=c['pp_lower' if j==0 else 'qq_lower'];hi=c['pp_upper' if j==0 else 'qq_upper']
   ax.fill_between(xm,lo,hi,color='#dce7ef',alpha=1);ax.plot(xm,lo,color='#7794ab',lw=.65);ax.plot(xm,hi,color='#7794ab',lw=.65);ax.scatter(xm,ym,s=10,c=color,zorder=3,alpha=.85)
   low=0 if j==0 else min(min(xm),min(ym),min(lo));high=1 if j==0 else max(max(xm),max(ym),max(hi));margin=(high-low)*.03 if j else 0
   ax.plot([low,high],[low,high],ls='--',color='#555555',lw=.8);ax.set_xlim(low-margin,high+margin);ax.set_ylim(low-margin,high+margin)
   ax.set_title(label,fontsize=9,pad=8);ax.set_xlabel('Uniform quantiles' if j==0 else 'Fitted GEV quantiles');ax.set_ylabel('Sorted fitted CDF' if j==0 else 'Maxima');ax.grid(alpha=.18)
 fig.text(.1,.035,'Shading: 95% pointwise plug-in order-statistic bands; no parameter-estimation adjustment.',fontsize=10)
 paths=[]
 for ext in ['png','svg']:
  p=dest/(dataset.lower()+'-diagnostics.'+ext);fig.savefig(p,dpi=150,facecolor='white');paths.append(str(p.resolve()))
 plt.close(fig);manifest['figures'].append({'dataset':dataset,'panels':8,'paths':paths})
(dest/'render-receipt.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(manifest))
