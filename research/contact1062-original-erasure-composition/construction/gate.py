# SPDX-License-Identifier: Apache-2.0
"""Construct a labelled commuting square and audit its chart-922 operand streams."""
import argparse
import gzip
import hashlib
import io
import json
from collections import Counter
from fractions import Fraction
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent
GRID = 1125 << 25
HEADS = {"7643":"694667c8c129508d78b53a6a51690d4c284d0549","7644":"32cfa1d20d3e4587dc601e69ccac1cd24a239e5c","7113":"07a76c5e2738882c0cb322278e56f6cae3c9885d"}
PINS = {
    "7605-word.json.gz":"37358c493d18ebc6be386aebb4c17529b38883674731f7009ef4e96a5313467d",
    "7642-word.json.gz":"d65839ddd8e514eccb8cb463b90f4043866995d3994908368c940dd302d48adc",
    "7643-word.json.gz":"9cab99591ce19425b261104c7381335a5ccf53c57b5973f27b649a52becc2744",
    "7644-word.json.gz":"1b0efdc59fe3f8056f3dbfdd618c7f5b4b4f0ed4063689f182ae3dbd1138fede",
    "7642-edits.json":"a49e9962e32d13fd91cd8715d888bb1f4305003e63dd25485aa413905e00b8d9",
    "7643-contact.json":"512dbbc3c5133b07400b720f55753e976aca48020e91b2d0086345802de1bc14",
    "7644-edits.json":"70318dfdd760104c07d8c0c45b57bd05bee47499b01767180aaf563ea195bac7",
    "7113-caller.json":"255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc"}
def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",",":")).encode()
def sha(raw):
    return hashlib.sha256(raw).hexdigest()
def need(cond, msg):
    if not cond:
        raise ValueError(msg)
def pack(raw):
    out=io.BytesIO()
    with gzip.GzipFile(fileobj=out, mode="wb", filename="", mtime=0, compresslevel=6) as f:
        f.write(raw)
    return out.getvalue()
def build(inputs):
    def load(name):
        raw=(inputs/name).read_bytes()
        need(sha(raw)==PINS[name],name+" packed hash")
        return json.loads(gzip.decompress(raw) if name.endswith(".gz") else raw)
    load("7113-caller.json")
    word=load("7605-word.json.gz")
    base=list(enumerate(word["program"]))
    def splice(rows, plan, lane, shift):
        need(not plan["append"] and len(base)==plan["base_events"]+shift,"edit base length")
        dels={c+shift:e for c,e in plan["delete"]}
        ins={c+shift if c else 0:es for c,es in plan["insert_before"]}
        result=[]
        seen=set()
        for tag,e in rows:
            if tag in ins:
                result.extend(((lane,tag,k),a) for k,a in enumerate(ins[tag]))
            if tag in dels:
                need(e==dels[tag],f"delete anchor {tag}: {e}")
            else:
                result.append((tag,e))
            seen.add(tag)
        need((set(ins)|set(dels))<=seen,"missing anchors")
        return result
    a=splice(base,load("7642-edits.json"),42,5)
    contact=load("7643-contact.json")
    repl={int(i):v for i,v in contact["proposed_events"].items()}
    for i,e in contact["old_events"].items():
        need(a[int(i)][1]==e,f"contact {i}")
    b=[(tag,repl.get(i,e)) for i,(tag,e) in enumerate(a) if repl.get(i,e) is not None]
    repair=load("7644-edits.json")
    d=splice(base,repair,44,0)
    z=splice(b,repair,44,0)
    for name,seq in (("7642",a),("7643",b),("7644",d)):
        need(load(name+"-word.json.gz")==dict(word,program=[e for _,e in seq]),name+" literal identity")
    return word,{"7605":base,"7642":a,"7643":b,"7644":d,"combined":z},repl

def roles(e):
    return e[1:3] if e[0] in ("ADD","COPY") else e[1:2]
def at922(e):
    return 922 in e[2:4] if e[0]=="MOVE" else e[-1]==922
@lru_cache(None)
def ratio(s):
    q=Fraction(s)
    return q.numerator,q.denominator
def update(row,src,scalar,clock):
    a,b=ratio(scalar)
    for j,x in src.items():
        v,rem=divmod(a*x,b)
        need(not rem,f"grid overflow at event {clock} column {j} coefficient {a*x}/{b*GRID}")
        v+=row.get(j,0)
        if v: row[j]=v
        else: row.pop(j,None)

