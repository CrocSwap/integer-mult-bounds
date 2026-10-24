# A central-spectrum law for scalar Schur deletion

This contribution was produced by Nick Petalas. Apache-2.0.

**Scoped algebraic proof with exact finite corroboration.** Let P,Q be
commuting idempotent matrices over any field F, with common leading scalar
entry 1. Let S,T be their Schur complements after deleting that entry, and set

```text
h = (PQ)[1,1],  D = S-T,  Z = D^2,  C = ST-TS,  theta = h(2-h).
```

Then

```text
(Z-theta I) C = 0,
Z(Z-I)(Z-theta I) = 0.
```

Thus the central operator Z has no eigenvalues outside `{0,1,h(2-h)}`.
If these three scalars are distinct, Z is diagonalizable over F and its
`theta`-eigenspace equals `im C`, of dimension at most two. The polynomial
retains its repeated factors when theta is 0 or 1. A ternary example below
has nonzero Z with Z^2=0, so replacing the polynomial by its square-free part
is false in general.

This supplies one constraint on the higher-rank residual invariants asked for
in [codyw912's PR4735](https://github.com/CrocSwap/integer-mult-bounds/pull/4735).
The known centrality of Z for arbitrary idempotent pairs is credited to
[Ryanson Jonathan's PR4609](https://github.com/CrocSwap/integer-mult-bounds/pull/4609)
in this repository. The new statement is the specific scalar action of Z on
the commutator image after a commuting scalar identity-pivot deletion.
It is neither a sufficient conjugacy invariant nor a full-guard count.

## Proof over every field

Write the original matrices in blocks as

```text
P = [[1,r],[c,A]],  Q = [[1,s],[e,B]],
S = A-cr,          T = B-es.
```

Here r,s are rows and c,e are columns. Products are ordered as displayed.
Idempotency gives

```text
rc=se=0,  rS=Sc=0,  sT=Te=0,  S^2=S,  T^2=T.
```

For example, P^2=P gives `rA=0`, `Ac=0`, `rc=0`, and `A^2=A-cr`.
Substitution in `(A-cr)^2` proves S^2=S. The proof for T is identical.
These residual facts already occur in the credited Schur lineage.

The top-left block of PQ=QP gives

```text
re=sc=h-1.
```

The top-right and bottom-left blocks respectively give

```text
rT-sS = h(r-s),
Se-Tc = h(e-c).
```

Put `x=e-c`, `y=r-s`, and `w=Tc`. Expanding the bottom-right commutation
identity and substituting the last two equations gives

```text
C = w y + x(sS+h y).                         (1)
```

For clarity, the unreduced equation is

```text
0 = C + Se s - Tc r + c rT - e sS + h(cs-er).
```

Its last five terms reduce to `-w y-x sS-h x y`, proving (1).
Consequently `im C` is contained in `L=span{x,w}`, whose dimension is at most
two. No independence of x,w is assumed.

The same identities determine D on this subspace:

```text
Sx = w+hx,          Tx = -w,
Sw = (1-h)w+h(1-h)x,  Tw = w,
Dx = hx+2w,        Dw = h(1-h)x-hw.           (2)
```

To obtain Sw, apply S^2=S to e and use `Se=w+hx` and `Sx=w+hx`.
Squaring the two equations for D in (2) now gives

```text
D^2 x = h(2-h)x,  D^2 w = h(2-h)w.
```

They are polynomial identities and hold in characteristic two as well.
Together with (1) they prove `(Z-theta I)C=0`.

For any two idempotents, without a commutation assumption on them,

```text
Z = S+T-ST-TS,
ZS = SZ = S-STS,  ZT = TZ = T-TST,
C^2 = Z^2-Z.
```

The first two lines prove centrality; expansion using S^2=S,T^2=T proves
the last. Multiply `(Z-theta I)C=0` on the right by C and substitute
`C^2=Z(Z-I)`. All factors are polynomials in Z, so
`Z(Z-I)(Z-theta I)=0`.

When 0,1,theta are distinct, this annihilating polynomial splits into
distinct linear factors, proving diagonalizability. Equation (1) and the
first identity give `im C` inside the theta-eigenspace. Conversely, if
`Zv=theta v`, then `C^2 v=theta(theta-1)v`, so v belongs to im C. This
proves equality and the dimension bound.

## A necessary repeated root

Over F3 use the commuting diagonal pair

```text
P0 = diag(0,1,0,1),  Q0 = diag(0,0,1,1).
```

Choose first header column `a=(1,1,1,1)^t` and inverse first row
`b=(1,2,2,2)`. They satisfy `ba=bP0a=bQ0a=1` and `bP0Q0a=2`.
Complete the header with the kernel basis of b used by the verifier.
The resulting three-dimensional Schur pair has h=2, theta=0, and nonzero
Z with Z^2=0. The checker constructs the full header, inverts it, and
checks the input hypotheses and the literal Schur complements. Thus this
is an attained deletion example, not merely an arbitrary idempotent pair.
The factor Z^2 in the cubic at theta=0 is necessary.

## Reproduce and verification scope

From the repository root, the exact local interpreter is
`/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12`:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/schur-central-spectrum
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/schur-central-spectrum --check-source-history
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/schur-central-spectrum/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/schur-central-spectrum/verify.py
```

The standalone checker needs only Python 3.12's standard library and the
package files; it has no Git or predecessor-code dependency. It prints
its exact finite histograms, hashes of the package files it read, and
`PASS_SCHUR_CENTRAL_SPECTRUM`. It writes no receipt or generated file.
The stdout hash report is generated from the actual file bytes.

The finite domains are all split pairs for the following fixed diagonal
sector profiles, in sector order 00,10,01,11:

| Field | Sector dimensions | Split pairs | Admitted identity pivots |
|---|---|---:|---:|
| F2 | (1,1,1,2) | 496 | 172 |
| F3 | (1,1,1,1) | 2,160 | 306 |
| F5 | (1,1,1,1) | 78,000 | 4,260 |

Every admitted split tests the new identities on the full-space lifts
`P0-P0abP0` and `Q0-Q0abQ0`. These maps kill a and have image in ker b;
in any completing header they are `diag(0,S)` and `diag(0,T)`. Hence the
lift checks are exactly the claimed polynomial identities for the residuals.
For the first twelve admitted splits in each profile the checker also
constructs the header and compares the lifted matrix with the literal Schur
matrix. The binary profile is the first working example from Mihir
Srivastava's #4689; its 172 admissions are cited corroboration, not a new count.

Another 28 explicit eight-dimensional examples cover every h in each of
F2,F3,F5,F7,F11 and are checked with literal headers. Eight controls reject
missing pivot, idempotency, commutation, field and shape hypotheses; replacing
theta by h; forcing central idempotency; and extending the theta=0 identity
to arbitrary idempotent pairs. All checks use explicit exceptions under -O.
The all-field theorem rests on the written proof, not extrapolation from these
domains. The histograms are corroborating outputs, not complete-header counts.

## Scope, provenance and credit

Canonical base is `624de9dc66858af0945e5f8a0942488d62280d43`, priority revision 7.
The selected conditional kappa remains 0.00302015. The original
`formal-interface-lemma` card is explicitly changed to an algebraic side
question following #4735. This does not discharge a selected supplier premise.
The family decision is to stop at this identity, with complete producer,
consumer, emission, reads, restoration, stock and physical costs still unknown.

The public [claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19132032)
records the original question. Live overlap searches and their limits are
recorded in TASK.json. All-main README and merged-PR searches supplement the
sparse local-note search. An absence of matches is not proof of novelty.
No existing package or selected-frontier file is changed.

Credit codyw912 #4735 for the sufficient-invariant question and residual
recurrence; Mihir Srivastava #4689 for the first binary profile and state
census; Ryanson Jonathan #4609 for the central-operator viewpoint and projector
refinement; ssafwann #4678/#4671 for header counting and sector methods;
Nick Petalas #4597/#4278 for ordered Schur factorization and residual identities;
lee-phys for binary dimension work; and Cinna Davis and the retained normalizer
lineage, source527, commdata2338 and Jose Manuel, for the BIT/header context.
Exact source paths and hashes are provenance entries in SOURCES.json.
No predecessor code is imported. Existing predecessor credit remains unchanged.

Independent human and formal proof-kernel review are unclaimed. Lean, Docker,
the selected cold replay, a sufficient higher-rank conjugacy classification,
block pivots of size greater than one and physical caller admission were not
run or proved. No new kappa or complete multiplication theorem is claimed.

## Open next questions

1. Can the central-operator constraint be combined with image/kernel data to
   give a sufficient residual invariant? Begin with the theta=0 repeated-root
   example and distinguish its nilpotent blocks. The identity is only a
   necessary condition, so completeness is the unresolved obligation.
2. What replaces the scalar action h(2-h) for a common identity block I_d?
   Start from the two-column calculation (1)-(2) with matrix H and retain
   product order. Noncommuting matrix coefficients obstruct treating h as a
   scalar; no larger-block identity is asserted here.

## Verifier engineering limits

The checker has structured finite loops, no recursion, and functions shorter
than 60 lines. Prime fields and matrix sizes are fixed internally; matrices
have at most eight rows, and enumeration materializes at most 625 vectors in
the registered domains. There are no subprocesses, network operations, dynamic
code evaluation or shared mutable caches. Explicit exceptions check the
mathematical invariants in ordinary and optimized Python.

Power-of-Ten rules 3 and 9 require a managed-runtime deviation here. Python
allocates tuples, integers and generator objects during arithmetic, and its
standard library uses runtime dispatch. The scope is this finite standalone
checker; bounded dimensions, finite domains and five package reads of at most
1 MiB each bound live data. Normal and optimized warning-strict registered
replays are the compensating checks. Reassess these bounds before adding an
input-driven search or an external dependency. There is no compiled build or
repository-configured Python type checker for this isolated checker; Python's
warning-strict execution and the package CI replay provide diagnostics.
