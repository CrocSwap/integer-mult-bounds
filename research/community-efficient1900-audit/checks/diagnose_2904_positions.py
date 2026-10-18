from pathlib import Path
import sys,inspect,textwrap,json,hashlib
P=Path('/tmp/pr-efficient1900');D=P/'sources/2904/research/t185-dirty-entry-frame-screens'
sys.path.insert(0,str(D/'tools'))
import entry_screen as E
W=E.W
original=inspect.getsource(E.Screen.direct_options)
old='times = sorted({i for (i, _, _, _) in self.tl[r] if i < len(self.prog)} | qtimes)'
# All state changes relevant to the gate feasibility, response or unchanged-partner predicate.
new='times = sorted({self.npre, len(self.prog)} | {j for z in ({r,q0} | pset) for (i,_,_,_) in self.tl[z] for j in (i,i+1) if 0 <= j <= len(self.prog)})'
assert old in original
ns={};exec(compile(textwrap.dedent(original.replace(old,new)),str(P/'diagnose_2904_positions.py'),'exec'),E.__dict__,ns)
expanded=ns['direct_options']
for name in sys.argv[1:] or ['pr2857']:
 x,_=W.load(D/f'vendor/{name}/WORD-base.json.gz' if name=='pr2857' else D/f'vendor/{name}/WORD-PM-base.json.gz')
 sc=E.Screen(x,'direct');rows=[]
 for q in range(224,704):
  if not sc.eligible(q):continue
  evs=sc.events(q);t0,first=evs[0];f1=W.basis(first[-1])
  if not f1:continue
  partners=[(e[2],E.F(e[3],e[4]),k) for k,e in evs if e[0]=='add' and e[1]==q];pset={s for s,_,_ in partners};args=(q,t0,f1,partners,sc.horizon(q,evs,t0),pset)
  oldopts=sc.direct_options(*args);newopts=expanded(sc,*args);oldspan=E.Span(o['R'] for o in oldopts);newspan=E.Span(o['R'] for o in newopts)
  extra=[o for o in newopts if not oldspan.contains(o['R'])];target={t:-v for t,v in sc.R0[q].items()}
  row=dict(helper=q,old_options=len(oldopts),expanded_options=len(newopts),old_rank=len(oldspan.piv),expanded_rank=len(newspan.piv),new_directions=len(extra),old_accept=oldspan.contains(target),expanded_accept=newspan.contains(target))
  if extra:row['first_extra']={k:(str(v) if k=='R' else v) for k,v in extra[0].items()}
  rows.append(row);print(json.dumps(dict(family=name,**row)),flush=True)
 (P/f'position-audit-2904-{name}.json').write_text(json.dumps(dict(scope='Independent enlargement to all relevant register/partner transition boundaries; direct-mode primary base word only, not a complete revised circuit audit.',source_sha256=hashlib.sha256((D/'tools/entry_screen.py').read_bytes()).hexdigest(),rows=rows),indent=2)+'\n')
