"""Positive and failure controls: indep_check.py vs the author's check_order.py."""
import random, subprocess, sys, os
# Directory holding limits-1 bootstrap/xl (philippeVV fork @ ed21d624): check_order.py, graph16_59.txt, ord784.txt
XL = os.environ.get("LIMITS1_XL", os.path.join("l1", "research", "complex-budget-law", "limits-1", "bootstrap", "xl"))
G = os.path.join(XL, "graph16_59.txt")
O = os.path.join(XL, "ord784.txt")
os.makedirs("ctl", exist_ok=True)

def run(cmd):
    p = subprocess.run([sys.executable, "-I", "-B"] + cmd, capture_output=True, text=True)
    return p.returncode, (p.stdout + p.stderr).strip().splitlines()[-1] if (p.stdout + p.stderr).strip() else ""

def both(g, o, tag):
    a = run(["indep_check.py", g, o]); b = run([os.path.join(XL, "check_order.py"), g, o])
    print(f"{tag:34s} indep[{a[0]}] {a[1][:90]}\n{'':34s} author[{b[0]}] {b[1][:90]}")
    return a, b

order = open(O).read().split()
both(G, O, "positive ord784")
rnd = random.Random(20261016)
w = lambda name, xs: (open(name, "w").write(" ".join(xs)), name)[1]
both(G, w("ctl/dup.txt", order[:-1] + [order[0]]), "duplicate vertex")
both(G, w("ctl/short.txt", order[:-1]), "missing vertex")
sw = order[:]; sw[10], sw[400] = sw[400], sw[10]
both(G, w("ctl/swap.txt", sw), "two positions swapped")
both(G, w("ctl/rev.txt", order[::-1]), "reversed ord784")
for s in range(3):
    r = order[:]; rnd.shuffle(r); both(G, w(f"ctl/rand{s}.txt", r), f"random order {s}")
# corrupted graphs
L = open(G).read().split("\n")
nb = [list(map(int, x.split())) for x in L[1:547]]
u = 0; v = nb[0][0]
g1 = [x[:] for x in nb]; g1[u].remove(v); g1[v].remove(u)
open("ctl/g_drop.txt", "w").write("546 16\n" + "\n".join(" ".join(map(str, x)) for x in g1) + "\n")
both("ctl/g_drop.txt", O, "graph with one edge dropped")
# swap one edge endpoint so degrees stay 16 but a 4-cycle may appear
g2 = [x[:] for x in nb]
a, b = 0, nb[0][0]; c = 1; dd = [y for y in nb[1] if y not in nb[0]][0]
g2[a][g2[a].index(b)] = dd; g2[dd][g2[dd].index(c)] = a
g2[c][g2[c].index(dd)] = b; g2[b][g2[b].index(a)] = c
open("ctl/g_rewire.txt", "w").write("546 16\n" + "\n".join(" ".join(map(str, x)) for x in g2) + "\n")
both("ctl/g_rewire.txt", O, "degree-preserving rewire")
