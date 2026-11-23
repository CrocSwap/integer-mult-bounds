"""Independent rational realification; does not import author audit.py."""
from fractions import Fraction as F
from hashlib import sha1, sha256
from pathlib import Path
import argparse, importlib, json, sys, time
PROOF_SHA='162dd4bb7a020dfb72dd3c80cb9a1de37212cc7f812f36fd4365d487d49b341b'
def need(ok,why):
    if not ok:raise ValueError(why)
def eye(n):return [[F(i==j) for j in range(n)] for i in range(n)]
def zero(n,m=None):return [[F(0)]*(n if m is None else m) for _ in range(n)]
def trans(a):return [list(r) for r in zip(*a)]
def add(a,b,s=1):return [[x+s*y for x,y in zip(r,t)] for r,t in zip(a,b)]
def scale(a,s):return [[s*x for x in r] for r in a]
def block(a,i,j,n,m):return [r[j:j+m] for r in a[i:i+n]]
def join(a,b,c,d):return [r+s for r,s in zip(a,b)]+[r+s for r,s in zip(c,d)]
def diag(a,b):return join(a,zero(len(a),len(b)),zero(len(b),len(a)),b)
def mm(a,b):
    out=zero(len(a),len(b[0]))
    for i,r in enumerate(a):
        for k,x in enumerate(r):
            if x:
                for j,y in enumerate(b[k]):
                    if y:out[i][j]+=x*y
    return out
def inv(a):
    n=len(a);r=[list(map(F,row))+eye(n)[i] for i,row in enumerate(a)]
    for k in range(n):
        piv=[j for j in range(k,n) if r[j][k]];need(piv,'singular matrix rejected')
        j=piv[-1];r[k],r[j]=r[j],r[k];s=r[k][k];r[k]=[x/s for x in r[k]]
        for j in range(n):
            if j!=k and r[j][k]:
                s=r[j][k];r[j]=[x-s*y for x,y in zip(r[j],r[k])]
    return [row[n:] for row in r]
def frob2(a):return sum(x*x for row in a for x in row)
def envelope(a):return max(max(sum(abs(x) for x in r) for r in a),max(sum(abs(x) for x in c) for c in zip(*a)))
def realify(a):
    out=zero(2*len(a),2*len(a[0]))
    for i,row in enumerate(a):
        for j,z in enumerate(row):
            x,y=(F(z.re),F(z.im)) if hasattr(z,'re') else (F(z),F(0))
            out[2*i][2*j]=x;out[2*i][2*j+1]=-y;out[2*i+1][2*j]=y;out[2*i+1][2*j+1]=x
    return out
def gate_left(a,ids,g):
    out=[r[:] for r in a];updated=mm(g,[a[i] for i in ids])
    for i,r in zip(ids,updated):out[i]=r
    return out
def word(layers,n,reverse=False):
    out=eye(n)
    for layer in (reversed(layers) if reverse else layers):
        for ids,g in (reversed(layer) if reverse else layer):out=gate_left(out,ids,inv(g) if reverse else g)
    return out
def triangular_certificate(a,ai,m):
    u=block(a,0,0,m,m);v=block(a,m,m,m,m);x=block(a,m,0,m,m)
    need(block(a,0,m,m,m)==zero(m),'upper block not zero')
    need(mm(trans(u),u)==eye(m) and mm(trans(v),v)==eye(m),'bank block not orthogonal')
    need(ai==join(trans(u),zero(m),scale(mm(mm(trans(v),x),trans(u)),-1),trans(v)),'inverse bank formula failed')

