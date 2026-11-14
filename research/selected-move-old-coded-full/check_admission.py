"""Independent exact algebra; no retained factor/verifier imports.
Prepared for @CubeJerry with OpenAI assistance. Apache-2.0.
Finite checks corroborate the universal proof in ADMISSION-REVIEW.md.
"""
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import argparse
import copy
import gzip
import json
ZERO=(F(0),F(0)); ONE=(F(1),F(0))
def need(ok,message):
    if not ok: raise ValueError(message)
def add(x,y): return x[0]+y[0],x[1]+y[1]
def mul(x,y): return x[0]*y[0]-x[1]*y[1],x[0]*y[1]+x[1]*y[0]
def rotate(z,p):
    a,b=z
    return ((a,b),(-b,a),(-a,-b),(b,-a))[p%4]
def combine(out,key,value):
    value=add(out.get(key,ZERO),value)
    if value==ZERO: out.pop(key,None)
    else: out[key]=value
def linear(rows,vector):
    result=[]
    for row in rows:
        total=0
        for i,value in enumerate(vector):
            if row>>i&1: total^=value
        result.append(total)
    return tuple(result)
def inverse_rows(rows):
    # Exhaust fixed nine-bit bijection, independently of source elimination.
    inv={}
    for x in range(512):
        y=sum(((r&x).bit_count()%2)<<i for i,r in enumerate(rows))
        need(y not in inv,'noninvertible binary map'); inv[y]=x
    cols=[inv[1<<i] for i in range(9)]
    return tuple(sum(((cols[j]>>i)&1)<<j for j in range(9)) for i in range(9))
def exponent(record,address,f):
    return (f*record['phase']
        +sum(c*a.bit_count() for c,a in zip(record['linear_Z4'],address))
        +2*sum((address[i]&address[j]).bit_count()
          for i in range(9) for j in range(i+1,9)
          if record['quadratic_rows'][i]>>j&1))%4
def monomial(values,record,f,inverse=False):
    result={}; offset=tuple(((record['offset']>>i)&1)*((1<<f)-1) for i in range(9))
    backwards=inverse_rows(record['matrix_rows']) if inverse else None
    for address,value in values.items():
        if inverse:
            target=linear(backwards,tuple(a^b for a,b in zip(address,offset)))
            changed=rotate(value,-exponent(record,target,f))
        else:
            target=tuple(a^b for a,b in zip(linear(record['matrix_rows'],address),offset))
            changed=rotate(value,exponent(record,address,f))
        need(target not in result,'monomial collision')
        if changed!=ZERO: result[target]=changed
    return result
def c_axis(values,axis):
    result={}
    for address,value in values.items():
        combine(result,address,mul(value,(F(1,2),F(1,2))))
        target=(address[0]^(1<<axis),)+address[1:]
        combine(result,target,mul(value,(F(1,2),F(-1,2))))
    return result
def lowered_move(values,recipe,f):
    result=monomial(values,recipe['right'],f)
    for j in range(f): result=c_axis(result,j)
    return monomial(result,recipe['left'],f)
def frame_quadratic(direction):
    # Canonical frame definition. Explicit finite spans establish basis
    # independence rather than either source's elimination implementation.
    cols=[]; span={0}
    for v in [direction]+[1<<i for i in range(9)]:
        if v not in span:
            cols.append(v); span|={x^v for x in tuple(span)}
    need(len(cols)==9 and len(span)==512,'frame basis')
    rows=tuple(sum(((c>>i)&1)<<j for j,c in enumerate(cols)) for i in range(9))
    inv=inverse_rows(rows)
    ic=[sum(((r>>i)&1)<<j for j,r in enumerate(inv)) for i in range(9)]
    q=tuple((1<<i)^sum(((a&b).bit_count()%2)<<j for j,b in enumerate(ic)) for i,a in enumerate(ic))
    def value(x):
        return (sum((q[i]>>i)&1 for i in range(9) if x>>i&1)
            +2*sum((q[i]>>j)&1 for i in range(9) for j in range(i+1,9)
                    if x>>i&1 and x>>j&1))%4
    return rows,q,value
def native_frame(values,direction,f):
    # F([u])=D_Q P_G C_0 P_G^-1 D_Q^*. Diagonal (1+i)/2;
    # shifted coefficient ((1-i)/2)*i^(q(x XOR u)-q(x)).
    # No lowered recipe/helper is used by this oracle.
    _,_,q=frame_quadratic(direction); result=dict(values)
    for j in range(f):
        out={}
        for address,value in result.items():
            x=sum(((a>>j)&1)<<i for i,a in enumerate(address))
            combine(out,address,mul(value,(F(1,2),F(1,2))))
            target=tuple(a^((1<<j) if direction>>i&1 else 0) for i,a in enumerate(address))
            off=rotate(mul(value,(F(1,2),F(-1,2))),q(x^direction)-q(x))
            combine(out,target,off)
        result=out
    return result
def integral(values): return all(v.denominator==1 for z in values.values() for v in z)
def symmetric(values,bound): return all(abs(v)<=bound for z in values.values() for v in z)
def serialize(values):
    return [{'address':list(k),'real':str(z[0]),'imag':str(z[1])} for k,z in sorted(values.items())]
