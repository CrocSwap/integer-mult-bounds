"""Emit the frozen literal input recipe without modifying PENCILS.json.
ToikY with OpenAI Codex assistance. Inherited Petalas6451/6543 attainers.
Apache-2.0. Expected degrees remain calibrations checked by both engines.
"""
import json

MUL = ((0,0,0,0),(0,1,2,3),(0,2,3,1),(0,3,1,2))

def copy(a):
    return [r[:] for r in a]

def companion_attainer(degree, power=1):
    # t^degree+t, or its square; minus equals plus in characteristic two.
    d = degree*power
    coefficients = [0]*(d+1)
    coefficients[power] = 1
    coefficients[d] = 1
    a = [[int(i == j and i < d) for j in range(d+1)] for i in range(d+1)]
    b = [[0]*(d+1) for _ in range(d+1)]
    for i in range(d-1):
        b[i+1][i] = 1
    for i in range(d):
        b[i][d-1] = coefficients[i]
    b[d][d] = 1
    return a,b

def strict_transform(a,b):
    out = [copy(a),copy(b)]
    for m in out:
        n = len(m)
        # Four invertible elementary operations, in this literal order.
        m[0] = [x ^ MUL[2][y] for x,y in zip(m[0],m[1])]
        m[-1] = [x ^ MUL[3][y] for x,y in zip(m[-1],m[0])]
        for row in m:
            row[0] ^= MUL[3][row[-1]]
            row[1] ^= MUL[2][row[0]]
    return out

fixtures = []
def add(name,a,b,e,description):
    fixtures.append(dict(name=name,A=a,B=b,expected_degree=e,description=description))

add('empty',[],[],1,'Empty determinant is1; infinity succeeds.')
add('singular-one',[[0]],[[0]],None,'Identically singular pencil.')
add('nonprime-infinity',[[2]],[[0]],1,'Literal nonprime encoded scalar z; inverse is z+1.')
add('constant-determinant',[[0,2],[0,0]],[[1,3],[0,1]],1,'Affine determinant is constant1; infinity fails.')
add('polynomial-row-pivot',[[0,0],[0,0]],[[0,2],[3,0]],1,'Nonzero polynomial pivot needs a row swap.')
for d,e in ((4,2),(16,3)):
    a,b = companion_attainer(d)
    add('first-degree-'+str(e),a,b,e,'Inherited t^'+str(d)+'+t companion plus infinity block; expected degree is a prospective check.')
    c,k = strict_transform(a,b)
    add('first-degree-'+str(e)+'-nonprime-transform',c,k,e,'Same pencil after row0+=z row1; rowLast+=(z+1)row0; col0+=(z+1)colLast; col1+=z col0.')
a,b=companion_attainer(4,2)
add('repeated-degree-two',a,b,2,'Inherited (t^4+t)^2 companion plus infinity; repeated affine roots.')

obj = dict(schema_version=1,base_field=dict(characteristic=2,modulus=[1,1,1],cardinality=4,encoding='base2 low-first,2=z,3=z+1'),fixtures=fixtures,expectations_status='Frozen prospective assertions, not executed evidence.',limits='No new threshold or attainment theorem; old source theorem credited. Both engines independently check actual raw matrices.')
raw=(json.dumps(obj,sort_keys=True,indent=2)+'\n').encode()
print(raw.decode(),end='')
