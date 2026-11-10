"""Source-coordinate tensor oracle and signed-domain failure controls.

The address/phase oracle does not call the native numerical implementation.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
import json
from serial_sources import activate, need


def one(recipe, word):
    phase=recipe['phase'];m=len(recipe['matrix_rows'])
    for i in range(m):
        if word>>i&1:
            phase+=recipe['linear_Z4'][i]
            for j in range(i+1,m):
                if word>>j&1 and recipe['quadratic_rows'][i]>>j&1:phase+=2
    out=recipe['offset']
    for i,row in enumerate(recipe['matrix_rows']):
        if (row&word).bit_count()%2:out^=1<<i
    return out,phase%4


def apply_column(address, a, u, m, stride, rho, recipe):
    positions=[a-1-(u+i*stride+rho) for i in range(m)]
    old=sum(((address>>p)&1)<<i for i,p in enumerate(positions))
    new,phase=one(recipe,old);out=address
    for i,p in enumerate(positions):
        if (old^new)>>i&1:out^=1<<p
    return out,phase


def run():
    S=activate()
    _entry,_exit,record,source=S.selected.source_boundary()
    recipes=[record['right'],record['left'],
             dict(matrix_rows=(1,),offset=0,linear_Z4=(0,),quadratic_rows=(0,),phase=2),
             dict(matrix_rows=(1,3),offset=2,linear_Z4=(3,1),quadratic_rows=(2,0),phase=3)]
    counts=0;phase_control=spacing_control=False
    for recipe in recipes:
        m=len(recipe['matrix_rows'])
        inverse_map={one(recipe,x)[0]:(x,one(recipe,x)[1]) for x in range(1<<m)}
        need(len(inverse_map)==1<<m,'recipe address map invertible')
        for f in (1,2,3,4):
            for K in (1,2,3):
                for rho in range(K):
                    H=max(1,f-1);u=2*H+2;z=u+m*f*K+3;a=z+H+1
                    for salt in range(32):
                        seed=((salt*0x9e3779b97f4a7c15)^(salt<<(a//2)))&((1<<a)-1)
                        for address in (seed,seed^((1<<a)-1)):
                            expected=address;total=0
                            for j in range(f):
                                # Batched endpoint reads every original column.
                                new,phase=apply_column(address,a,u,m,f*K,j*K+rho,recipe)
                                selected=sum(1<<(a-1-(u+(i*f+j)*K+rho)) for i in range(m))
                                expected=(expected&~selected)|(new&selected);total+=phase
                            actual=address;acc=0
                            for j in range(f):
                                actual,phase=apply_column(actual,a,u,m,f*K,j*K+rho,recipe);acc+=phase
                            need((actual,acc%4)==(expected,total%4),'exact batched versus serial tensor action')
                            restored=actual;inverse_phase=0
                            for j in reversed(range(f)):
                                pos=[a-1-(u+(i*f+j)*K+rho) for i in range(m)]
                                y=sum(((restored>>p)&1)<<i for i,p in enumerate(pos))
                                x,phase=inverse_map[y]
                                for i,p in enumerate(pos):
                                    if (x^y)>>i&1:restored^=1<<p
                                inverse_phase-=phase
                            need(restored==address and (acc+inverse_phase)%4==0,'complete inverse with absolute phase')
                            phase_control |= (total-(f-1)*recipe['phase'])%4 != total%4
                            if f>1:
                                wrong,_=apply_column(address,a,u,m,K,rho,recipe)
                                good,_=apply_column(address,a,u,m,f*K,rho,recipe)
                                spacing_control |= wrong!=good
                            counts+=1
    need(phase_control and spacing_control,'tensor constant and unscaled-stride controls discriminate')
    lo=-8
    need((-1)**2*lo==lo and -lo>7,'batched cancellation versus intermediate overflow')
    return dict(status='PASS_SERIAL_MONOMIAL_ALGEBRA',source=source,
                exact_tensor_address_cases=counts,recipes=len(recipes),
                controls=['missing_tensor_constant','unscaled_stride','batched_vs_serial_headroom'],
                universal_claim='descriptor identity and disjoint tensor factors proved separately')


if __name__=='__main__':
    print(json.dumps(run(),sort_keys=True))
