"""Source-bound static response-presentation replacement on PR535. No search."""
import argparse,copy,gzip,hashlib,json,sys
from pathlib import Path
from fractions import Fraction as Q

def main():
 if not __debug__:raise SystemExit('Assertions must remain enabled.')
 a=argparse.ArgumentParser();a.add_argument('--raw',type=Path,required=True);a.add_argument('--base',type=Path,required=True);a.add_argument('--old-recipe',type=Path,required=True);a.add_argument('--recipe',type=Path,required=True);a.add_argument('--gk-dir',type=Path,required=True);a.add_argument('--out',type=Path,required=True);a=a.parse_args()
 sys.path.insert(0,str(a.gk_dir));import gk_word as g,gk_common as co;g.V=co.V=112;g.DATA=co.DATA=7168
 load=lambda f:json.loads(gzip.decompress(f.read_bytes())if f.suffix=='.gz'else f.read_bytes())
 semantic=lambda w:hashlib.sha256(json.dumps({k:v for k,v in w.items()if k!='report'},sort_keys=True,separators=(',',':')).encode()).hexdigest()
 raw,base,old,r=map(load,[a.raw,a.base,a.old_recipe,a.recipe]);assert semantic(raw)==r['raw_semantic']and semantic(base)==r['base_semantic']
 sel=r['selection'];seed=g.build(raw,sel,check=True);assert all(len(c['E'])==1 for c in sel['kernel']);assert sum(len(c['pivots'])for c in sel['kernel'])==44
 prefix=seed['A'][:-len(raw['A'])];w=copy.deepcopy(base)
 assert[e[:-1]for e in base['A'][-len(raw['A']):]]==[e[:-1]for e in raw['A']]
 w['A']=prefix+base['A'][-len(raw['A']):]
 for cl in old['selection']['kernel']:
  for h in cl['pivots']:del w['start_extra'][str(224+h)]
 w['start_extra'].update(seed['start_extra'])
 w['cleanup']=[g.inverse(e,g.FULL)for e in reversed(w['A']+w['B'])if not 112<=e[1]<224]
 for sec in ('A','B','cut','cleanup','precondition'):
  for e in w.get(sec,[]):
   if e[0]=='add':assert e[1]!=e[2];q=Q(e[3],e[4])
   else:q=Q(e[2],e[3]);assert q and abs(q.numerator)&(abs(q.numerator)-1)==0
   assert q.denominator&(q.denominator-1)==0
 H=g.profile(w);assert dict(H)=={int(k):v for k,v in r['profile'].items()};assert semantic(w)==r['output_semantic']
 widths=g.widths_of(w);w['report']['local_profile']=dict(H);w['report']['local_rank_mass']=sum(k*v for k,v in H.items());w['report']['static_pivots']=44;w['report']['entrance_rank']=sum(9-x for x in widths);w['report']['entering_helpers']=sum(x<9 for x in widths);w['report']['width_inventory']={x:widths.count(x)for x in sorted(set(widths))};w['report']['status']='EXACT_STATIC44_RESPONSE_PRESENTATION_PENDING_INDEPENDENT_AUDIT'
 a.out.mkdir(parents=True,exist_ok=False);(a.out/'FULL-WORD.json.gz').write_bytes(g.dump(w));(a.out/'SELECTION.json').write_text(json.dumps(sel,indent=2)+'\n');(a.out/'REPLAY.json').write_text(json.dumps({'status':'PASS_EXACT_STATIC44_CONSTRUCTOR','semantic_sha256':semantic(w),'profile':dict(H),'widths':g.widths_of(w)},indent=2)+'\n')
 print('PASS exact static44 constructor')
if __name__=='__main__':main()
