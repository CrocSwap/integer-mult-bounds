"""Test trace phases and quadratic Bell-label transport on literal five-qubit gates.
The sparse columns have Gaussian integer entries with a shared power-of-two denominator.
apoursh with substantial OpenAI Codex assistance. Apache-2.0.
"""
from itertools import product

N = 5
D = 1 << N
MASK = D - 1


def require(condition, message):
    if not condition:
        raise ValueError(message)


def mul(v, w):
    a,b = v
    c,d = w
    return a*c-b*d, a*d+b*c


def power(v, n):
    out = (1,0)
    for _ in range(n):
        out = mul(out,v)
    return out


def accumulate(values, key, delta):
    a,b = values.get(key,(0,0))
    values[key] = a+delta[0], b+delta[1]


def sign(mask):
    return 1 - 2*(mask.bit_count() & 1)


def gate_matrix(program):
    columns = [{j:(1,0)} for j in range(D)]
    denominator = 1
    for gate, a, b in program:
        active = 1 << a
        if gate == "H":
            # Multiply the usual Hadamard lift by its eighth-root phase,
            # obtaining (1+i)[[1,1],[1,-1]]/2 in the Gaussian-dyadic ring.
            denominator *= 2
        for j,col in enumerate(columns):
            new = {}
            for y, (v,w) in col.items():
                if gate == "H":
                    lo, hi = y & ~active, y | active
                    accumulate(new,lo,(v-w,v+w))
                    factor = sign(y & active)
                    accumulate(new,hi,(factor*(v-w),factor*(v+w)))
                elif gate == "S":
                    new[y] = (-w,v) if y & active else (v,w)
                elif gate == "X":
                    new[y ^ active] = (v,w)
                elif gate == "Z":
                    factor = sign(y & active)
                    new[y] = v*factor,w*factor
                elif gate == "CNOT":
                    new[y ^ ((1 << b) if y & active else 0)] = (v,w)
                else:
                    raise ValueError(gate)
            columns[j] = {r:c for r,c in new.items() if c != (0,0)}
    return columns, denominator


def symplectic(program, label):
    x, z = label & MASK, label >> N
    for gate,a,b in program:
        bit = 1 << a
        if gate == "H" and bool(x & bit) != bool(z & bit):
            x ^= bit
            z ^= bit
        if gate == "S" and x & bit:
            z ^= bit
        if gate == "CNOT":
            x ^= ((x >> a) & 1) << b
            z ^= ((z >> b) & 1) << a
    return (z << N) | x


def translate_trace(columns, x, z):
    real = imag = 0
    for j,col in enumerate(columns):
        y = x ^ j
        a,b = col.get(y,(0,0))
        factor = sign(z & y)
        real += a*factor
        imag += b*factor
    return real,imag


def refinement(u, p):
    ux, uz = u & MASK, u >> N
    px, pz = p & MASK, p >> N
    return ((px & pz) ^ (ux & pz) ^ (uz & px)).bit_count() & 1


def bell_target(program, u):
    basis = [1 << i for i in range(2*N)]
    guesses = [v for v in range(D*D)
               if all(refinement(v,symplectic(program,e)) == refinement(u,e)
                      for e in basis)]
    require(len(guesses) == 1, "Bell-label transport must be unique")
    return guesses[0]


def check_bell(program, columns, den, u):
    x,z = u & MASK, u >> N
    output = {}
    for j,col in enumerate(columns):
        factor = sign(z & j)
        for r,v in columns[j ^ x].items():
            for c,w in col.items():
                a,b = mul(v,w)
                accumulate(output,(r,c),(a*factor,b*factor))
    output = {p:v for p,v in output.items() if v != (0,0)}
    target = bell_target(program,u)
    xnext,znext = target & MASK, target >> N
    phase = output.get((xnext,0),(0,0))
    require(sum(v*v for v in phase) == den**4, "Bell amplitude")
    expected = {(xnext ^ c,c): (phase[0]*sign(znext & c),phase[1]*sign(znext & c))
                for c in range(D)}
    require(output == expected,"literal congruence and quadratic refinement disagree")
    require(refinement(0,u) == refinement(0,target),"changed Arf orbit")


def main():
    h,s,cx = "H","S","CNOT"
    programs = [
        (), ((s,0,0),), ((h,2,0),), ((cx,0,4),),
        ((h,0,0),(s,0,0),(cx,0,1),(h,1,0),("Z",3,0)),
        ((h,1,0),(cx,1,4),(s,2,0),(h,4,0),("X",0,0),(cx,2,0)),
    ]
    translated = bell_cases = detected = 0
    seen = set()
    for program in programs:
        cols, den = gate_matrix(program)
        count = sum(symplectic(program,u) == u for u in range(D*D))
        d = count.bit_length()-1
        require(2**d == count,"fixed-space count")
        seen.add(d)
        nonzero = 0
        for x,z in product(range(D),repeat=2):
            a,b = translate_trace(cols,x,z)
            translated += 1
            if (a,b) == (0,0):
                continue
            nonzero += 1
            require(a*a+b*b == den**2 * count,"Pauli trace norm")
            require(power((a,b),12) == (((-64)**d)*den**12,0),"width-13 trace phase")
            require(power((a,b),16) == ((128**d)*count*den**16,0),"width-15 trace phase")
            detected += int(d % 2 == 1)
        require(nonzero * count == D*D,"trace support")
        for u in [0, 1, 32, 33, 22, 61, 210, 411, 700, 1023]:
            check_bell(program,cols,den,u)
            bell_cases += 1
    require(detected and len(seen)>=3,"controls exercise changing trace sign and rank")
    print(f"PASS literal five-qubit gates={len(programs)} Pauli-translates={translated} "
          f"Bell-congruences={bell_cases} fixed-dimensions={sorted(seen)}")


if __name__ == "__main__":
    main()
