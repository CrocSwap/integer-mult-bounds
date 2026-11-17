# Exact bit memory for modular phase caches

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped written proof with exact finite corroboration. For a source
indexed by F2^t with coefficients modulo 2^b, the least persistent cache that
answers its sum after every sequence of coordinate sign changes has exactly

```text
2^B(t,b) states, where B(t,b) = sum_j binom(t,j) max(b-j,0).
```

The lower bound permits arbitrary nonlinear states and zero-error randomized
encodings and updates. An explicit packed subset-sum cache attains it, with
reversible in-place modular updates and no separate phase cursor. For t=2,
b=3 it needs eight logical persistent bits rather than the source's twelve.
For b=2, its width is exactly t+2. The source is not required to be recoverable.
[PROOF.md](PROOF.md) defines the complete contract and proves the formula.

The new contribution changes Ali Romman's
[PR #4958](https://github.com/CrocSwap/integer-mult-bounds/pull/4958)
characteristic-zero linear-cache interface to a finite residue ring, where
integer rank alone does not count states. Its 56- and 112-row historical
values are cited background, not computations or claims of this package.
Boolean zeta/Mobius inversion, Walsh interpolation, the classical Walsh Smith
diagonal and finite-state distinguishability retain their classical credit.
No literature-wide priority claim is made for those ingredients.

## Reproduce

From the repository root with standard-library CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/modular-phase-cache/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/modular-phase-cache/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/modular-phase-cache
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/modular-phase-cache --check-source-history
```

Another CPython 3.12 executable may replace the absolute path. The verifier is
read-only and Git-free. It emits `PASS_MODULAR_PHASE_CACHE` in a generated JSON
receipt bound to all six package files. No receipt is handwritten. The
registered normal and optimized commands have 120-second limits.

The finite checks compare literal phase tables and subset sums with the packed
zeta encoder, enumerate every source in eleven small domains, and enumerate
every packed state in the declared small-state domain. They check image
cardinality, inverse-zeta representatives, every generator, involution,
commutation and longer histories. Larger fixtures reach t=10 and b=16.
Boundary controls reject malformed domains and states; semantic controls show
that one initial sum is insufficient and that the modular quotient cannot
recover exact integer sums. The universal result rests on the written proof.
No predecessor scientific program or certificate is replayed.

The local CPython 3.12.15 normal and optimized checks agree on all 135,798
enumerated sources, 337,268 source/generator transitions, 8,766 enumerated
cache states, 21,564 state/generator transitions and 17,156 commuting pairs.
They also check 220 larger fixtures, 2,200 history updates, 131 closed-form
parameter cases and eleven rejected inputs. The two direct registered
commands took 4.636 and 4.539 seconds locally. These are check durations,
not a performance comparison. The combined registered replay passed.
Three disposable implementation mutations, changing the ADD sign, omitting
negation and skipping a zeta axis, were rejected by the literal comparisons.
The longest function has 29 physical lines. No separate static-analyzer
or independent mathematical review is claimed.

## Scope and limitations

This is a modular observation cache, not lossless storage of the source.
Every source-dependent header or controller state counts toward the lower
bound. The upper construction has no source-dependent external transcript.
The B-bit claim counts persistent logical information. Python object sizes,
source loading, temporary arithmetic, output storage, physical movement and
instruction costs are not claimed to fit in B bits.

There is no asserted transfer to exact complex queries, unbounded integers,
source restoration, omitted carries or the selected word. A source-preserving
physical caller and its complete invoice remain missing. No native supplier,
selected assumption discharge, new kappa, complete multiplication theorem,
independent human review or formal proof-kernel acceptance is claimed. Lean,
Docker and the selected cold replay were not run. The selected frontier and
all five framework assumptions remain unchanged.

The historical source is pinned as provenance in [SOURCES.json](SOURCES.json).
It supplies motivation, not a live input. [TASK.json](TASK.json) records the
change from the centre-path-sharing card to this finite-ring side result.
The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19601590)
pins canonical base e54523517d0f03e58352e647c403a5af3e525a57, priority revision
8 and selected #7000. The first card control passed
`PASS_RESEARCH_BASELINE_BINDINGS_ONLY`; it is metadata orientation only.

Overlap checks included live open/account PRs, recent handoffs, active
Discussions, merged searches and all-main README searches for modular phase
caches, nonlinear caches and Walsh/Smith state counts. The overlap cache
reported 846 open PRs and 7,482 Discussion records, with complete remote
pagination. Its sparse local search covered 215 of 10,178 note paths;
the all-main searches cover omitted READMEs. Arbitrary code diffs, unindexed
prose and unpublished work remain limits, and no-match is not novelty proof.

## Open next questions

Can one source-bound caller use only these modular observations and safely
discard the quotient kernel? First specify the output modulus, every later
read and all carry/restoration obligations. Its physical boundary and full
paid invoice are missing. The present result alone does not justify a
construction campaign. The structured question is in TASK.json.

## Verification bounds

The single verifier has no recursion, subprocess, network access, dynamic code
or output files. Its public constructor accepts 0<=t<=10 and 1<=b<=16.
At most 1,024 source coefficients, cache fields or layout entries are live
per construction. The source census has at most 65,536 inputs per fixture;
its transcript dictionary retains at most 4,096 records. The state census
admits at most 4,096 states per fixture. Functions stay below 60 lines.
Explicit contracts remain active with assertions disabled. File reads for
receipts are bounded at 256 KiB each. Warning-strict normal/optimized runs,
in-memory compilation and AST inspection are the available diagnostics.

Power of Ten rule 3 deviation: CPython arithmetic and containers allocate
during evaluation. This terminating verifier bounds input dimensions,
retained dictionaries and integer widths, and claims no fixed-allocation
runtime. A fixed-storage port would need its own arithmetic and receipt
implementation before use in an allocation-prohibited environment.
Rule 9 deviation: eleven fixed no-argument rejection closures invoke the
same local validation functions. Their target set and lifetimes are bounded
by `controls`; each is executed once and its exact error is checked.
