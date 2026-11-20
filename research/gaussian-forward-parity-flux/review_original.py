"""Independent check in original integer coordinates; no verifier imports."""
import itertools
import json

H = ((1,1,1,1),(1,-1,1,-1),(1,1,-1,-1),(1,-1,-1,1))
S = (1,-1,-1,1)


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def dot(a, b):
    return sum(x*y for x,y in zip(a,b))


def norm2(a):
    return dot(a,a)


def transform2(y):
    jy = (*y[:3], -y[3])
    return tuple(dot(row,jy) for row in H)


def radial(x, y, num, den):
    a, b = norm2(y), norm2(x)
    if a <= b:
        return True
    left = (a-b)*den*den-num*num
    return left <= 0 or left*left <= 4*num*num*den*den*b


def run():
    require(all(dot(H[i],H[j]) == 4*(i==j) for i in range(4) for j in range(4)), "orthogonality")
    receipts, charges, escape_counterexample = [], 0, False
    for n in (3,5):
        cube = list(itertools.product(range(-n,n+1,2),repeat=4))
        aa = [t for t in cube if sum(t)%4 == 2]
        bb = {t for t in cube if sum(t)%4 == 0}
        corners = {t for t in bb if all(abs(v)==n for v in t)}
        require(len(aa)==len(bb) and len(corners)==8, "cube balance")
        reached, excluded_escapes = set(), 0
        for t in aa:
            numer = tuple(2*t[i]-S[i]*dot(S,t) for i in range(4))
            require(all(v%4==0 for v in numer), "inverse coordinate integrality")
            x = tuple(v//4 for v in numer)
            require(sum(x)%2==1 and 4*norm2(x)==norm2(t), "original odd input")
            hx = tuple(dot(row,x) for row in H)
            for bits in itertools.product((0,1),repeat=4):
                y = tuple(hx[j]//2+bits[j] for j in range(4))
                require(sum((2*y[j]-hx[j])**2 for j in range(4))==4, "error-one choices")
                z = transform2(y)
                if sum(y)%2:
                    require(sorted(abs(z[j]-t[j]) for j in range(4))==[0,0,0,2], "unit edge")
                    if z not in bb:
                        require(not radial(x,y,1,2), "outward escape below half")
                        excluded_escapes += 1
                    if radial(x,y,3,10):
                        require(z in bb and z not in corners, "forbidden corner or escape")
                        reached.add(z)
                else:
                    e2 = tuple(dot(row,y) for row in H)
                    require(all(v%2==0 for v in e2), "charged input integrality")
                    e = tuple(v//2 for v in e2)
                    require(sum(e)%2==0 and e!=x, "distinct even charge")
                    for axis in range(4):
                        for sign in (-1,1):
                            out = list(y)
                            out[axis] += sign
                            v = transform2(tuple(out))
                            require(max(abs(v[j]-t[j]) for j in range(4))<=2, "two-edge bound")
                            require(max(map(abs,v))<=n+2, "expanded cube")
                            escape_counterexample |= max(map(abs,v))>n
                            charges += 1
        require(reached == bb-corners, "complete finite neighbor union")
        receipts.append({"N":n,"odd_inputs":len(aa),"available_neighbors":len(reached),"excluded_escapes":excluded_escapes})
    require(escape_counterexample, "same-cube negative control was vacuous")
    require(not radial((1,0,0,0),(2,0,0,0),1,2), "radial rejection control")
    return {"status":"PASS_INDEPENDENT_ORIGINAL_COORDINATES","cubes":receipts,
            "two_edge_choices":charges,"same_cube_claim_rejected":True}


if __name__ == "__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
