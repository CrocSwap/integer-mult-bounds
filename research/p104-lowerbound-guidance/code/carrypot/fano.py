"""[C] Fano non-liftability over Z/4: no lifts x_c in (Z/4)^3 (x_c = c mod 2) of the 7 points of PG(2,2) with
x_{a+b} in span_{Z/4}(x_a, x_b) for all 7 lines.  (lifts of e1,e2,e3 fixed to the standard basis by GL3(Z/4).)
Control: the same test over a 2-dim space (3 points, 1 line) and over PG(2,2) minus one line both succeed."""
import itertools
def inspan(x, a, b):
    return any(all((i*p + j*q - r) % 4 == 0 for p, q, r in zip(a, b, x)) for i in range(4) for j in range(4))
pts = [1,2,3,4,5,6,7]
vec = lambda c: tuple((c >> i) & 1 for i in range(3))
lines = [(a, b, a ^ b) for a in pts for b in pts if a < b and a < (a ^ b) and b < (a ^ b)]
lines = sorted(set(tuple(sorted(l)) for l in lines))
assert len(lines) == 7
def lifts(c): return [tuple(v + 2*e for v, e in zip(vec(c), ee)) for ee in itertools.product((0,1), repeat=3)]
base = {1: (1,0,0), 2: (0,1,0), 4: (0,0,1)}
def count(linesets):
    sols = 0
    for xs in itertools.product(*[lifts(c) for c in (3,5,6,7)]):
        x = dict(base); x.update(zip((3,5,6,7), xs))
        if all(inspan(x[c], x[a], x[b]) for (a, b, c) in linesets): sols += 1
    return sols
print('full Fano (7 lines): liftings =', count(lines))
for drop in range(7):
    print('  Fano minus line', lines[drop], ': liftings =', count([l for i, l in enumerate(lines) if i != drop]))
