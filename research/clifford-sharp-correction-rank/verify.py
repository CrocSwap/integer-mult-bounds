"""Exact sharp nonreciprocal correction rank; standard library, no floats."""
import argparse
import hashlib
import importlib.util
import json
from math import comb
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
KERNEL = 'research/complex-multicold/vendor/pr558/vendor/pr552/complex-global/vendor531/vendor/clifford/clifford_exact.py'
Z, ONE = (0,0), (1,0)

def need(ok, why):
    if not ok:
        raise ValueError(why)

def add(x,y): return x[0]+y[0], x[1]+y[1]
def sub(x,y): return x[0]-y[0], x[1]-y[1]
def mul(x,y): return x[0]*y[0]-x[1]*y[1], x[0]*y[1]+x[1]*y[0]
def phase(x,u):
    a,b = x
    return ((a,b),(-b,a),(-a,-b),(b,-a))[u%4]

def walsh(v):
    v, step = list(v), 1
    while step < len(v):
        for start in range(0,len(v),2*step):
            for j in range(start,start+step):
                a,b = v[j],v[j+step]
                v[j],v[j+step] = add(a,b),sub(a,b)
        step *= 2
    return v

def multiplicities(h,direction=1,u=0):
    out = [0]*4
    for k in range(h+1): out[(u+direction*k)%4] += comb(h,k)
    return out

