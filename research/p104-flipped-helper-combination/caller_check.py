"""Separate formal and physical checks of one complete mixed caller."""
import argparse, json, subprocess, sys
from pathlib import Path
from linear import HERE,need,read
import dual_check as dual

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--compressed',action='store_true');a=ap.parse_args()
    caller=HERE/('CALLER-COMPRESSED.json' if a.compressed else 'retained/data/caller.json')
    subprocess.run([sys.executable,'-B',str(HERE/'dual_check.py'),'--word',str(HERE/'WORD.json.gz'),'--caller',str(caller),'--controls'],check=True)
    subprocess.run([sys.executable,'-B',str(HERE/'retained/6917/caller_physical.py'),str(caller),str(HERE/'WORD.json.gz')],check=True)
    # The retained geometric audit checks a first-plane shim of each type.
    # Explicitly bind every second-plane chart and the whole joint allocation.
    w,c=read(HERE/'WORD.json.gz'),read(caller)
    need(c['types']['A']['ports']==w['hosted']['Dports'],'Second-plane order')
    mains=set(w['live'])|{r+112 for r in w['live']}|set(w['hosted']['X2'])|set(w['hosted']['Y2'])
    fields=set()
    for e in c['events']:
        if e[0]!='J':continue
        allocation={}
        for i,x2,y2 in zip(w['hosted']['Dports'],w['hosted']['X2'],w['hosted']['Y2']):
            x=w['live'][i]
            for local,role in zip((x,x+112,x2,y2),e[2]):allocation[local]=('main','A',role,i)
        for i in c['types']['B']['ports']:
            x=w['live'][i]
            for local,role in zip((x,x+112),e[3][:2]):allocation[local]=('main','B',role,i)
        for r in range(w['public']):
            if r not in mains:allocation[r]=('helper',e[1],r)
        need(len(allocation)==len(set(allocation.values()))==w['public'],'Injective complete joint field allocation')
        fields.update(allocation.values())
    expected=read(HERE/'RESULT.json')['construction']['productive_fields']
    # Contacts alone omit caller roles never selected for a joint.
    fields.update(('main',ty,r,i) for ty,m in c['types'].items() for r in range(m['offset'],m['offset']+m['roles']) for i in m['ports'])
    need(len(fields)==expected,'Every complete productive field has one independent public label')
    print('PASS_MIXED_CALLER_AND_PHYSICAL_BINDINGS', 'compressed' if a.compressed else 'original',len(fields))

if __name__=='__main__':main()
