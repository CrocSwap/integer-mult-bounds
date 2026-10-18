# Uniform separation of the selected nine COPY pullbacks

**Independent source-bound interface audit; no supplier or kappa change.**
The nine fixed rank-seven COPY address maps in Adam Gall's [PR2088](https://github.com/CrocSwap/integer-mult-bounds/pull/2088)
are pairwise distinct over **every field of characteristic other than two**.
Each of the 36 pairs has an explicit address-basis witness whose nonzero output
coordinate difference is a unit in `Z[1/2]`. The certificate supplies those
witnesses; rational inequality alone would not prove this specialization claim.

Consequently, for any nonempty subset of these maps, the simultaneous scalar
helper/snapshot rebasing contract from
[`bit-live-copy-operator-intertwiner`](../bit-live-copy-operator-intertwiner/README.md)
permits only `U=V=I`. This applies that credited theorem to concrete physical
pullbacks, answering its request to identify actual operator classes. It is
not a new abstract intertwiner theorem. PR2088 already reports distinct rational
matrices; independent reconstruction, uniform separation witnesses and this
specific rebasing implication are the delta here.

## Fixed object and independent reconstruction

The input is Sagar Thakrar's PR1062 payload in
`research/r439-bsection-stars-seed01/candidate.json.gz`, with retained centers
472 through 480. Replaying only frame assignments in D/A identifies their nine
COPY frames. For each frame, rational RREF produces a normal `q`; an independent
Gram-Schmidt row-span computation reproduces the projector

`P = I - q q^T/(q^T q)`.

The normal has one coordinate equal to one, and its squared norm is a dyadic
unit. The projector and the address map

`D_P = [[I-P,P],[P,I-P]]`

have dyadic entries. The checker verifies `P^2=P`, the two independent projector
computations, `D_P^2=I`, and exact equality with all nine recorded PR2088
matrices. All consumed predecessor bytes are retained unchanged with their
head, Git blob and SHA256 in `PREDECESSOR.json`; no predecessor executable is
imported. Selected live inputs and historical task provenance are in
`SOURCES.json`.

The COPY charge seven is the dimension of the projector's frame; it is **not**
the rank of `D_P`, which is an invertible 16-dimensional address transformation.
It is also not a rank assertion about the Boolean-function space below.

## Uniform proof and Boolean-function separation

Every identity with entries in `Z[1/2]` above specializes to any odd address
characteristic and to characteristic zero. Since a coordinate of `q` is one
and `q^T q` is a unit, `q q^T/(q^T q)` still has rank one; `P` has rank seven.
This certifies the displayed specialized operators. The physical interpretation
inherits PR2088's exact-stream and common-chart hypotheses.

For each pair `(i,j)`, the certificate gives a basis column `e_b`, coordinate
`a`, and difference

`(D_i e_b - D_j e_b)_a = +/- 2^k`.

Negative k is allowed. This difference is nonzero in every permitted field,
so the two address images differ there. Let `M` be the F2 vector space of all
Boolean functions on `K^16` and `C_i f = f composed with D_i`. The indicator of
the point `D_i e_b` then satisfies `(C_i f)(e_b)=1` and `(C_j f)(e_b)=0`.
Thus `C_i != C_j` as complete operators, including for finite address fields.
For the ambient 128-dimensional maps in PR2088, extend `e_b` by zero exterior
coordinates; the local difference remains. Each `C_i` is nonzero and invertible.

This proof does not infer equality or inequality from frame names or COPY ranks.
It treats Boolean coefficients and odd-characteristic **addresses** separately.

## Consequence for simultaneous scalar rebasing

For arbitrary independent dirty helper functions `h_i`, fix their original
snapshot maps `C_i`. Let `U,V` be invertible scalar matrices over F2 acting on
the helper functions and live copied functions respectively. Requiring the
updated snapshot to equal its own updated center's transported value at every
ERASE is equivalent to

`diag(C_i) U = V diag(C_i)`.

