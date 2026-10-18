"""Finite ring controls; --lean additionally recompiles and audits the live kernel proof."""
import argparse,hashlib,json,os,re,shutil,subprocess,tempfile
from pathlib import Path
P=Path(__file__).resolve().parent
R=P.parent.parent
ROOTS=("map_sub","factorization","left_inverse","right_inverse","projection_idempotent",
       "image_iff","lifted_injective","involution","conjugate_factorization",
       "conjugate_left_inverse","conjugate_right_inverse","conjugate_residual",
       "integer_example","integer_split_example")

def need(ok,message):
    if not ok:raise ValueError(message)
def canonical(x):return json.dumps(x,sort_keys=True,separators=(",",":"),allow_nan=False)
def sha(x):return hashlib.sha256(x).hexdigest()
def sources():
    for item in json.loads((P/"SOURCES.json").read_bytes())["files"]:
        if item["usage"]=="input":
            raw=(R/item["path"]).read_bytes()
            need(sha(raw)==item["sha256"],"source hash mismatch")
            need(hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()==item["git_blob"],"source blob mismatch")

def ident(n):return [[int(i==j) for j in range(n)] for i in range(n)]
def transpose(a):return [list(x) for x in zip(*a)]
def add(a,b,q):return [[(x+y)%q for x,y in zip(ar,br)] for ar,br in zip(a,b)]
def neg(a,q):return [[-x%q for x in row] for row in a]
def sub(a,b,q):return add(a,neg(b,q),q)
def mul(a,b,q):
    return [[sum(x*y for x,y in zip(row,col))%q for col in zip(*b)] for row in a]
def block(a,b,c,d):return [x+y for x,y in zip(a,b)]+[x+y for x,y in zip(c,d)]

def inverse(a,q):
    n=len(a);t=[row[:]+ir for row,ir in zip(a,ident(n))]
    import math
    for j in range(n):
        pivot=next((i for i in range(j,n) if math.gcd(t[i][j],q)==1),None)
        need(pivot is not None,"nonunit matrix pivot")
        t[j],t[pivot]=t[pivot],t[j]
        u=pow(t[j][j],-1,q);t[j]=[x*u%q for x in t[j]]
        for i in range(n):
            if i!=j:
                c=t[i][j];t[i]=[(x-c*y)%q for x,y in zip(t[i],t[j])]
    need([row[:n] for row in t]==ident(n),"inverse elimination")
    return [row[n:] for row in t]

def chart(n,q,variant):
    a=ident(n)
    if n>1:
        for k in range(2*n+variant):
            i=k%n;j=(i+1+(variant%(n-1)))%n
            if i==j:j=(i+1)%n
            a[i]=[(x+(k+1)*y)%q for x,y in zip(a[i],a[j])]
        a=a[1:]+a[:1]
    a[0]=[2*x%q for x in a[0]]
    return a

def rank_mod(a,p):
    t=[[x%p for x in row] for row in a];r=0
    for j in range(len(t[0])):
        pivot=next((i for i in range(r,len(t)) if t[i][j]),None)
        if pivot is None:continue
        t[r],t[pivot]=t[pivot],t[r]
        u=pow(t[r][j],-1,p);t[r]=[x*u%p for x in t[r]]
        for i in range(len(t)):
            if i!=r:
                c=t[i][j];t[i]=[(x-c*y)%p for x,y in zip(t[i],t[r])]
        r+=1
    return r

def finite():
    sources()
    counts=dict(ring_cases=0,positive_trace_zero_cases=0,conjugated_cases=0,controls=0)
    for p in (3,5):
        for w in (1,2):
            q=p**w
            for n in range(1,7):
                c=[row[::-1] for row in ident(n)]
                for r in range(1,n+1): # rank zero is separately an identity control
                    for variant in range(3):
                        t=chart(n,q,variant);ti=inverse(t,q)
                        b=[row[:r] for row in t];v=ti[:r]
                        pr=mul(b,v,q)
                        need(mul(v,b,q)==ident(r),"basis retraction")
                        need(mul(pr,pr,q)==pr,"projector premise")
                        pc=mul(pr,c,q);cp=mul(c,pr,q)
                        d=block(sub(ident(n),pr,q),pc,cp,sub(ident(n),mul(cp,c,q),q))
                        u=neg(b,q)+mul(c,b,q)
                        ww=[a+z for a,z in zip(v,neg(mul(v,c,q),q))]
                        ll=[a+[0]*n for a in neg(v,q)]
                        rr=b+[[0]*r for _ in range(n)]
                        f=sub(d,ident(2*n),q)
                        need(mul(u,ww,q)==f,"residual factorization")
                        need(mul(ll,u,q)==ident(r),"left retraction")
                        need(mul(ww,rr,q)==ident(r),"right retraction")
                        need(mul(d,d,q)==ident(2*n),"address involution")
                        need(rank_mod(f,p)==r,"residual residue rank")
                        need(rank_mod(pr,p)==r,"projector residue rank")
                        if r%p==0:
                            need(sum(pr[i][i] for i in range(n))%p==0,"trace-zero fixture")
                            counts["positive_trace_zero_cases"]+=1
                        s=chart(2*n,q,variant);si=inverse(s,q)
                        dc=mul(mul(s,d,q),si,q)
                        uc=mul(s,u,q);wc=mul(ww,si,q)
                        lc=mul(ll,si,q);rc=mul(s,rr,q)
                        need(mul(uc,wc,q)==sub(dc,ident(2*n),q),"conjugated residual")
                        need(mul(lc,uc,q)==ident(r) and mul(wc,rc,q)==ident(r),"conjugated retractions")
                        counts["ring_cases"]+=1;counts["conjugated_cases"]+=1
    q=9;b=[[1],[0]];v=[[1,0]];c=[[0,1],[1,0]]
    u=neg(b,q)+mul(c,b,q);ww=[v[0]+neg(mul(v,c,q),q)[0]]
    ll=[[-1%q,0,0,0]]
    need(mul(ll,b+mul(c,b,q),q)!=[[1]],"missing negative sign not exposed")
    counts["controls"]+=1
    badv=[[3,0]]
    need(mul(badv,b,q)!=[[1]],"missing VB identity not exposed")
    counts["controls"]+=1
    s=chart(4,q,2);si=inverse(s,q)
    need(mul(s,transpose(s),q)!=ident(4),"transpose alias fixture")
    need(mul(mul(ll,transpose(s),q),mul(s,u,q),q)!=[[1]],"transpose-as-inverse not exposed")
    counts["controls"]+=1
    badc=[[2,0],[0,2]]
    need(mul(badc,badc,q)!=ident(2),"C involution fixture")
    bad_d=block([[0,0],[0,0]],badc,badc,[[0,0],[0,0]])
    need(mul(bad_d,bad_d,q)!=ident(4),"missing C involution not exposed")
    counts["controls"]+=1
    need(sub(ident(4),ident(4),q)==[[0]*4 for _ in range(4)],"rank-zero residual")
    counts["controls"]+=1
    return {"status":"PASS_SPLIT_RESIDUAL_CONTROLS","formal_sha256":sha((P/"SplitResidual.lean").read_bytes()),**counts}