def audit(package):
    raw=(package/'inputs/core/reference/RECIPE.json').read_bytes()
    need(sha256(raw).hexdigest()=='96fadb44c3316be93c6c02f50cd2c841a9541d67b98fd94fc47b73fa64dd404c','recipe pin')
    record=json.loads(raw); recipe=record['lowered_recipe']
    witness=json.loads((package/'inputs/core/reference/SOURCE-FRAMES.json').read_text())
    need(record['native_event_index']==witness['event_index']==24472,'event index')
    need(record['event']==witness['event']==['MOVE',415,3,99,False],'source event')
    need(witness['frames']=={'3':[],'99':[239]},'complete source frames')
    for x in range(512):
        values={tuple((x>>i)&1 for i in range(9)):ONE}
        need(lowered_move(values,recipe,1)==native_frame(values,239,1),'source column '+str(x))
    for a in [(0,)*9,(3,)*9,(1,0,2,3,1,0,2,3,1),(2,1,0,3,2,1,0,3,2)]:
        need(lowered_move({a:ONE},recipe,2)==native_frame({a:ONE},239,2),'tensor column')
    wrong=copy.deepcopy(recipe); wrong['right']['phase']=(wrong['right']['phase']+1)%4
    need(lowered_move({(0,)*9:ONE},wrong,1)!=native_frame({(0,)*9:ONE},239,1),'phase mutation missed')
    need(lowered_move({(0,)*9:ONE},recipe,1)!=native_frame({(0,)*9:ONE},238,1),'frame mutation missed')
    a=(1,0,0,0,0,0,0,1,0); source={a:(F(-2),F(0))}
    need(exponent(recipe['right'],a,1)==2,'phase exponent')
    phase_value=rotate(source[a],2); need(phase_value==(F(2),F(0)),'signed negation')
    target=native_frame(source,239,1)
    need(target==lowered_move(source,recipe,1),'phase witness source binding')
    need(integral(target) and symmetric(target,1),'phase witness endpoints')
    physical=sum(v<<(8-i) for i,v in enumerate(a)); need(physical==258,'MSB address')
    central={(0,)*9:ONE,(3,)+(0,)*8:ONE}
    entrance=monomial(central,recipe['right'],2,inverse=True)
    need(monomial(entrance,recipe['right'],2)==central,'inverse right')
    first=c_axis(central,0); last=c_axis(first,1)
    need(not integral(first),'fractional prefix not detected')
    need(last=={(1,)+(0,)*8:ONE,(2,)+(0,)*8:ONE},'central endpoint')
    endpoint=monomial(last,recipe['left'],2)
    need(integral(entrance) and integral(endpoint) and symmetric(entrance,1) and symmetric(endpoint,1),'symmetric integral endpoints')
    need(endpoint==native_frame(entrance,239,2),'prefix witness source binding')
    depths=0
    for n in range(1,2049):
        for t in range((n-1)//356+1):
            need((n+1)//2+178*t<=n,'grid depth inequality')
            need((n+2)//2+161*t+1<=n+2,'width depth inequality'); depths+=1
    rows,q,_=frame_quadratic(239)
    return {'marker':'PASS_FULL_MOVE_ADMISSION_CONTROLS',
        'base':'e54523517d0f03e58352e647c403a5af3e525a57',
        'source_index':24472,'source_event':witness['event'],
        'source_basis_checks':512,'two_column_basis_checks':4,
        'source_chart_rows':rows,'source_quadratic_rows':q,
        'source_oracle':'direct canonical-frame conjugation, no factor imports',
        'phase_overflow':{'f':1,'w':2,'physical_address':physical,
            'native_input':serialize(source),'phase_value':[str(x) for x in phase_value],
            'complete_native_output':serialize(target)},
        'nonintegral_prefix':{'f':2,'w':2,'native_input':serialize(entrance),
            'central_entrance':serialize(central),'first_prefix':serialize(first),
            'complete_native_output':serialize(endpoint)},
        'depth_checks':{'n_min':1,'n_max':2048,'pairs':depths,'meaning':'finite corroboration only'},
        'negative_controls':['changed absolute phase','changed source frame',
            'minimum-signed phase overflow','integral endpoints with nonintegral prefix']}
if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--package',type=Path,required=True)
    parser.add_argument('--output',type=Path); parser.add_argument('--archive',type=Path)
    args=parser.parse_args()
    result=audit(args.package.resolve())
    result['complete_archive_reextracted']=False
    if args.archive:
        raw=args.archive.read_bytes()
        need(len(raw)==350722,'archive length')
        need(sha256(raw).hexdigest()=='2b94953dc14a122e3ef089633f05b58ec689ec5156feb7c784ed3e137dc01883','archive hash')
        word=json.loads(gzip.decompress(raw))
        canonical=json.dumps(word,separators=(',',':'),sort_keys=True).encode()
        need(sha256(canonical).hexdigest()=='91429a6b96729292a8764836e00c87a6f7cd3b76f05159033f4867f69a98d097','canonical source hash')
        need(word['program'][24472]==result['source_event'],'actual source event')
        need(word['frames'][3]==[] and word['frames'][99]==[239],'actual complete frames')
        result['complete_archive_reextracted']=True
    if args.output: args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(result['marker'])
    print('512 source columns; 4 tensor columns; 2 numerical obstructions; '+str(result['depth_checks']['pairs'])+' bounded depth pairs')