def slice_rows(seq,watch,n,fields):
    """Reverse liveness on actual opcodes, then evaluate the slice on formal public inputs."""
    live=set()
    use=set()
    for i in range(len(seq)-1,-1,-1):
        tag,e=seq[i]
        op,r=e[:2]
        if r in live and op!="MOVE":
            use.add(i)
            if op in ("INIT","COPY","CLEAR"): live.remove(r)
            if op in ("ADD","COPY"): live.add(e[2])
        if tag in watch: live.update(roles(e))
    rows=[{j:GRID} if j<n else {} for j in range(fields)]
    writers=[None]*fields
    readings={}
    dag=[]
    for i,(tag,e) in enumerate(seq):
        op,r=e[:2]
        if tag in watch:
            readings[tag]=(i,e,[(writers[s],rows[s].copy()) for s in roles(e)])
        if i not in use: continue
        parents=[writers[s] for s in roles(e)]
        dag.append([i,tag,e,parents])
        writers[r]=i
        if op in ("INIT","CLEAR","COPY"): rows[r]={}
        if op=="SCALE":
            src=rows[r]; rows[r]={}; update(rows[r],src,e[2],i)
        elif op in ("ADD","COPY"): update(rows[r],rows[e[2]],e[3],i)
    return readings,dag

def first(word,seqs,repl):
    watch={t for seq in seqs.values() for t,e in seq if at922(e) or isinstance(t,tuple)}
    watch.update(seqs["7642"][i][0] for i in repl)
    selected=("7605","7643","7644","combined")
    streams={}
    archive={"denominator":GRID,"rows":{},"words":{}}
    for name in selected:
        r,dag=slice_rows(seqs[name],watch,word["public"],word["public"]+word["owned_fields"])
        streams[name]=r
        records=[]
        for tag,(i,e,forms) in r.items():
            ids=[]
            for writer,row in forms:
                pairs=sorted(row.items()); key=sha(canonical(pairs))
                archive["rows"].setdefault(key,pairs)
                ids.append([writer,key])
            records.append([i,tag,e,ids])
        archive["words"][name]={"observations":records,"slice":dag}
    # For common origins the #7644 perturbation must be identical with and
    # without the other literal edits. One-sided added observers compare directly.
    counts=Counter()
    first_nonzero={}
    for t in watch:
        for k in range(max(len(s[t][2]) for s in streams.values() if t in s)):
            terms=[]
            for name,sign in (("combined",1),("7643",-1),("7644",-1),("7605",1)):
                if t in streams[name]:
                    i,e,forms=streams[name][t]
                    terms.append((name,i,roles(e)[k],sign,forms[k][1]))
            need(len({x[2] for x in terms})==1,"operand alignment")
            diff=Counter()
            for _,_,_,sign,row in terms:
                for j,v in row.items(): diff[j]+=sign*v
            bad=next((j for j in sorted(diff) if diff[j]),None)
            if bad is not None:
                raise ValueError({"observation":t,"operand":k,"input":bad,"terms":[[n,i,r,str(Fraction(row.get(bad,0),GRID))] for n,i,r,_,row in terms],"mixed":str(Fraction(diff[bad],GRID))})
            counts["operands"]+=1
            if t in streams["combined"] and t in streams["7643"]:
                u=streams["combined"][t][2][k][1]; v=streams["7643"][t][2][k][1]
                if u!=v:
                    counts["nonzero_repair_operand_deltas"]+=1
                    key=str(roles(streams["combined"][t][1])[k])
                    first_nonzero.setdefault(key,[]).append(streams["combined"][t][0])
    data=pack(canonical(archive))
    (ROOT/"first-provenance.json.gz").write_bytes(data)
    result=dict(status="PASS_FIRST",heads=HEADS,counts=counts,distinct_forms=len(archive["rows"]),
        observed_events={name:len(s) for name,s in streams.items()},
        chart922_events={name:sum(at922(e) for _,e in seqs[name]) for name in selected},
        nonzero_delta_clocks_by_role={k:sorted(v) for k,v in first_nonzero.items()},
        provenance_sha256=sha(data),method="exact four-corner mixed difference including all incident chart-922 operands, chart-3 insertions and contact anchors")
    (ROOT/"first-receipt.json").write_bytes(canonical(result))
    return result

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage",choices=("first","full"))
    parser.add_argument("--inputs",type=Path,default=ROOT.parent/"inputs")
    parser.add_argument("--source7644",type=Path,default=ROOT.parent/"closure/pr7644")
    parser.add_argument("--contact-check",type=Path,default=ROOT.parent/"closure/contact_phase.py")
    args=parser.parse_args()
    word,seqs,repl=build(args.inputs)
    if args.stage=="first": result=first(word,seqs,repl)
    else:
        import sys
        sys.path.insert(0,str(ROOT))
        from full_gate import full
        result=full(word,seqs,repl,args)
    print(json.dumps(result,sort_keys=True),flush=True)
if __name__=="__main__":
    main()