def audit(output):
    expected={"SplitResidual."+n for n in ROOTS}
    pattern=re.compile(r"^'([^']+)' (?:depends on axioms:\s*\[([^]]*)\]|does not depend on any axioms)\s*$",re.M)
    found={}
    for m in pattern.finditer(output):
        name,body=m.groups()
        need(name in expected and name not in found,"unexpected/duplicate axiom root")
        axioms=[] if body is None else [x.strip() for x in body.split(",")]
        need(set(axioms)<={"propext","Classical.choice","Quot.sound"},"forbidden axiom")
        found[name]=sorted(axioms)
    need(set(found)==expected,"missing axiom roots")
    need(not pattern.sub("",output).strip(),"unexpected audit output")
    return found

def live_lean(executable):
    lean=shutil.which(executable);need(lean,"Lean unavailable")
    version=subprocess.check_output([lean,"--version"],text=True,encoding="utf-8").strip()
    need("version 4.34.1" in version,"tested compiler is Lean4.34.1")
    formal=(P/"SplitResidual.lean").read_bytes()
    with tempfile.TemporaryDirectory(prefix="split-residual-") as temp:
        directory=Path(temp);env=os.environ.copy();env["LEAN_PATH"]=str(directory)
        def run(name,compile=False):
            cmd=[lean,"-j1","-DwarningAsError=true",name]
            if compile:cmd+=["-o",name.replace(".lean",".olean")]
            return subprocess.run(cmd,cwd=directory,env=env,text=True,encoding="utf-8",capture_output=True,timeout=120)
        (directory/"SplitResidual.lean").write_bytes(formal)
        result=run("SplitResidual.lean",True)
        need(result.returncode==0,"kernel compilation failed\n"+result.stdout+result.stderr)
        query="import SplitResidual\n"+"".join("#print axioms SplitResidual."+n+"\n" for n in ROOTS)
        (directory/"Audit.lean").write_bytes(query.encode())
        result=run("Audit.lean")
        need(result.returncode==0 and not result.stderr.strip(),"axiom command failed")
        axioms=audit(result.stdout)
        mutations=(
          ("wrong_lift_sign","(-B.apply a, C.apply (B.apply a))","(B.apply a, C.apply (B.apply a))"),
          ("omit_retraction","(hVB : ∀ a, V.apply (B.apply a) = a)","(hVB : True)"),
          ("wrong_right_section","(B.apply a, 0)","(0, B.apply a)"),
          ("omit_involution","(hCC : ∀ x, C.apply (C.apply x) = x)","(hCC : True)"))
        for name,old,new in mutations:
            need(old.encode() in formal,"mutation missing")
            (directory/"Mutation.lean").write_bytes(formal.replace(old.encode(),new.encode(),1))
            result=run("Mutation.lean")
            need(result.returncode!=0 and "error" in result.stdout.lower(),"mutated theorem accepted: "+name)
        bad="import Std\naxiom injected : False\n"
        bad+="theorem SplitResidual."+ROOTS[0]+" : False := injected\n"
        bad+="".join("theorem SplitResidual."+n+" : True := by trivial\n" for n in ROOTS[1:])
        bad+="".join("#print axioms SplitResidual."+n+"\n" for n in ROOTS)
        (directory/"BadAudit.lean").write_bytes(bad.encode());result=run("BadAudit.lean")
        need(result.returncode==0,"axiom rejection control failed to compile")
        try:audit(result.stdout)
        except ValueError:pass
        else:raise ValueError("forbidden axiom accepted")
    return {"version":version,"roots":len(ROOTS),"axioms":axioms,"rejected_mutations":[m[0] for m in mutations],"formal_sha256":sha(formal)}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write",action="store_true")
    parser.add_argument("--lean")
    args=parser.parse_args()
    result=finite()
    if args.write:(P/"RESULT.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8",newline="\n")
    else:need(canonical(result)==canonical(json.loads((P/"RESULT.json").read_bytes())),"receipt mismatch")
    if args.lean:print("PASS_LIVE_LEAN "+canonical(live_lean(args.lean)))
    print(canonical(result))
if __name__=="__main__":main()
