# One-sided P112 fitting rigidity

We state a one-sided corollary of Adam Gall's
[PR1098 support-spectrum certificate](../p112-gram-support-seed80/README.md)
and verify it by a separate deletion-rank calculation. Fixing only the column
spaces of the rational decoder and binary pairing already forces both original
matrices. Neither row space needs a restriction.

The support geometry and spectra belong to Mihir Srivastava's PR845 and Adam
Gall's PR1098. We do not claim new underlying geometry. The contribution here
is the joint-fitting corollary, its explicit coloop classification and the
direct exact checker. It supplies no new supplier or exponent.

## Statement

Let P contain `root_lines[8:]` from the pinned
[prototype](../direct-delivery504-global/inputs/hamming/PROTOTYPE.json), and put
R=P/2. Each raw root has squared norm four, so R has unit row norms. Let U be
the corresponding 112-by-9 binary matrix from `binary_ports[8:]`.

For arbitrary W in Q^(8-by-112) and L in F2^(9-by-112), put

```
N = R W,        B = U L.
```

Suppose both matrices have unit diagonal, and N_ij=0 whenever i!=j and
B_ij=1. Then

```
N = R R^T,        B = U U^T.
```

In particular, rank_Q(N)=8 and rank_F2(B)=9. Transposing the statement gives
the analogous result when only the two row spaces are fixed.

For a proposed decoder that retains both rational root-code spaces, a binary
pairing below rank nine must therefore change both its column and row codes.
This statement does not exclude such outside-code constructions, different
port sets, block-valued replacements, or other native interfaces. It gives no
new lower bound on the complete paid supplier cost at window nine.

## Column reduction

For a nonzero character a in F2^9, define

```
S_a = {i : u_i dot a = 1}.
```

In column j of B, the coefficient vector a=L[:,j] must satisfy j in S_a.
The fitting equations require the corresponding rational column w=W[:,j]
to obey R_i w=0 for i in S_a except j, and R_j w=1. Thus deleting row j
must lower the rational rank of R[S_a,:]. Such a row is a *coloop* of that
row configuration.

The complete classification is

```
{(a,j) : j is a coloop of P[S_a,:]} = {(u_j,j) : 0 <= j < 112}.
```

Consequently a=u_j in column j, which forces B=U U^T. For this character,
the other selected roots span the seven-dimensional orthogonal complement
of r_j. Their annihilator is the line through R_j^T. Unit diagonal fixes
w=R_j^T, so N=R R^T. This proves the statement without a symmetry assumption.

## Derivation from the predecessor spectra

PR1098 considers H_a=P[S_a,:]^T P[S_a,:]. Its complete spectrum certificate
has three relevant classes:

- Eight singular supports have eigenvalues zero and seven copies of 32.
- 112 supports have a simple eigenvalue four; their other eigenvalues exceed four.
- The remaining 391 supports have minimum eigenvalue strictly greater than four.

Each selected row r has squared norm four. Deleting it replaces H by
H-rr^T. On a full-rank support with minimum eigenvalue greater than four,
this cannot lower rank. On a singular support, r lies in the range of H;
the positive eigenvalues remain at least 32-4, so its rank also stays unchanged.

For H>=4I, a rank drop requires equality in both

```
z^T H z >= 4 ||z||^2,
(r^T z)^2 <= 4 ||z||^2.
```

Hence r spans the four-eigenspace. That space is simple in each of the
112 exceptional supports. For every original character a=u_j, the retained
Gram identity says that S_a consists of j and roots orthogonal to r_j.
Therefore H_a r_j=4r_j. These 112 distinct characters exhaust the exceptional
supports, and distinct projective root lines give the unique coloop j.

This is an application of PR1098's published spectra. PR845 supplies the
original support lemma. Philipp's [PR1191 fixed-mask result](../complex-masked-rigidity-seed28/PROOF.md)
already proves the related one-sided rational rigidity after fixing the mask;
the coloop argument here first forces the binary mask itself.