def primitives(retained):
    sys.path.insert(0,str(retained));ex=importlib.import_module('exact');en=importlib.import_module('engine')
    source=(retained/'check_circuits.py').read_text();oracle=(retained/'interval_kernel.py').read_text()
    count=0;proper=0;wrong=0;classes=0;intervals=0;cases=[]
    for n in (1,2,4):
        builder=en.Builder(en.Phases(4,oracle),4,source)
        first=[ex.C(F(1,4),F(1,8))]+[ex.C(F(1,j+4)) for j in range(1,n)]
        top=[first[0]]+[ex.C(-F(1,j+6),F(1,16)) for j in range(1,n)]
        mat=ex.Mat([[first[i-j] if i>=j else top[j-i] for j in range(n)] for i in range(n)])
        raw=builder.plan(mat);layers=[];cross=0
        for layer in raw:
            used=set();converted=[];kinds=[]
            for ids,g in layer:
                need(not used.intersection(ids),'overlapping matching');used.update(ids)
                rr=realify(g);converted.append((tuple(k for i in ids for k in (2*i,2*i+1)),rr))
                if all(i<n for i in ids) or all(i>=n for i in ids):
                    need(mm(trans(rr),rr)==eye(len(rr)),'nonunitary bank gate');kinds.append('unitary')
                else:
                    need(len(ids)==2 and ids[0]<n<=ids[1],'wrong cross-bank direction')
                    need(block(rr,0,0,2,2)==eye(2) and block(rr,0,2,2,2)==zero(2) and block(rr,2,2,2,2)==eye(2),'not lower shear')
                    lam=g[1][0];cap=builder.spectra[cross]['bound']+F(1,16)
                    need(F(lam.re)**2+F(lam.im)**2<=cap**2,'multiplier bound fails');kinds.append('shear')
                classes+=1
            need(not kinds or len(set(kinds))==1,'mixed matching alphabet')
            if kinds and kinds[0]=='shear':cross+=1
            layers.append(converted)
        need(cross==2,'wrong spectral matching count');total=word(layers,4*n);local=0
        for k,layer in enumerate(layers):
            for mask in range(1<<len(layer)):
                sel=[g for j,g in enumerate(layer) if mask>>j&1];rest=[g for j,g in enumerate(layer) if not mask>>j&1]
                pre=layers[:k]+[sel];suf=[rest]+layers[k+1:]
                p=word(pre,4*n);pi=word(pre,4*n,True);s=word(suf,4*n);si=word(suf,4*n,True)
                triangular_certificate(p,pi,2*n);triangular_certificate(s,si,2*n)
                need(mm(s,p)==total,'cut chronology wrong')
                need(mm(pi,p)==eye(4*n) and mm(si,s)==eye(4*n),'four-way inverse fails')
                count+=1;local+=1
                if mask not in (0,(1<<len(layer))-1):proper+=1
                if mm(p,s)!=total:wrong+=1
        flat=[[g] for layer in layers for g in layer];points=sorted({0,1,2,len(flat)//3,len(flat)//2,len(flat)-2,len(flat)-1,len(flat)})
        for a in points:
            for b in points:
                if not a<=b:continue
                segment=word(flat[a:b],4*n);si=word(flat[a:b],4*n,True)
                triangular_certificate(segment,si,2*n)
                need(segment==mm(word(flat[:b],4*n),word(flat[:a],4*n,True)),'arbitrary interval endpoint identity fails');intervals+=1
        cases.append({'bank_width':n,'layers':len(layers),'cuts':local,'envelope':str(1+sum(F(r['bound']) for r in builder.spectra)+F(1,8))})
    need(wrong>0,'reversed source order not distinguished')
    return dict(cases=cases,cuts=count,proper_sublayer_cuts=proper,four_way_certificates=4*count,classified_source_gates=classes,wrong_order_witnesses=wrong,arbitrary_intervals=intervals)

def compensated():
    p=[[F(1),F(1,5)],[F(1,7),F(1)]];h=[[F(2),F(1)],[-F(1),F(3)]]
    a=[[F(1),F(0)],[F(1,4),F(1)]];rem=[[F(1,5),F(1,3)],[F(1,9),-F(1,8)]]
    i=eye(2);z=zero(2);pi=inv(p)
    def low(b,d):return join(b,z,d,i)
    def shear(x):return low(i,x)
    hp=mm(h,p);term=mm(h,add(p,i,-1));c=add(term,rem)
    steps=[diag(p,i),shear(h),diag(pi,i),shear(scale(h,-1))]
    pres=[low(p,a),low(p,add(a,hp)),shear(add(a,hp)),shear(add(a,term))]
    sufs=[low(pi,mm(c,pi)),low(pi,add(mm(c,pi),h,-1)),shear(add(c,hp,-1)),shear(add(c,term,-1))]
    total=shear(add(a,c));prefix=shear(a)
    for g,ep,es in zip(steps,pres,sufs):
        prefix=mm(g,prefix);suffix=mm(total,inv(prefix))
        need(prefix==ep and suffix==es,'compensated checkpoint formula failed')
        need(mm(suffix,prefix)==total,'checkpoint order wrong')
        need(mm(inv(prefix),prefix)==eye(4) and mm(inv(suffix),suffix)==eye(4),'checkpoint inverse fails')
    need(mm(steps[3],mm(steps[1],steps[0]))!=shear(term),'missing paired inverse accepted')
    bad=mm(shear(add(scale(h,-1),[[F(1,32),F(0)],[F(0),F(0)]])),mm(steps[2],mm(steps[1],steps[0])))
    need(bad!=shear(term),'unpaired compensation accepted')
    need(mm(steps[0],steps[1])!=mm(steps[1],steps[0]),'reversed term order not detected')
    return dict(checkpoint_identities=16,missing_inverse_rejected=True,unpaired_compensation_rejected=True,wrong_order_rejected=True)

def normalized_suffixes():
    ideal=[[[F(1),F(1,5)],[F(0),F(1)]],[[F(1),F(0)],[F(1,7),F(1)]],[[F(3,2),F(0)],[F(0),F(2,3)]],[[F(1),-F(1,11)],[F(0),F(1)]]]
    errors=[[[F(1,1000*(j+1)),F(1,2000)],[F(0),-F(1,3000)]] for j in range(4)]
    q=[eye(2)];stored=[eye(2)];normalized=[]
    for a,e in zip(ideal,errors):
        q.append(mm(a,q[-1]));normalized.append(add(eye(2),mm(mm(inv(q[-1]),e),q[-2])))
        stored.append(mm(add(a,e),stored[-1]))
    wrong=0
    for j in range(5):
        w=eye(2)
        for g in normalized[j:]:w=mm(g,w)
        actual=mm(stored[-1],inv(stored[j]));expected=mm(mm(q[-1],w),inv(q[j]))
        need(actual==expected,'normalized suffix must use one consecutive product')
        need(inv(actual)==mm(mm(q[j],inv(w)),inv(q[-1])),'normalized inverse suffix failed')
        wr=eye(2)
        for g in reversed(normalized[j:]):wr=mm(g,wr)
        wrong+=wr!=w
    need(wrong>0,'normalized noncommuting factors fail to distinguish reversal')
    return dict(suffix_identities=5,inverse_suffix_identities=5,reversed_product_witnesses=wrong)

def negative_controls():
    tiny=[[F(1,1024)]];wrong_b=F(256);need(inv(tiny)[0][0]>wrong_b,'unclamped conditioning control fails')
    m=F(8);p0=[[m,F(0)],[F(1),1/m]];g=[[1/m,F(0)],[F(0),m]];p1=mm(g,p0);partial=[[F(1),F(0)],[F(0),m]];cap=m+2
    need(all(frob2(a)<=cap*cap for a in (p0,inv(p0),g,inv(g),p1,inv(p1))),'generic control endpoints not bounded')
    bad=mm(partial,p0);need(sum(row[0]**2 for row in bad)>cap*cap,'unpaired scaling control does not escape envelope')
    lower=[[F(1),F(0)],[F(2),F(1)]];upper=trans(lower);both=mm(upper,lower)
    need(sum(row[0]**2 for row in both)>25,'opposite directions fail to defeat additive envelope')
    splice=[[F(0),F(1)],[F(0),F(1)]];rejected=False
    try:inv(splice)
    except ValueError:rejected=True
    need(rejected,'split swap coordinate writes not singular')
    return dict(unclamped_conditioning={'lambda':'1/1024','Q':'1024','chi':'1','invalid_B':'256','actual_inverse_norm':'1024'},unpaired_scale={'endpoint_cap':str(cap),'intermediate_column_squared':str(sum(row[0]**2 for row in bad))},opposite_direction_shear={'false_cap':5,'column_squared':str(sum(row[0]**2 for row in both))},coordinate_write_swap_singular=True)

def downset_cases():
    results=[]
    for n in (1,2,4):
        atoms=[];nodes=[]
        def embed(a,offset):
            out=eye(n)
            for i,row in enumerate(a):out[offset+i][offset:offset+len(a)]=row
            return out
        def build(a,offset,parents):
            m=len(a);node={'size':m,'offset':offset,'a':a};nodes.append(node)
            if m==1:
                index=len(atoms);atoms.append({'matrix':embed(a,offset),'requires':set(parents)})
                node.update(ids={index},scalar=index,l=eye(1),u=eye(1),d=a);return node
            h=m//2;aa=block(a,0,0,h,h);bb=block(a,0,h,h,h);cc=block(a,h,0,h,h);dd=block(a,h,h,h,h)
            rr=mm(inv(aa),bb);ll=mm(cc,inv(aa));ss=add(dd,mm(cc,rr),-1)
            ur=join(eye(h),rr,zero(h),eye(h));lr=join(eye(h),zero(h),ll,eye(h))
            upper=len(atoms);atoms.append({'matrix':embed(ur,offset),'requires':set(parents)})
            left=build(aa,offset,set(parents)|{upper});right=build(ss,offset+h,set(parents)|{upper})
            lower=len(atoms);atoms.append({'matrix':embed(lr,offset),'requires':set(parents)|{upper}|left['ids']|right['ids']})
            node.update(ids={upper,lower}|left['ids']|right['ids'],upper=upper,lower=lower,left=left,right=right,ur=ur,l=mm(lr,diag(left['l'],right['l'])),d=diag(left['d'],right['d']),u=mm(diag(left['u'],right['u']),ur))
            need(mm(mm(node['l'],node['d']),node['u'])==a,'recursive LDU identity failed');return node
        first=[F(2)]+[F(1,8+j) for j in range(1,n)];top=[first[0]]+[-F(1,10+j) for j in range(1,n)]
        a=[[first[i-j] if i>=j else top[j-i] for j in range(n)] for i in range(n)];root=build(a,0,set())
        lam=max(F(1),max(envelope(t['a']) for t in nodes));qq=max(F(1),max(envelope(inv(t['a'])) for t in nodes));chi=lam*qq;b=256*n**3*chi**12
        def factors(t,selected):
            m=t['size']
            if t['ids']<=selected:return t['l'],t['d'],t['u'],eye(m)
            if m==1 or t['upper'] not in selected:return eye(m),eye(m),eye(m),t['u']
            l1,d1,u1,f1=factors(t['left'],selected);l2,d2,u2,f2=factors(t['right'],selected)
            return diag(l1,l2),diag(d1,d2),mm(diag(u1,u2),t['ur']),diag(f1,f2)
        count=0
        for mask in range(1<<len(atoms)):
            selected={j for j in range(len(atoms)) if mask>>j&1}
            if any(not atoms[j]['requires']<=selected for j in selected):continue
            p=eye(n)
            for j,g in enumerate(atoms):
                if j in selected:p=mm(g['matrix'],p)
            ll,dd,uu,frontier=factors(root,selected)
            need(mm(mm(ll,dd),uu)==p,'downset LDU factorization failed')
            need(mm(frontier,uu)==root['u'],'unvisited upper frontier identity failed')
            need(mm(mm(inv(uu),inv(dd)),inv(ll))==inv(p),'downset inverse order failed')
            need(frob2(p)<=b*b and frob2(inv(p))<=b*b,'old downset envelope not sufficient')
            count+=1
        need(count>1,'no nontrivial downsets checked')
        results.append({'n':n,'atoms':len(atoms),'all_downsets':count,'lambda_envelope':str(lam),'inverse_envelope':str(qq),'old_B':str(b)})
    return {'cases':results,'downsets':sum(r['all_downsets'] for r in results)}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--source',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();start=time.monotonic()
    source=args.source.resolve();proof=(source/'PROOF.md').read_bytes();need(sha256(proof).hexdigest()==PROOF_SHA,'reviewed proof changed')
    origins=json.loads((source/'ORIGINS.json').read_text());checked=[]
    for item in origins['files']:
        data=(source/item['local']).read_bytes();need(len(data)==item['bytes'],'source size changed')
        need(sha256(data).hexdigest()==item['sha256'],'source SHA256 changed')
        need(sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==item['git_blob'],'source Git blob changed');checked.append(item['local'])
    result={'status':'PASS_INDEPENDENT_SOURCE_ALPHABET_CUT_REVIEW','proof_sha256':PROOF_SHA,'source_commit':origins['base_commit'],'source_files':checked,'method':'Own Fraction realification, reverse-pivot inverses, gate-word multiplication, recursive LDU downsets; imports retained coefficient factory only; never imports audit.py.'}
    result['primitive_cuts']=primitives(source/'retained');result['compensated_generator']=compensated();result['normalized_suffixes']=normalized_suffixes();result['downsets']=downset_cases();result['negative_controls']=negative_controls()
    need(sha256((source/'PROOF.md').read_bytes()).hexdigest()==PROOF_SHA,'proof changed during review');result['seconds']=round(time.monotonic()-start,3)
    args.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':result['status'],'cuts':result['primitive_cuts']['cuts'],'downsets':result['downsets']['downsets'],'seconds':result['seconds']}))
if __name__=='__main__':main()
