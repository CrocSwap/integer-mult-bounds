# Sharp quarter-dimension repair for two Gaussian banks

For `N=2^t`, `t>=2`, separating one Walsh/Gaussian transform into two balanced
independent coordinate banks requires ordinary correction rank at least `N/4`.
The minimum is exactly `N/4`, even when the independent target must be unitary
after normalization. A four-coordinate reflection and its tensor extensions
attain it with exactly `N/4` commuting invertible rank-one updates.

Claim type: scoped written proof with exact finite corroboration. This is an
original interface obstruction motivated by the binding complex supplier.
It does not give a physical tariff, an unfavorable complete signed moment,
a new supplier, a kappa improvement or a complete multiplication theorem.
All five selected framework assumptions remain.

The input and output coordinate partitions may differ. Both have equal bank
sizes. Invertible monomial adapters are free, and both resulting invertible
bank maps may be chosen freely. General encoders mixing coordinates across
banks are outside the theorem. Ordinary rank on `N` address coordinates must
not be substituted for the binary frame rank of a recursive child.

Read [PROOF.md](PROOF.md) for the contract, classical submatrix inequality,
sharp reflection identity and exact Gaussian monomial equivalence. The
attaining bank maps are specified there. They are not asserted to be two
preassigned native jobs. The separate `N=2` minimum is one.

## Reproduce

From the repository root, with CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/balanced-walsh-pooling/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/balanced-walsh-pooling/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/balanced-walsh-pooling
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/balanced-walsh-pooling --check-source-history
```

Any CPython 3.12 executable can replace the absolute interpreter path. The
direct verifier is read-only and Git-free. It prints a generated receipt
bound to every package file, followed by `PASS_BALANCED_WALSH_POOLING`.
The universal result rests on the written proof, not finite extrapolation.

The complete finite evidence consists of:

- All 4,940 balanced row/column subset pairs at `N=2,4,8`. Exact rational
  elimination and separate modular elimination over F101 agree. At `N=8`
  the submatrix rank counts are 84 of rank two, 1,344 of rank three and
  3,472 of rank four.
- Five complete sharp operators at `N=4,8,16,32,64`. Their exact correction
  ranks are `1,2,4,8,16`. A literal sequence of fiber reflections agrees
  with a separately constructed block target. Full target rank, both
  cross-block zeros, orthogonality and repair involutivity are checked.
- All 5,456 raw Gaussian tensor entries at those sizes. The literal
  `[[i,1],[1,i]]` tensor entries agree with independent monomial factors.
- Fifteen omitted-reflection controls, five rejected invalid inputs,
  an uncorrected pooling counterexample and the exact two-address boundary.

No predecessor scientific verifier or receipt is imported or replayed.
The selected bindings-only orientation passed. Selected cold replay,
physical implementation, Lean and Docker are not part of this package.
Independent human and formal proof-kernel review are unclaimed.

## Scope and provenance

The canonical base is `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority
revision 8 and selected PR6030. [TASK.json](TASK.json) preserves the drawn
`complex-rank-shape-decoder` card and records the change to this original
pooling question. [SOURCES.json](SOURCES.json) pins historical provenance.
The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19373319)
describes the same delivered scope.

Live handoffs, active Discussion titles, open/account PR lists, main READMEs,
merged/general-object searches and the repository overlap helper were checked.
Arbitrary historical diffs, sparse unmaterialized notes and unpublished work
remain coverage limits. This is not a follow-up to the recent unitary
reciprocal-encoder result PR6443: its fixed repeated-lane target, reciprocal
encoder and spectral optimization are replaced by independent coordinate
partitions, monomial endpoints and freely chosen bank targets.

## Verifier bounds

The retained code has no recursion, subprocess, network or artifact writes.
Every matrix dimension is at most 64. The census has exactly 4,940 pairs;
every elimination has at most 64 pivots and rows. Each function is shorter
than 60 physical lines. Explicit exception contracts remain enabled under
optimized Python. Warning-strict execution and an AST inspection are the
available local diagnostics; no repository-wide static analysis is claimed.

Power-of-ten rule 3 has a managed-runtime deviation in `model.py` and
`verify.py`: CPython and Fraction arithmetic allocate during verification.
The verifier admits no external numerical input, fixes the five operator
sizes, retains only bounded matrices and reads each of seven receipt files
with a 128 KiB limit. These domain bounds and scoped file handles constrain
live resources; they are not a fixed-allocation guarantee. A future larger
domain must establish new capacity bounds before changing these limits.
All other inspected control paths use direct bounded loops, shallow data,
explicit contracts and short functions. There is no metaprogramming.

## Open next questions

1. For one actual pair of desired native bank operators, what correction and
   complete physical bill are achievable? Pin a chronological pair and its
   entry/exit frames and arbitrary dirty inputs, then compute its full
   correction. Causal access, native delivery and restoration remain blockers.
2. Can a paid cross-bank encoder and its inverse evade this coordinate
   obstruction and still improve the signed moment? Specify both maps and
   their producer/consumer contract first. Target debits, precision, stock,
   tape and the complete invoice must be included.

Structured first steps and blockers are in TASK.json. No follow-on scope is
reserved by this package.

## Credit

This contribution was produced by Nick Petalas. Apache-2.0.
The Hadamard submatrix rank inequality is classical and is credited to
Lokam's spectral method. Walsh orthogonality, Householder reflections and
rank telescoping are also classical; no literature-priority claim is made.
[PROOF.md](PROOF.md) gives primary-source references and the repository
lineage, including Greer Guthrie's PR679 selector-batching warning, Arham
Tahir's PR1920 reciprocal-encoder obstruction, ToikY's PR1924 clean encoding,
ywz65's nonreciprocal correction result and the retained native authors.
Their results are cited context, not audit targets or new claims here.
