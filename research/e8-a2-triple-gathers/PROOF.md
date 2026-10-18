# Finite proof and A2 triangle obstruction

**Definitions.** Work with twice the standard E8 roots, so coordinates are either `(±2,±2,0,0,0,0,0,0)` in any two distinct positions, or `(±1,±1,±1,±1,±1,±1,±1,±1)` with even parity of negative entries. Every vector has squared norm 8. These are 112 + 128 = 240 distinct roots; dividing by `r ~ −r` gives 120 lines. For distinct lines `x,y`, adjacency means `|x·y|=4`. It corresponds to `|x·y|=1` for standard norm-two roots. Call the open neighbors `N(x)` and the closed gather `G(x)=N(x)∪{x}`.

**Lemma 1 (pair intersections, exactly checked).** For every line, `|N(x)|=56`, and for two different lines:

- adjacent: `|N(x)∩N(y)| = 28`, `|G(x)∩G(y)|=30`;
- nonadjacent: `|N(x)∩N(y)| = 24`, `|G(x)∩G(y)|=24`.

These follow by finite enumeration of 120 canonical coordinate representatives in the checker (7,140 unordered pairs). They are also the strongly regular graph identity `A²=32I+4A+24J`, with parameters `(v,k,λ,μ)=(120,56,28,24)`.

**Lemma 2 (each edge closes exactly one A2 triple).** Choose representatives `a,b` for adjacent root lines. Then `a·b = ±4`. If their scalar product is +4, `a−b` has squared norm 8; otherwise `a+b` does. Either vector is an E8 root, and the third line is distinct from both endpoints. It belongs to their real 2-plane and closes an adjacency triangle. Conversely, any triangle lying in that plane has as its third line precisely the one just identified, since the only lines in the A2 span at norm 8 are `±a`, `±b`, `±(a∓b)`. Thus each edge belongs to exactly one A2 triangle. There are `(120×56)/2 = 3,360` edges and hence **3,360/3 = 1,120 A2 triangles**.

**Lemma 3 (an A2 triple has no open common neighbor).** Orient the three representatives so `c=a−b` (or `c=a+b`). If a fourth root line `x` were adjacent to all three, its integer scaled dot products with `a,b,c` would all have absolute value 4. But `x·c = x·a−x·b` (or their sum) must be one of `−8,0,8`, never `±4`: contradiction. The three A2 vertices lie in each other's closed gathers, so `|G(a)∩G(b)∩G(c)|=3`. Each pair is adjacent and has closed intersection size 30 by Lemma 1. Therefore inclusion/exclusion gives

```
|G(a) ∪ G(b) ∪ G(c)| = 3×57 − 3×30 + 3 = 84.
```

**Lemma 4 (complete fixed-graph census).** Iterate over the `C(120,3)=280,840` line triples. Compute the number of internal adjacency edges, the number of open and closed common neighbors, the rank of the doubled-coordinate Gram matrix (its determinant is `512 + 2abc − 8(a²+b²+c²)`, with `a,b,c` the three pairwise dot products), and the union. The exact integer case breakdown is stored in `RESULT.json` and rederived by `verify.py`. All triples not of A2 type have a union size of at least 100. The checker verifies the closed union in a second way for **every** triple, by inclusion/exclusion. Hence **84 is the global minimum**, attained exactly by the **1,120 A2 triangles**.

As an independent combinatorial check of the aggregate **number** of triples in each edge class:

1. Three-edge triangles: `3,360×28/3 = 31,360`, including 1,120 A2 and 30,240 other triangles.
2. Two-edge wedges: at each center, `C(56,2) − (56×28)/2 = 756` pairs of nonadjacent neighbors, for `120×756=90,720` wedges.
3. One-edge triples: an edge has `120−|G(a)∪G(b)| = 120−(114−30)=36` vertices nonadjacent to both endpoints, for `3,360×36=120,960` triples.
4. Zero-edge triples: `C(120,3)−31,360−90,720−120,960 = 37,800`.

These aggregate calculations do not assume the detailed three-way intersection counts, which are independently enumerated. Together with Lemmas 1–3, the exact finite census proves the stated result.

**Limits.** The combinatorial 84-source floor is a lower bound for a *set-based* 3-port gather of all closed 57-entry E8 neighborhoods with each distinct line counted once. It does not bound the true number of physical copies, frame transitions, helper registers, recursive children, or circuit gates. It is neither a new supplier nor a proof of an improved κ. It is specifically **not** a finding about #703's quaternionic ten-line fitting decoder, nor an improvement to #626's selected complex K-triangle implementation.
