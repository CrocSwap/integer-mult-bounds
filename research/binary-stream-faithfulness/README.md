# Sharp width boundary for formal binary-stream address tests

For the diagonal action of `GL_d(F2)` on **w point columns**, formal
group-algebra equality is equivalent to equality on full arbitrary binary
streams exactly when **w>=d**, for d>=2. For the corresponding `AGL_d(F2)`
action the boundary is **w>=d+1**. Dimension one is exceptional: GL_1 is
faithful even at w=0, while AGL_1 is faithful from w=1.

Here an address is a d by w binary matrix: d coordinate words with w bits
each. A linear label acts bitwise on all columns; an affine label uses the
**same** translation on every column. Its coordinate translation flips an
all-ones w-bit mask. This is a specified stream action, not integer arithmetic
with carry or a native selected layout.

[PROOF.md](PROOF.md) proves both directions for every d and w. A regular
orbit recovers every formal coefficient, including every entry of a complete
dirty-register endpoint. Below the boundary, the nonzero sum of all group
elements annihilates every payload, because every address stabilizer is even.
The proof spells out the small-dimensional exceptions.

The failure is attainable by a legal word. A retained GL_2 example uses two
dirty roles, **18 paid coordinate CNOTs and 10 free scalar XORs**, with no
extra role or erasure. Its complete formal map is `I+n_G E_01`, but it is
identity on all eight input columns at w=1. At w=2 six of 32 input columns
expose its nonzero coupling. All 40 columns agree with the exact formal
action; deleting any of the 18 paid calls fails its formal endpoint.
This does not establish a cheaper monomial target below the threshold.

The practical corollary is source-bound: the credited PR1974 exact minima
for all **28,224 two-register GL_3 target pairs** transfer to this full
binary bit-plane stream action at every w>=3, with the same alphabet,
free scalar mixing and full endpoint. Its third-register result transfers
only within its existing length-seven coverage. No predecessor census is
rerun or independently certified here. PR1333's earlier homogeneous-image
norm alias and arbitrary-register rank floor are credited, not repeated.

The standard-library verifier enumerates all point-tuple orbits for linear
and affine dimensions 1..3 through their thresholds (19 cases), compares
stabilizers with the exact formula, recovers coefficients on a regular orbit,
and checks the legal word formally and on full dirty input bases. Separate
controls enforce the common affine translation and expose clean-only testing.
The bounded checks corroborate the written proof. [RESULT.json](RESULT.json)
records all orbits and the literal chronological word; its D indices 0 and 1
are coordinate CNOTs `x_0 ^= x_1` and `x_1 ^= x_0` on role 0, and X adds role
1 to role 0. Every inverse address call is included in the 18-call bill.

## Reproduce

From the repository root:

```sh
python3.12 -I -O -B research/binary-stream-faithfulness/verify.py
python3.12 scripts/research_package.py --package research/binary-stream-faithfulness
```

Replay authenticates both predecessor README inputs by SHA256 and Git blob
before computation, works in a Git-free source export, and is read-only.
Four subprocess groups exercise unchanged exports, missing/drifted inputs,
typed receipt corruption and exclusive receipt regeneration. Explicit failures
remain active under `-O`; no external dependency is required.

Formal algebra faithfulness supplies no physical storage, scalar-work price,
address conversion or tape compiler. Arithmetic modulo q^w, rational frame
actions, restricted payload subspaces and independent affine offsets per
column have different contracts. No new supplier, selected frontier or
multiplication exponent follows.

## Open next questions

Can a monomial target actually become cheaper below the faithful width?
Start with one two-register GL_2 target and compare exact full-stream versus
formal searches at w=1; the norm word proves an alias, not such a saving.

Can one physical caller realize the faithful bit-plane action with a complete
invoice? Pin its legal ADD/translation and scalar mixing primitives, then
charge conversion, all roles and restoration. The declared algebraic action
does not provide that implementation. Structured questions are in
[TASK.json](TASK.json).

## Credit

PR1974 (`a4992da8e4e81a74cf1fd2b2d3af948662476d6e`) is by Josie Elliston,
building on Hanson Sun's seed18 census. PR1333
(`7f25b6d0e1d7e995d4d2840f231d98b1a1a9fec2`) is by Gareth Davidson.
Standard regular-orbit and orbit-stabilizer arguments are reused openly.
Exact retained inputs and main provenance are in [SOURCES.json](SOURCES.json).
Prepared for ywz65 with substantial OpenAI Codex assistance. Apache-2.0.
No independent human or formal-kernel verification is claimed.
