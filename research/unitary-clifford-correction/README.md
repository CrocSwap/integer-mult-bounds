# Exact Clifford correction rank under unitary encoding

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped written mathematical proof with exact finite corroboration.
For q=2^s independent forward rank-one Clifford lanes, one phased width-(s+1)
Clifford tensor child under a square unitary reciprocal encoder needs correction
rank exactly

```
q - 2^floor(s/2)
```

when its phase and direction are optimized. For a fixed child with multiplicities
m_0,m_1,m_2,m_3 at 1,i,-1,-i, the exact optimum is m_2+m_3. In particular the
sixteen-lane optimum is twelve, attained by an explicit real orthogonal encoder
whose entries are 0 or +/-1/4. Every input coordinate is arbitrary and retained.

The cited unrestricted invertible-encoder optimum six belongs to
[ywz65 / PR2516](https://github.com/CrocSwap/integer-mult-bounds/pull/2516).
The new result explains why that rank cannot be retained if the encoder must
preserve Euclidean norm. It changes the encoder hypothesis and does not audit,
replay or contradict the predecessor. Algebraic rank is not a count of paid
recursive children or native ADDs. No new kappa or selected-frontier change
is claimed.

## Proof and evidence

[PROOF.md](PROOF.md) proves the lower bound for every complex unitary encoder.
The Hermitian functional Q(A)=Re((1-i)A) equals I on the desired spectrum and
I-2P_bad on the candidate. Equality on a vector forces P_bad v=0. Rank-nullity
therefore charges both unwanted eigenspaces. Orthogonal spectral matching
attains the bound. A root filter gives the all-size closed form.

The standard-library verifier reconstructs the complete finite operators with
Gaussian integer numerators and explicit denominators. It emits a generated
six-file SHA256 receipt, with these enumerated checks:

- 520 phase/direction spectral cases through child width 65, comparing a
  binomial formula with an independent cyclic recurrence for the new rank law.
- 40 full operator cases through 32 coordinates and all 10,912 tensor entries
  against a separate Hamming-distance kernel. Each case checks encoder
  orthogonality, the full intertwining identity, correction unitarity and
  the complete arbitrary-input endpoint.
- Exact correction ranks from 2-by-2 Gaussian determinants, corroborated by
  elimination over F5 and F13. Both lower bounds match the exact block ranks.
- All 322,768 spectral permutations in the declared small domains and 31
  rational rotations that mix the sixteen-lane encoding. The permutations
  exhaust only spectral matchings; the proof covers arbitrary unitaries.
- Seven rejected domains or mutations and four semantic control groups,
  including a nonunitary rank-one escape, omitted correction and the failure
  of using only the larger unwanted multiplicity.

These checks corroborate the written proof; they do not establish its universal
quantifiers by finite enumeration. The verifier imports no predecessor code,
needs no network or Git, and writes only its stdout receipt. No receipt is
hand-written or stored as a golden output.

## Reproduce

From the repository root with CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/unitary-clifford-correction/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/unitary-clifford-correction/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/unitary-clifford-correction
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/unitary-clifford-correction --check-source-history
```

Another CPython 3.12 path may replace the local path. The direct marker is
`PASS_UNITARY_CLIFFORD_CORRECTION`; registered replay also prints
`PASS_REGISTERED_RESEARCH_PACKAGE`. Both warning-strict modes are registered
with 60-second timeouts. The initial complete direct check took under one
second on CPython 3.12.15. This is a replay-duration observation, not a
performance improvement claim. Publication-byte/source-history checks are
separate from mathematical acceptance.

## Scope and source record

[Sources](SOURCES.json) pin canonical main
7c49fe32c55de02c2c873655c804b16e4c3fef0a and the retained README context of
PR2516 and Arham Tahir / PR1920. All are provenance, not live executable
inputs. [TASK.json](TASK.json) preserves the revision-8 card and records its
changed scope from physical synthesis to this norm-constrained boundary
lemma. The selected baseline bindings passed as orientation only.

The new statement quantifies over complex unitary encoders. It does not exclude
arbitrary invertible encoders, independent entry/exit adapters, multiple
children, clean subspace promises, discarded outputs or a different tariff.
Encoding and correction realization, coefficient reads, native frames,
routing, storage, restoration, precision, stock, compiler and complete caller
funding remain unpriced. The inherited joined-volume upper expression already
loses with free adapters; this package does not reopen that physical route.
All five selected framework assumptions remain. Independent human and formal
proof-kernel review are unclaimed. No selected cold, native/compiler, Lean,
Docker or predecessor scientific replay is required or run.

## Verification design

There is no recursion, runtime code generation, subprocess, network operation,
external scientific dependency or externally supplied search parameter.
Functions are below sixty lines. Dense matrices have at most 32 rows and
columns. Spectral widths are at most 65, and the largest permutation domain
has 8! elements. Cases are streamed. The complete call graph uses direct
functions, and failure propagates through explicit exceptions active under
optimized Python. Warning-strict execution and AST inspection provide the
available diagnostics; a separate static analyzer is not claimed.

Power of Ten rule 3 has a managed-runtime deviation in verify.py. CPython
integers, tuples, lists and JSON serialization allocate during this bounded
replay. Matrix capacity, fixed iteration domains, six receipt files each
capped at one MiB and no retained case history bound live data. Both registered
modes exercise the full domain. A future externally parameterized or embedded
implementation needs explicit bit and storage capacities before expanding
these limits. No fixed-allocation runtime claim is made.

## Open next questions

1. What is the least encoder condition number that permits the cited rank-six
   sixteen-lane optimum? A positive lower bound above one would quantify the
   norm-versus-rank tradeoff. Start with one unwanted two-eigenvalue block and
   its singular values. The current theorem settles only condition number one.
2. Can an actual consumer exploit this orthogonal rank-twelve boundary under
   a changed favorable volume tariff? First specify the consumer, exact data
   volume and complete paid bill. The present encoder formula supplies no
   physical implementation, and the inherited joined-volume tariff loses.

Neither question is reserved. This contribution stops at its first verified
algebraic improvement.

## Credit and overlap

Credit ywz65 / PR2516 for the unrestricted correction construction and explicit
physical-boundary question; Arham Tahir / PR1920 for the reciprocal-encoding
contract and obstruction; Greer Guthrie / PR679, Ross Richardson, ToikY /
PR1924, Douglas Colkitt / PR665, Jose Manuel and Cinna Davis / PR1779, Josie
Elliston / PR1817, icekylinx, DreamingOfClouds and the retained native/kernel
lineage. Walsh bases, supporting functionals, spectral matching and rank-nullity
are classical. The new theorem and checker are produced by Nick Petalas.
Existing sources and their credit are unchanged.

Jeremy Diviney's PR836 concerns formal group-algebra rank transport, and
ywz65's PR2491 concerns a centre-reader intertwiner. Neither gives this
one-child full-space correction optimum or is replayed here. The live queue,
recent account work, main README/object/formula terms, merged general-form
searches and local reservations were checked before the
[advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19362348).
The cached overlap report explicitly has incomplete sparse historical coverage.
Arbitrary historical diffs and unpublished work remain coverage limits.