The `(i,j)` entry is `U_ij C_i = V_ij C_j`. Nonzero maps force the two scalar
bits to agree; a common value one then requires equal complete operators.
The 36 witnesses exclude this for every off-diagonal pair. The remaining
diagonal matrices are invertible only when all diagonal entries are one.
Hence `U=V=I`, for every subset of the nine roles and arbitrary word length.
This is the existing intertwiner proof specialized using independently checked
physical maps, not an exhaustive enumeration of GL9.

For each of the 36 pairs a separate literal Boolean-function experiment over
F3 checks every one of the 36 GL2(U,V) pairs on all 16 pairs of functions from
`{0,1,indicator(D_i e_b),indicator(D_j e_b)}`. Only identity survives. These
finite tests falsify weaker criteria; the dyadic proof supplies the uniform
statement. When the two maps are deliberately equal, all six synchronized
GL2 changes pass, showing why the distinction matters.

## Price and limits

The identity choice can use zero added rebasing gates and preserves nine rank-seven
COPY charges, sum 63. Granting all proposed rebasing gates and frame changes
zero cost still cannot make a nonidentity U/V satisfy this **unchanged-map**
contract. No actual saving, native implementation or completed physical budget
is asserted. Operator-valued transport, changing the snapshot maps or moving
the observation boundary changes the hypotheses and is outside this exclusion.

This does **not** reject PR1704/2088. Their centers stay fixed; temporarily mixed
snapshot outputs are restored before their own ERASE, so their net snapshot
map at that cut is already identity. The package does not independently replay
their full word, owners, workspace allocation, positive guards or compiler.
Native hosting, child scratch, all-size compilation, tape/precision, outer
assembly and any full multiplication theorem remain unrun/inherited obligations.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -I -B research/bit-selected-copy-separation/verify.py
python3.12 -I -O -B research/bit-selected-copy-separation/verify.py
python3.12 scripts/research_package.py --package research/bit-selected-copy-separation
```

Expected marker: `PASS_SELECTED_COPY_SEPARATION maps=9 pairs=36 characteristic=all_odd controls=4 no_new_kappa`.
The receipt is recomputed and compared in full. Equal-map, rational-only
separation (difference three collapses over F3), and changed-copy-map controls
exercise the hypotheses. All checks use exceptions and remain active under `-O`.
`--emit NEW_PATH` explicitly emits a receipt and refuses to overwrite a file.

## Assignment, overlap and credit

Base `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4;
selection nonce `104eb4f6871e27257261d0e2f901e1b0`. The assigned H2/K helper
contract scope is changed explicitly in `TASK.json`: its copyshare pricing
handoff was already completed by PR1805, and its two-copy implementation
handoffs by PR1943/2088. This work follows the actual-operator question in the
intertwiner package instead. The initial live overlap index covered 650 open
PRs and 1,179 Discussion records with complete pagination; `OVERLAP.json`
records the final refresh and limitations. No-match searches are not novelty
certificates. [Advance claim](https://github.com/CrocSwap/integer-mult-bounds/pull/2088#issuecomment-6190513563).

Credit Adam Gall/adamgall, PR2088 head
`95669bdd93cb3707f42268f5edee48af2a611bcc`, for the physical COPY maps and
interpretation; woklerx for the operator-intertwiner theorem; Ross Richardson,
PR1704, for the two-copy scatter contract; Adam Gall, PR1943, for the formal bank
boundary; alephnan, PR1627, for exact-stream hosting; and Sagar Thakrar's PR1062,
PR967/theon199, PR1015/Aaron Wang, PR923/Ross Richardson, PR589/DreamingOfClouds,
PR555/eumemic and retained geometry/hosting contributors for the input lineage.
Prepared for ywz65 with substantial OpenAI Codex assistance. Apache-2.0.
No independent human review or hosted CI pass is claimed.

## Open next questions

An operator-valued helper shear could satisfy `C_i A = B C_j` even when scalar
mixing cannot. Is one such transport physically admissible with a favorable
complete bill? First specify its frames, source/private locations and inverse
restoration, then price a two-role instance. The missing native transport and
child-scratch contracts are the blockers; the fixed scalar result supplies no
evidence of a gain for that changed alphabet. Structured question: `TASK.json`.
