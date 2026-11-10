# Seven distinct source axes cannot supply the seven-source connector

This scoped obstruction was produced by Nick Petalas. Apache-2.0.
The finite exclusion below is new. The normalized-axis and mandatory-mask
methods are credited to conorholds, Mason Hale and Arham Tahir.

## 1. Contract and conclusion

There are seven immutable source rows x_j, four arbitrary dirty root rows z_p,
and separate output rows y_m for every nonzero seven-bit mask m. Source calls
add B_j x_j to one physical root. Output calls add A_m z_p to their own target.
Every B_j and A_m occurs exactly twice. The compatible binary linear maps are
arbitrary, including singular and noncommuting maps. Outputs are not observed
or used as scratch. All roots and sources restore. Child scratch is private
and restores under its inherited contract.

Allow any finite number of invertible scalar binary root-frame changes, any
physical port on each call, and no bound on the cost of those changes. Granting
these operations only enlarges a paid-XOR interface.

**Theorem.** A universal connector under this contract cannot have seven
pairwise distinct normalized source axes. If it supplies the all-ones output
and its normalized axes are distinct, at least 22 other requested masks fail
the mandatory-mask necessary condition. The number 22 is the exact minimum
of that deficit in the complete reduced domain. It is not an exact maximum
for the total set of outputs a legal circuit can supply.

Consequently a universal seven-source connector with four dirty roots must
repeat an axis. This is a restriction within the known optimal root count,
not a new root-count theorem or a transfer-count minimum.

## 2. Necessary mask equation

Let R_t be the invertible matrix carrying the four independent initial dirt
rows into the current roots. In normalized coordinates a source call at port p
injects the nonzero column R_t^{-1} e_p. Its two calls must have the same
normalized column v_j, since no other call can remove that source coefficient
from the restored roots. Final dirt restoration also forces R_final=I.

Let q_t be the seven-bit parity of source calls before a cut. A physical root
whose dirty covector is r then contains

    r z_initial + sum_j (r v_j) q_t[j] B_j x_j.

Two calls of an arbitrary A_m cancel initial dirt only when their dirty
covectors agree. Their source mask is therefore

    m = h AND d,    h = r V,    d = q_s XOR q_t,    V=[v_0 ... v_6].

Write H=rowspace(V) and D(w)={q_s XOR q_t} for the paired source word w.
Thus every supplied mask belongs to {h AND d: h in H, d in D(w)}.
This implication is the normalized-axis method of PR2182 and the code
formulation of PR2795. The calculation above states the exact premise used
here; neither predecessor's census or attaining construction is reverified.

The implication is necessary already for identity source/output maps on
independent scalar inputs. Hence it applies at every positive row length,
without inferring arbitrary-size behavior from a finite dense fixture.

## 3. Complete domain for distinct axes

The all-ones mask requires both h=127 and d=127. Some nonzero covector r_*
therefore has r_* v_j=1 for every j. The axes lie in an eight-point affine
hyperplane of F2^4. Under the distinctness hypothesis they occupy seven of
its points and span F2^4.

A change of root basis takes this hyperplane to the points (1,u), u in F2^3.
The affine transformations u -> Au+b act transitively on its omitted point
and are induced by invertible linear maps on (1,u). We may choose the omitted
point to be u=7. Coordinate assignments to the seven sources remain arbitrary.
Therefore every possible H is a coordinate permutation of

    H_0 = { ((r dot (1,j)))_(j=0,...,6) : r in F2^4 }.

Here (1,j) is encoded by 1|(j<<1). The primary generator visits all 7!
coordinate permutations, takes their exact row spaces, and deduplicates them.
There are exactly 30 distinct codes, each with sixteen words. No source-order
symmetry is assumed after this code inventory is formed.

For every proper codeword h != 127 define its supported subsets. A nonzero
mask m is mandatory when no such h contains its support. If m=h AND d is
mandatory, h must be 127, so d=m. Thus

    M(H) subset D(w)

is necessary for universality. Each of the thirty codes has exactly 57
mandatory masks, as directly enumerated in both checkers.

## 4. Complete source-order reduction

The equality d=127 means an interval of the paired source word contains each
source an odd number of times. Since there are only two calls per source,
that interval contains each source exactly once and has length seven.
Rotate the closed source word to start at that interval and rename sources
in its order. The resulting word is

    0,1,2,3,4,5,6, permutation(0,1,2,3,4,5,6).

Rotation translates all prefix parities by the same vector and preserves D.
Renaming coordinates permutes H as well as D. Enumerating all 5,040 second
orders and all thirty codes is therefore complete for this necessary test.
This is the all-ones interval reduction of PR2795. It does not assert that
physical frame changes can be rotated without paying for them.

## 5. New finite certificate

For every reduced pair the checker computes the full bitset M(H) minus D(w).
The two engines agree on every one of the 151,200 bitsets. Their minimum
cardinality is 22, attained by four reduced pairs. There are no zero-deficit
pairs. The generated report contains the complete deficit histogram and a
SHA256 digest of all bitsets in lexicographic (source order, code) order.

One attaining deficit witness has second order

    1,4,0,3,6,2,5

and code

    0,11,22,29,37,46,51,56,71,76,81,90,98,105,116,127.

Its missing mandatory masks are

    23,45,53,54,55,57,58,61,75,78,79,85,86,87,92,94,102,
    113,117,118,119,121.

The primary engine uses coordinate permutations of the affine-cube code,
pairwise prefix XORs and support containment. The second enumerates all
11,811 three-dimensional binary RREF row spaces, retains the thirty whose
nonzero vectors all have weight four, and takes orthogonal complements.
It forms D by contiguous interval parities and M by enumerating proper
codeword subsets. The full code inventories and every deficit agree.
No predecessor executable, stored numerical receipt or search solver is an
acceptance input.

## 6. Consequence and limits

The 22 absent mandatory masks cannot be recovered by more scalar frame
changes, different physical read ports or a more expensive frame itinerary.
Thus the complete 127-mask endpoint is impossible with distinct axes. If the
all-ones mask is supplied, at most 105 nonzero masks can pass this necessary
test. Attainment of that total-output bound is unclaimed.

Repeated axes escape the premise. As a positive control, the credited star's
axes (1,1,1,1,2,4,8) and source word

    0,1,0,1,4,5,6,2,3,2,3,4,5,6

pass the full mask-intersection criterion. This is a tiny control on the
scope, not a new verification claim for its physical construction or invoice.
The predecessor's four-root, 56-X star and root-minimum proof remain credited
premises. No smaller paid word was established here.

Extra source/output calls, source mutation, output feedback, clean roots,
matrix-valued root transformations and nonlinear updates change the contract.
Physical hosting, native realization, tape/precision/stock costs and supplier
admission are not supplied. All five selected framework assumptions remain.
The finite certificate supports this scoped written proof; independent human
and formal proof-kernel review are unclaimed.
