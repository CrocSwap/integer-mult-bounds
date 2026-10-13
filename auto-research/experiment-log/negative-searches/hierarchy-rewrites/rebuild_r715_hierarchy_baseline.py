"""Reproduce the pinned R715 hierarchy-to-word pipeline before new structural nominees."""
from pathlib import Path
from types import SimpleNamespace
import os,sys,json,hashlib,gzip,time
r=Path.cwd();out=r/'r715-hierarchy-baseline-rebuild';assert not out.exists();out.mkdir();os.environ['E8COORD']='ham';sys.path[:0]=[str(r/'source463-review/code/rekid'),str(r/'source454-review/e8-r740-replica32/parent436/code/reuse')]
import c2x as C2,compile as C,fullword,reuse as RU,retime as RT
h=SimpleNamespace(**json.loads((r/'r715-hierarchy-rewrite-inventory/HIERARCHY.json').read_text()));h.need=list(map(set,h.need))
start=time.monotonic();W=C2.compile2(h);bad=C.f2_check(W);assert not any(bad);print('RAW COMPILE',W.nh,W.stats,flush=True)
raw=fullword.build(W);fullword.save(raw,str(out/'RAW.json.gz'))
reused,ledger=RU.reuse(raw);fullword.save(reused,str(out/'REUSED.json.gz'));print('REUSE',reused['R'],flush=True)
word,moves=RT.retime(reused,sweeps=6,M=64);fullword.save(word,str(out/'WORD.json.gz'));print('RETIME',word['R'],moves,flush=True)
reference=json.loads(gzip.decompress((r/'source463-review/data/R715_FP_final.json.gz').read_bytes()));assert word==reference,'baseline pipeline differs from pinned word'
result=dict(status='PASS_EXACT_PINNED_R715_HIERARCHY_RECONSTRUCTION',source_hierarchy_sha256=hashlib.sha256((r/'source463-review/data/R715_FP_hier.h').read_bytes()).hexdigest(),canonical_word_sha256=hashlib.sha256(json.dumps(word,sort_keys=True,separators=(',',':')).encode()).hexdigest(),R=word['R'],raw_helpers=W.nh,stats=W.stats,moves=moves,seconds=time.monotonic()-start,scope='Exact parent reconstruction and compiler F2 checks. No new word, bound or native/full replay claim.')
(out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
