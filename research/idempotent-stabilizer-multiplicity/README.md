# Exact orbit multiplicities for ordered idempotents

This scoped finite-field counting proof was produced by Nick Petalas.
Apache-2.0. It extends the factor descriptor of
[MatShep, PR4762](https://github.com/CrocSwap/integer-mult-bounds/pull/4762)
with the exact size of each simultaneous-conjugacy orbit. The new step is an
exact centralizer sequence and its extension-group order. The predecessor's
classification and active-dimension theorem are cited, not re-audited.

The result supplies a weight for a residual state once its smaller factor-data
stabilizer is known. It does not enumerate a transition table, count passing
headers, price a physical caller or improve kappa. Independent human and formal
proof-kernel review are unclaimed.

## Statement

Let P,Q be ordered idempotents on an n-dimensional space V over F_q, where q
is any prime power. Use the predecessor's rank factorizations

```text
P=XY, YX=I_r,     Q=ZW, WZ=I_s,
U=F_q^r direct-sum F_q^s,
C=[X Z]:U->V,     D=[Y;W]:V->U,
K=ker C,          L=im D,          M=DC.
```

Set a=rank C, b=rank D, c=rank M and

```text
h=a-c,          j=b-c,          z=n-a-b+c.
```

All three numbers are nonnegative. The predecessor identifies n-z as the
minimum active dimension. Define the factor-data stabilizer

```text
H = {g=diag(A,B) in GL_r(F_q) x GL_s(F_q):
     gK=K, gL=L, gM=Mg}.
```

Write G_d(q)=|GL_d(F_q)|, with G_0(q)=1. Then the simultaneous centralizer
Z(P,Q) in GL_n(F_q) has order

```text
|Z(P,Q)| = |H| G_z(q) q^(hj+hz+jz).                 (1)
```

Consequently the simultaneous-conjugacy orbit of the ordered pair has size

```text
G_n(q) / (|H| G_z(q) q^(hj+hz+jz)).                 (2)
```

If the first projector is fixed to diag(I_r,0), the number of second
projectors in this pair's orbit under its centralizer is

```text
G_r(q) G_(n-r)(q) / (|H| G_z(q) q^(hj+hz+jz)).      (3)
```

These statements include zero ranks, full ranks, coincident projectors and
noncommuting pairs. They do not require invertibility of M.

## Proof

Every f in Z(P,Q) preserves im P and im Q. Their chosen image bases define
unique A in GL_r and B in GL_s with fX=XA and fZ=ZB. Commuting with P also
gives Yf=AY: indeed YP=Y, Pf=fP and YfX=A. The same argument gives Wf=BW.
Thus, with g=diag(A,B),

```text
fC=Cg,          Df=gD.                             (4)
```

These equations imply gK=K, gL=L and Mg=gM. Restriction therefore defines
a group homomorphism rho:Z(P,Q)->H.

The map rho is surjective. For g in H, consider the two systems (C,D) and
(Cg,g^-1 D). Their C kernels, D images and DC products agree. The
inclusion/observation extension lemma of codyw912 PR4735, generalized by
MatShep PR4762, supplies an invertible f with fC=Cg and (g^-1 D)f=D.
Those are (4), which in turn imply fP=Pf and fQ=Qf. This uses the cited
extension lemma without checking its predecessor census.

It remains to count the kernel of rho. Put A0=im C and B0=ker D.
The restriction of D to A0 has rank c, so T=A0 intersect B0 has dimension
h. Choose a complement R of T in A0, a complement Z0 of T in B0, and a
complement J of A0+B0 in V. Their dimensions are c,z,j respectively:

```text
V = T direct-sum R direct-sum Z0 direct-sum J.
```

An element of ker rho fixes A0 pointwise and satisfies Df=D. Conversely
these two conditions characterize ker rho. Relative to the displayed
decomposition its matrix is exactly

```text
      T  R  Z0 J
T   [ I  0  U  V ]
R   [ 0  I  0  0 ]
Z0  [ 0  0  G  E ]
J   [ 0  0  0  I ].                                (5)
```

Here U is any h-by-z matrix, V any h-by-j matrix, E any z-by-j matrix,
and G any invertible z-by-z matrix. To see necessity, f-I vanishes on A0
and takes all other vectors into B0=T direct-sum Z0. Invertibility is
equivalent to invertibility of G. Each such matrix also suffices, with no
further constraints. Hence

```text
|ker rho| = G_z(q) q^(hz+hj+zj).
```

The finite exact sequence 1->ker rho->Z(P,Q)->H->1 proves (1). No splitting
of this sequence is asserted or needed. Orbit-stabilizer proves (2).
The centralizer of diag(I_r,0) is GL_r x GL_(n-r), which proves (3).

## First fixture and checks

Use the sharp rank-one pair displayed in MatShep's package:

```text
P = [1 1 0],       Q = [0 0 0].
    [0 0 0]           [1 1 1]
    [0 0 0]           [0 0 0]
```

It has h=j=1, z=0 and |H|=q-1. Its centralizer therefore has order
q(q-1). Appending one simultaneous zero coordinate changes that order to
q^3(q-1)^2. Over F2 these orders are 2 and 8. Over F3 they are 6 and 108,
and over F5 they are 20 and 2000. These are algebraic illustrations of (1),
not newly claimed classifications of the displayed pair.

The standalone verifier tests (1) against direct matrix commutation on
859 fixed-first-projector pairs. Each listed domain enumerates every second
projector of the specified rank. It independently checks domain completeness
against the ordinary idempotent count G_n/(G_s G_(n-s)).

| q | n | r | s | Second projectors |
|---:|---:|---:|---:|---:|
| 2 | 4 | 1 | 1 | 120 |
| 2 | 4 | 2 | 2 | 560 |
| 3 | 3 | 1 | 2 | 117 |
| 5 | 2 | 0 | 1 | 30 |
| 5 | 2 | 1 | 0 | 1 |
| 5 | 2 | 1 | 2 | 1 |
| 5 | 2 | 2 | 1 | 30 |

The direct count enumerates GL_r x GL_(n-r) and retains matrices commuting
with Q. The formula separately enumerates GL_r x GL_s and tests its action
on ker C, im D and M. The two centralizer calculations do not share a
commutation test for their different ambient spaces. They share elementary
finite-field matrix arithmetic. The verifier does not build class signatures
or compare the predecessor's state counts.

Five omission controls use these direct counts to reject deletion of each
factor q^hj, q^hz, q^jz, G_z and |H|. The output records a concrete mismatch
for each detected omission. Six sharp-pair fixtures cover q=2,3,5 and z=0,1.
A capacity control rejects enumeration of all 3^(4*4) matrices. The written
proof covers extension fields; the finite checks use prime fields only.

Every successful invocation prints a generated JSON record containing results
and SHA256 hashes of all five package files. No receipt is written by hand.

## Reproduction and implementation limits

From the repository root, with the local interpreter used for this package:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/idempotent-stabilizer-multiplicity/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/idempotent-stabilizer-multiplicity
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/idempotent-stabilizer-multiplicity --check-source-history
```

The registered checks use normal and optimized Python, with warnings treated
as errors. A reviewer can use any CPython 3.12 interpreter in place of the
machine-specific path. The verifier needs only this package and the standard
library; predecessor files are historical provenance, not runtime inputs.

The implementation has no recursion. All census parameters are fixed in main;
no raw enumeration exceeds 65,536 matrices. Matrices have at most eight rows
and columns, and the GL cache has at most twenty entries. Each function is
under sixty lines. Python's managed runtime allocates small bounded temporary
matrices; this is the documented fixed-allocation deviation from Power of Ten.
The dataclass decorator and bounded cache are explicit library mechanisms,
rather than generated arithmetic. Explicit exceptions preserve all scientific
checks under -O. There is no external process, network access or output file.

Computing H can still require an exponential search in r and s. Formula (1)
removes the extension-space enumeration once H is known; it is not a general
polynomial-time canonical-form algorithm or a measured runtime comparison.
No full-guard recurrence, physical header cover, recursive implementation,
precision/tape analysis or stock bound follows. No selected cold replay, Lean
or Docker run is needed or claimed. Selected kappa stays 60403/20000000.

## Sources and scope

Base main is 624de9dc66858af0945e5f8a0942488d62280d43, priority revision 7.
This changes the formal-interface-lemma card to a finite-field algebraic side
result. The first working orientation used research_selected_baseline.py,
the current-priorities replacement for the card's historical baseline command;
it passed the selected source-binding check. Family decision: narrow to the
orbit-weight formula and stop. A useful residual-state weight does not price
any missing physical consumer, so it justifies no construction expansion.

- MatShep, [PR4762](https://github.com/CrocSwap/integer-mult-bounds/pull/4762),
  head 3b4e0449262b0b1e07b80e009ef71cc0ca5bf816, supplies the complete
  (K,L,M) descriptor, active dimension and explicit transition-multiplicity
  question. Its README is pinned as historical provenance in SOURCES.json.
- codyw912, [PR4735](https://github.com/CrocSwap/integer-mult-bounds/pull/4735),
  head 4afbea22e79e19d1d65702eb4090d454ee39d967, supplies the original
  inclusion/observation extension argument and residual-transition context.
- Mihir Srivastava, [PR4689](https://github.com/CrocSwap/integer-mult-bounds/pull/4689),
  supplies the seven-state motivation. The retained lineage includes ssafwann
  PR4678/PR4671, Nick Petalas's ordered Schur/header work, Ryanson Jonathan,
  lee-phys, Cinna Davis and the source527, commdata2338 and normalizer sources.
  No earlier numerical result is republished as a new contribution here.

Live PR titles/bodies, latest handoffs, active Discussions and distinct main
README and merged-PR searches found no matching formula within their coverage.
The card-wide helper snapshot searched 428 open PRs and 3,964 discussion
records, but only 111 of 6,319 local note paths were materialized then. The
separate main README search includes omitted packages. Arbitrary package files,
PR diffs and unpublished work remain outside these novelty checks.

## Open next questions

1. Can the factor stabilizer H be computed without enumerating GL_r x GL_s
   for one actual higher-rank residual family? That is the remaining algebraic
   cost in (1). First express the block-diagonal commutation and K/L constraints
   as an endomorphism algebra, then count its units. The algebra's radical and
   semisimple structure are not supplied here.
2. Can these orbit weights be used in a caller-specific split-transition
   table? First pin one residual ensemble and count split maps into each
   descriptor orbit, using (1) for its stabilizer fibers. The present theorem
   supplies weights only; split incidence and all physical costs remain open.
