"""Regenerate native recipes from authenticated inputs; explicit output only."""
from pathlib import Path
from functools import lru_cache
import argparse, gzip, json, sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import core

def word_text(word):
    """One instruction per line keeps the complete literal word reviewable."""
    lines=['{','  "schema_version": 1,','  "chart": '+json.dumps(word['chart'])+',']
    for key in ('initial_frames','final_frames'):
        lines.append('  '+json.dumps(key)+': {')
        rows=list(word[key].items())
        lines += ['    '+json.dumps(r)+': '+json.dumps(f)+(',' if i+1<len(rows) else '') for i,(r,f) in enumerate(rows)]
        lines.append('  },')
    lines.append('  "program": [')
    lines += ['    '+json.dumps(e,separators=(',',':'))+(',' if i+1<len(word['program']) else '') for i,e in enumerate(word['program'])]
    return '\n'.join(lines+['  ]','}'])+'\n'

def construct():
    core.authenticate()
    C=core.module('clifford_exact.py');N=core.module('native_verify.py')
    cv,ports=core.geometry(N);word=core.build_word(cv)
    core.replay(word,ports)
    @lru_cache(None)
    def chart(f):
        return C.canonical_frame(9,f)
    def from_gates(gates):
        out=C.ident(9)
        for e in gates:
            if e[0]=='P':g=C.perm(9,e[1])
            elif e[0]=='D':g=C.diag(9,e[1],e[2])
            elif e[0]=='C':g=C.cgate(9,e[1],e[2])
            elif e[0]=='X':g=C.xgate(9,e[1])
            else:
                core.need(e[0]=='phase','compiler gate')
                g=C.Op(9,C.identity(9),[e])
            out=out.then(g)
        return out
    edges={}
    for i,e in enumerate(word['program']):
        if e[0]=='transport':edges.setdefault((tuple(e[2]),tuple(e[3])),[]).append(i)
    records=[]
    for (a,b),events in sorted(edges.items()):
        raw=chart(a).adjoint().then(chart(b))
        op=from_gates(core.conjugate(raw.circuit))
        rec,_=C.lower_child(op)
        core.need(rec['rank']==abs(len(a)-len(b)),'compiled rank')
        records.append(dict(old=list(a),new=list(b),events=events,recipe=rec))
    return word,dict(schema_version=1,chart=word['chart'],transports=records)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out-dir',type=Path,required=True);a=ap.parse_args()
    a.out_dir.mkdir(parents=True,exist_ok=True)
    core.need(not any((a.out_dir/n).exists() for n in ['WORD.json','NATIVE.json.gz']),'exclusive new outputs')
    word,recipes=construct()
    (a.out_dir/'WORD.json').write_text(word_text(word),encoding='utf-8',newline='\n')
    (a.out_dir/'NATIVE.json.gz').write_bytes(gzip.compress((json.dumps(recipes,sort_keys=True,separators=(',',':'))+'\n').encode(),mtime=0))
    print('BUILT_PHYSICAL_CORRECTED_DUAL',len(word['program']),len(recipes['transports']))

if __name__=='__main__':main()