def minimum(s):
    if s == 0: return 0
    return (1 << (s-1)) - (0 if s%2 else 1 << ((s-2)//2))

def construction(s,u,direction=1):
    """S diagonalizes F_spec D to q copies of diag(1,i)."""
    h,n = s+1,1 << (s+1)
    groups = [[j for j in range(n) if (u+direction*j.bit_count())%4 == k] for k in range(4)]
    one,imag = [{j:ONE} for j in groups[0]],[{j:ONE} for j in groups[1]]
    pairs = list(zip(groups[2],groups[3]))
    for a,b in pairs:
        one.append({a:ONE,b:(1,-1)})
        imag.append({a:(2,0),b:(1,-1)})
    sign_one,sign_imag = groups[2][len(pairs):],groups[3][len(pairs):]
    one += [{j:ONE} for j in sign_one]
    imag += [{j:ONE} for j in sign_imag]
    need(len(one) == len(imag) == n//2,'complete target eigenbasis')
    spec = {'s':s,'h':h,'phase':u,'direction':direction,'dimension':n,
            'multiplicities':list(map(len,groups)),'pairs':pairs,'signs':sign_one+sign_imag,
            'rank':max(len(groups[2]),len(groups[3]))}
    columns = []
    for a,b in zip(one,imag):
        va,vb = [a.get(j,Z) for j in range(n)],[b.get(j,Z) for j in range(n)]
        columns.extend([walsh([add(x,y) for x,y in zip(va,vb)]),
                        walsh([sub(x,y) for x,y in zip(va,vb)])])
    # Gaussian integer numerators of E=W_h S (I_q tensor W_1)/2.
    return spec,columns

def correct(v,spec,wrong_sign=False,drop_last=False):
    out = list(v)
    pairs = spec['pairs'][:-1] if drop_last else spec['pairs']
    for a,b in pairs:
        delta = mul((0,-2 if wrong_sign else 2),sub(v[b],v[a]))
        out[a],out[b] = add(v[a],delta),add(v[b],delta)
    for j in spec['signs']: out[j] = (-v[j][0],-v[j][1])
    return out

def child(v,h,direction,u):
    out = list(v)
    for axis in range(h):
        out = [add(mul((1,direction),out[j]),mul((1,-direction),out[j^(1<<axis)])) for j in range(len(v))]
    return [phase(x,u) for x in out]  # denominator 2^h

def identity(spec,columns,fault=None):
    h,n = spec['h'],spec['dimension']
    for j,v in enumerate(columns):
        actual = child(v,h,spec['direction'],spec['phase']+(fault=='wrong_phase'))
        actual = walsh(correct(walsh(actual),spec,wrong_sign=fault=='wrong_shear',drop_last=fault=='missing_shear'))
        expected = [add(mul((1,1),a),mul((1,-1),b)) for a,b in zip(columns[j],columns[j^1])]
        # F_H H E denominator 2^(2h+1); E T denominator four.
        factor = 1 << (2*h-1)
        if actual != [(a*factor,b*factor) for a,b in expected]: return False
    return True

def rank_mod(columns,denominator=1,p=65537):
    # i=256; a nonzero modular minor is also nonzero over Q(i).
    a = [[(x+256*y)*pow(denominator,-1,p)%p for x,y in row] for row in zip(*columns)]
    pivot = 0
    for j in range(len(a[0])):
        k = next((k for k in range(pivot,len(a)) if a[k][j]),None)
        if k is None: continue
        a[pivot],a[k] = a[k],a[pivot]
        z = pow(a[pivot][j],-1,p)
        a[pivot] = [v*z%p for v in a[pivot]]
        for k in range(pivot+1,len(a)):
            z = a[k][j]
            if z: a[k] = [(x-z*y)%p for x,y in zip(a[k],a[pivot])]
        pivot += 1
    return pivot

def correction_columns(spec):
    n = spec['dimension']
    return [walsh(correct(walsh([ONE if i==j else Z for i in range(n)]),spec)) for j in range(n)]

def authenticate():
    raw = {}
    for row in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if row.get('usage') != 'input': continue
        data = (ROOT/row['path']).read_bytes()
        need(hashlib.sha256(data).hexdigest()==row['sha256'],'source SHA256 '+row['path'])
        need(hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==row['git_blob'],'source Git blob')
        raw[row['path']] = data
    return raw

def native_kernel(raw):
    spec = importlib.util.spec_from_file_location('sharp_rank_pinned_clifford',ROOT/KERNEL)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    exec(compile(raw[KERNEL],str(ROOT/KERNEL),'exec',optimize=0),module.__dict__)
    return module

def witness():
    spec,enc = construction(4,2)
    return dict(spec,encoding_denominator=2,encoding_columns=enc,
                correction_denominator=32,correction_columns=correction_columns(spec))

def run():
    native = native_kernel(authenticate())
    recurrence,digest = [1,0,0,0],hashlib.sha256()
    cases,dense,entries = [],[],0
    for h in range(1,130):
        recurrence = [recurrence[j]+recurrence[(j-1)%4] for j in range(4)]
        need(recurrence==multiplicities(h),'independent cyclic spectrum recurrence')
        s,best = h-1,[]
        for direction in (1,-1):
            for u in range(4):
                m = multiplicities(h,direction,u)
                need(m[0]+m[2]==m[1]+m[3]==1<<(h-1),'opposite multiplicity balance')
                r = max(m[2],m[3])
                need(r==max(abs((1<<(h-1))-m[0]),abs((1<<(h-1))-m[1]),m[2],m[3]),'phase-specific discrepancy')
                best.append(r)
                digest.update(json.dumps([s,direction,u,m,r]).encode())
        need(min(best)==minimum(s),'closed all-size formula corroboration')
        cases.append({'s':s,'minimum':minimum(s),'phase_ranks_forward':best[:4]})
    for s in range(6):
        h,n = s+1,1<<(s+1)
        for direction in (1,-1):
            op = native.fourier(h)
            if direction==-1: op=op.adjoint()
            for j in range(n):
                exact,exp = op.zero_state(j)
                our = child([ONE if i==j else Z for i in range(n)],h,direction,0)
                need(our==[(a*(1<<(h-exp)),b*(1<<(h-exp))) for a,b in exact],'pinned complete native child')
                entries += n
            for u in range(4):
                spec,enc = construction(s,u,direction)
                need(identity(spec,enc),'complete encoded operator identity')
                need(rank_mod(enc,2)==n,'encoding invertibility minor')
                fc = correction_columns(spec)
                delta = [[sub(x,(n,0) if i==j else Z) for i,x in enumerate(col)] for j,col in enumerate(fc)]
                need(rank_mod(delta,n)==spec['rank'],'modular correction rank')
                need(rank_mod(fc,n)==n,'correction invertibility')
                dense.append({'s':s,'phase':u,'direction':direction,'rank':spec['rank'],
                              'pairs':len(spec['pairs']),'signs':len(spec['signs']),'columns':n})
    spec,enc = construction(4,2)
    controls = []
    for fault in ('wrong_phase','wrong_shear','missing_shear'):
        need(not identity(spec,enc,fault),'ineffective control '+fault)
        controls.append(fault)
    need(spec['rank']==6 and len(spec['pairs'])==6 and not spec['signs'],'six-shear attainer')
    need(multiplicities(5)==[6,6,10,10],'PR1920 predecessor spectrum')
    need([max(multiplicities(5,1,u)[2:]) for u in range(4)]==[10,10,6,10],'PR1920 lower bounds')
    return {'status':'PASS_SHARP_CLIFFORD_CORRECTION_RANK','spectrum_cases':1032,'s_range':[0,128],
            'spectrum_sha256':digest.hexdigest(),'first_cases':cases[:17],
            'complete_operator_fixtures':dense,'native_entries':entries,
            'sixteen_lane':{'dimension':32,'phase':2,'host_width':5,'minimum_correction_rank':6,
                            'rank_one_shears':6,'singleton_signs':0},'controls':controls,
            'scope':'Exact algebraic correction rank; no native adapter tariff, supplier or new kappa.'}

def encoded(obj): return json.dumps(obj,sort_keys=True,indent=2)+'\n'

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write',type=Path)
    args = ap.parse_args()
    result = run()
    if args.write:
        with args.write.open('x',encoding='utf-8',newline='\n') as f: f.write(encoded(result))
    else:
        need((HERE/'RESULT.json').read_text(encoding='utf-8')==encoded(result),'committed exact receipt')
        need((HERE/'WITNESS.json').read_text(encoding='utf-8')==encoded(witness()),'committed full witness')
    print('PASS_SHARP_CLIFFORD_CORRECTION_RANK spectra=1032 full_operators=48 sharp_rank=6')

if __name__=='__main__': main()
