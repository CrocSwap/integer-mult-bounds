# Local frame-compiler search, frozen through PR62

All experiments in this directory use the pinned PR62 pair graph at
`ad0f25ff7b23cff7f08ad237c2254e6ecf74257e`. No later community source is consumed.
The original checkout is unchanged. Each emitted word and compiler copy has
a SHA256 recorded in its `compiled.json`; changed words are sent separately
to the independent literal replay and profile verifier.

## New dependency-circuit choices

The inherited compiler reduces retired fresh-signal rows against the current
live anchors and an echelon basis of compatible retired rows. Instead of
accepting the first dependent retired row, the new selectors collect the
available fundamental dependency circuits and choose a circuit by one of:

- total charged target/provider rank growth (`all_growth`);
- number and rank growth of other retired providers (`all_collateral`);
- anchor-only dependence before general retired dependence (`anchor_first`);
- actual physical transition child-profile moment cost (`profile_cost*`).

Every clearing XOR and every target/provider frame promotion is still emitted
and charged. A zero fresh-signal row can contain arbitrary physical dirty state;
its reuse is justified by the complete reversible word, not by claiming that
the physical register is initialized to zero. The compiler runs both complete
dirty-basis orientations, and the independent verifier repeats them.

For the last selector let `C(A,B) = sum_t n_t(A,B) F_t`, where the `n_t` are
the exact inherited fixed-I+J pivot-run profile of the physical frame transition
and `F_t = t exp(a log(m/t))`. A candidate target `s` at old frame `A_s`, cleared
into frame `G` with providers `z`, is priced by

```
C(A_s,G) - C(A_s,I)
  + sum_z [C(A_z,G) + C(G,I) - C(A_z,I)].
```

This accounts for immediate promotions and the change in deferred cleanup,
assuming each other retired provider remains retired until cleanup. Future
reuse couples decisions, so this is a discovery heuristic, not an additive
global optimality certificate. Linear rank mass cancels between candidates;
`t*expm1(a*log(m/t))` avoids cancellation in floating discovery prices.
Missing transition profiles are recorded and collected for the next iteration.
Once a run has zero missing pairs, every local price uses an actual transition
profile. The final saving is accepted only through exact rational whole-profile
moment bounds and all assembly gates.

`build_pair_oracle.py` is a local adaptation of the frozen C++ profiler that
additionally exports each transition histogram. It preserves the projector,
pivot, bounded-minor and three-prime CRT routines. Its synthetic transition-list
input is an oracle request, not a physical executable word. Each immutable
profile dump and the source/header hashes are recorded.

## Moment-ordered carry selection

The `--weighted` experiment orders the inherited linear/partition-matroid
candidate edges by their physical transition moment change before the original
greedy initialization and augmenting paths. For a value produced at `P`,
preserved through donor frame `G`, and carried to future target `T`, its
no-reclamation child-cost change is

```
C(G,T) - C(G,I) - C(0,P) - C(P,T).
```

At fixed cardinality, role and external-volume corrections are common to all
edge choices in the same axis. The inherited augmenting algorithm still seeks
maximum cardinality; it does not optimize the weights globally. Reclamation
adds coupling, so only the changed whole-word profile can establish an actual
improvement. This experiment makes no minimum-cost matroid claim.

The `--exchange` variant starts from the frozen original maximum-cardinality
matching and tries bounded improving one-edge exchanges. A new edge may replace
the old donor of the same use when its donor block stays linearly independent;
or it may replace a selected edge in the same donor block and serve an unused
use. Both preserve cardinality and distinct-use constraints. The `--cycle`
variant additionally tests two-edge donor/use cycles, checking the independence
of both changed blocks. No improving two-edge cycle was found in the tested
native-price instance; this is not a proof that longer cycles cannot improve it.

## Joint basis and schedule search

`--basis shift1` profiles all candidate physical transitions after the point
permutation `i -> (i+1) mod h`, while preserving their original frame IDs.
Matching and reclamation are then priced in that basis. The emitted word is
renamed by `relabel_word.py`: all frame masks, canonical source/output triples,
common points and scatter port indices change together. Scratch slots and
literal XOR instructions are retained. The complete triple family and the
permutation-invariant `I+J` basis are inherited; every final renamed word still
gets fresh full-basis and actual physical-profile verification.

This joint search differs from merely relabeling an already selected schedule:
the selected carries and clearing circuits are optimized under the new ordered
pivot-run prices. It remains a bounded discovery heuristic.

## Regeneration

The frozen graph/matching setup and a moment-cost exchange run are generated by:

```
python -S collect_matching_pairs.py --h 23
python -S build_pair_oracle.py --h 23 --strategy matching_collect
python -S run_strategy.py --h 23 --strategy profile_cost --exchange
```

Repeat at `h=25`. For joint search, add `--basis shift1` to the oracle and
strategy commands. Reclamation may encounter transitions absent from the
initial carry-edge inventory. Run the oracle again on the emitted strategy
directory with `--incremental`, then run a new strategy label. The new label
must start with `profile_cost`; output directories are never overwritten.
`compiled.json` records the exact oracle dump hash, missing-pair count, word
hashes and source pin. Immutable earlier oracle dumps are retained by SHA256.
Use `--oracle path/to/the-immutable-dump.jsonl` to reproduce the prices of a
specific recorded run instead of consuming the subsequently enlarged cache.
The initial compiler matching cache is accepted only if its complete candidate
edge list matches the current frozen graph and every restored selected block
passes the same linear-independence check.

The runner saves an immutable source copy and its hash for later runs. Floating
`expm1` prices at discovery saving `a=0.00005103` select proposals only. Neither
those prices nor their reported local gains are used as an arithmetic witness.

## Acceptance boundary

The independent verifier checks all input and dirty basis vectors in both
orientations, exact literal-scatter incidences, causal nested physical frames,
event equality reconstructed from the actual XOR word, rank mass, actual child
profiles and CRT agreement. It then computes the whole mixed-axis recurrence
and exact rational moment/assembly witnesses. Existing all-size geometry,
analytic envelopes, compiler/tape arguments and the surrounding reduction are
inherited from frozen PR62. A finite profile improvement does not by itself
formally prove those inherited hypotheses.

Reduced XOR count alone is not accepted as an exponent improvement. In this
search `all_collateral` and `anchor_first` reduced clearing XORs but worsened
the certified characteristic. Actual child-size distributions decide the
saving, even when both physical-role counts and total rank mass are unchanged.
