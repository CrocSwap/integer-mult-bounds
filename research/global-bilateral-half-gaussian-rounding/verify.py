"""Check the public kernel against separately written code and exact obligations."""
from pathlib import Path
from types import ModuleType
from itertools import product
import hashlib,json,random,io,contextlib
ROOT=Path(__file__).resolve().parent

def load_source(name,path):
    module=ModuleType(name);module.__file__=str(path)
    exec(compile(path.read_bytes(),str(path),'exec'),module.__dict__)
    return module
K=load_source('public_kernel',ROOT/'kernel.py')
O=load_source('independent_root_oracle',ROOT/'review/root/check_global_candidate.py')
G=load_source('independent_gaussian_oracle',ROOT/'review/root/check_gaussian_interfaces.py')

def need(condition,message):
    if not condition:raise ValueError(message)

def one(x):
    y=K.hadamard_forward(x);z=K.hadamard_inverse(x)
    need(y==O.F(x) and z==O.inv(x),'Hadamard implementation agreement')
    need(K.hadamard_inverse(y)==x and K.hadamard_forward(z)==x,'two inverse compositions')
    need(sum(x)%2==sum(y)%2,'total parity')
    target=O.mul(O.H,x)
    need(sum((2*a-b)**2 for a,b in zip(y,target))==(4 if sum(x)%2 else 0),'unit/zero error')
    need(O.radial_half(O.n2(y),O.n2(x)),'half radial allowance')
    a=K.gaussian_forward(x);b=K.gaussian_inverse(x)
    need(a==G.Fc(x) and b==G.Fc_inv(x),'Gaussian implementation agreement')
    need(K.gaussian_inverse(a)==x and K.gaussian_forward(b)==x,'Gaussian exact inverse')

def main():
    origin=json.loads((ROOT/'KERNEL-ORIGIN.json').read_text());source=(ROOT/origin['source']).read_bytes()
    need(hashlib.sha256(source).hexdigest()==origin['source_sha256'],'reference source hash')
    prefix=source[:origin['copied_prefix_bytes']]
    need(hashlib.sha256(prefix).hexdigest()==origin['copied_prefix_sha256'],'copied prefix hash')
    need(prefix in (ROOT/'kernel.py').read_bytes(),'exact reference arithmetic prefix')
    count=0
    for x in product(range(-4,5),repeat=4):one(x);count+=1
    rng=random.Random(20261113);large=0
    for bits in [1,8,64,256,1024,4096]:
        for _ in range(10):
            x=tuple((1 if rng.randrange(2) else -1)*rng.getrandbits(bits) for _ in range(4))
            one(x);large+=1
    for k in [0,1,2,7,100,10**10,10**50,10**100]:
        xo=(0,0,4*k+2,1);yo=(2*k+2,2*k+1,-2*k-1,-2*k-1)
        xi=(2*k+1,2*k+1,2*k+2,2*k+1);yi=(4*k+2,0,-1,0)
        need(K.hadamard_forward(xo)==yo and K.hadamard_forward(xi)==yi,'sharp directional families')
    bad=[(),(1,2,3),(1,2,3,4,5),(True,0,0,0),(0.5,0,0,0),('1',0,0,0),None]
    rejected=0
    for value in bad:
        for fn in [K.hadamard_forward,K.hadamard_inverse,K.gaussian_forward,K.gaussian_inverse]:
            try:fn(value)
            except (TypeError,ValueError):rejected+=1
            else:raise ValueError('malformed public input accepted')
    # These controls separately prove that four source-native identities are not inherited.
    buffer=io.StringIO()
    with contextlib.redirect_stdout(buffer):G.main()
    interface_check=json.loads(buffer.getvalue())
    print(json.dumps({'status':'PASS_GLOBAL_HALF_KERNEL','cube_cases':count,'large_cases':large,'max_bits':4096,'seed':20261113,'invalid_inputs_rejected':rejected,'interface_check':interface_check,'sharp_sequence_parameters':8,'kernel_sha256':hashlib.sha256((ROOT/'kernel.py').read_bytes()).hexdigest(),'independence':'public arithmetic extracted from C reviewer; compared with separately written root arithmetic and Gaussian transfer; shared proposed formulas disclosed','scope':'finite cross-implementation checks; all-input theorem rests on the written proof'},indent=2))
if __name__=='__main__':main()
