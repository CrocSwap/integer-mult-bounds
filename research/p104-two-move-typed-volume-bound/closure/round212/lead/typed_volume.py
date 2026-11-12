from fractions import Fraction as F
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import alarm

root = Path(__file__).resolve().parent / 'inputs'
pins = {'WORD.json.gz':'4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a','clifford_exact.py':'2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962','native_verify.py':'3049471905b47b385c88378a1a3be7a18b8858aadd035b8a6da2f4a03b470f38','pricing.py':'f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182'}
alarm(30)
for name,digest in pins.items():
    assert sha256((root/name).read_bytes()).hexdigest() == digest
w = loads(decompress((root/'WORD.json.gz').read_bytes()))
assert w['program'][32944:32946] == [['MOVE',625,3,117,False],['MOVE',624,3,117,False]]
a,b = (tuple(w['frames'][i]) for i in (3,117))
assert a == () and b == (8,17,34,68,391)
C,V = (run_path(str(root/name)) for name in ('clifford_exact.py','native_verify.py'))
recipe,_ = C['lower_child'](C['canonical_frame'](9,a).adjoint().then(C['canonical_frame'](9,b)))
assert recipe['rank'] == 5
T = V['frame'](b,9)
assert T == V['adjoint'](T[-2:]) + V['fourier'](5) + T[-2:]
V['equal'](T,V['recipe'](recipe),'exact chart and phase')
V['equal'](T*4,(),'exact order divides four')
witness = next([i,list(x),list(y)] for i,(x,y) in enumerate(zip(V['tableau'](()),V['tableau'](T*2),strict=True)) if x!=y)
h = run_path(str(root/'pricing.py'))['power_bounds']
lo,hi = map(F,('0.00364665195644044790699554028334161','0.00364665195644044790699554028334162'))
quote = [17*(2*h(5,hi)[0]-h(6,lo)[1]),17*(2*h(5,lo)[1]-h(6,hi)[0])]
assert 0 < quote[0] < quote[1]
alarm(0)
print(dumps({'pins':pins,'rank':5,'clocks':[32944,32945],'projective_order':4,'squared_pauli':witness,'quote':list(map(str,quote))},sort_keys=True,indent=2))