## Independent deletion-rank evidence

The prototype's 112 raw rows equal the X rows in PR845's
[reference geometry](../p112-single-lift/reference-geometry.json) after a
literal row permutation. The verifier checks this bridge. PR1098 binds its
generated X to that same reference; no sign or coordinate change is needed.

Our checker enumerates all 511 nonzero binary characters. It computes each
rational row rank by integer elimination with gcd normalization, then tests
deletion of each row in one chosen original-row basis. A row outside that
basis cannot be a coloop because the basis remains after its deletion.
Separate fraction-free Gram determinants check independence of every chosen
basis. The resulting census is:

| Support size | Rational rank | Coloops | Characters |
|---:|---:|---:|---:|
| 48 | 8 | 0 | 7 |
| 52 | 8 | 0 | 224 |
| 56 | 7 | 0 | 8 |
| 56 | 8 | 0 | 40 |
| 60 | 8 | 0 | 112 |
| 60 | 8 | 1 | 112 |
| 64 | 8 | 0 | 7 |
| 112 | 8 | 0 | 1 |

The verifier identifies the 112 character/port pairs, checks their rank-seven
punctures and orthogonality, and verifies the rank-nine original pairing. It
does not import predecessor verifiers, read stored spectrum answers, or use
floating-point rank estimates.

## Reproduce

From the repository root, with the Python standard library:

```sh
python3.12 -I -O -B research/polarized-p112-code-bound/verify.py
python3.12 scripts/research_package.py --package research/polarized-p112-code-bound
```

Expected status: `PASS_ONE_SIDED_P112_FITTING_RIGIDITY`.

The read-only replay checks 511 supports, 4,080 basis-row deletions and 4,591
positive integer Gram minors. It exercises positive coloop/non-coloop controls
and rejects nine corruptions, including missing characters, a changed coordinate
bridge and a false coloop. Explicit exceptions keep acceptance checks active
under `-O`. The program prints a deterministic receipt without rewriting files.

The universal reduction from fitting equations to coloops is the written proof
above. We have not formalized it in Lean or replayed a complete supplier.

## Open next questions

Can a pairing with both binary factor codes outside U produce a cheaper native
unit? A first step is to give explicit rational and binary factors, check every
diagonal and required zero, and establish their ranks. A candidate then needs
centre and side programs, restoration, phase adapters and a complete paid moment.
We have no such candidate. [TASK.json](TASK.json) records this acceptance boundary.

## Attribution and coordination

Jose Manuel (@jmbarrancoml) prepared this corollary and direct checker with
substantial OpenAI Codex assistance. Read-only subagents identified the spectral
connection, checked the geometry bridge and performed a separate deletion census.
We claim no independent human review. New work is Apache-2.0.

- Adam Gall (@adamgall), PR1098 head `75834dfc800511cebc0e4c696788e9081272d761`:
  exact support spectra and sharp energy constant four.
- Mihir Srivastava (@mihir-s-05), PR845 head `125ce25bdae421627b56077adc14940c2d0aa52f`:
  original support lemma, rank census and single-lift obstruction.
- DreamingOfClouds, PR717, and the E8/compiler authors retain the geometry
  attribution in [PR845's notice](../p112-single-lift/NOTICE.md).
- icekylinx supplied the unchanged prototype in
  [direct-delivery504-global](../direct-delivery504-global/NOTICE.md).
- Philipp (@mightyOil), PR1191, supplied the related fixed-mask one-sided result.
  Thiago Goulart (@Tuafo), PR1744, supplied the separate fixed-mask rank/broadcast
  theorem that helped frame this investigation.

[Discussion1803](https://github.com/CrocSwap/integer-mult-bounds/discussions/1803)
records the scope and attribution. Source pins are in [SOURCES.json](SOURCES.json).
We leave the selected frontier and predecessor packages unchanged.
