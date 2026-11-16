# LOANBUILD engine: how to run it

LOANBUILD is an exact builder for SYLforge's stationary-lifetime device (#7616/#7620). It works on P104 native words (schema p104-accumulated-block-composition/2). All code is ours; SYLforge's words were read only as data. Credit SYLforge for the device.

## The move
1. Register r drops an interior stop X from its path A→X→B, so it now goes A→B.
2. A partner p takes one extra stop:
   - side B: p is the source of r's write at X, and p inserts B after X;
   - side A: p is the reader of r at X, and p inserts A before X.
3. r's work at X is carried by:
   - a loan through a carrier c, a public register whose path runs A→X→B consecutively;
   - stationary owned snapshots (INIT at X, one write, one read, dirty CLEAR);
   - on side A, a signed role swap between r and p.
4. Native κ cost: each instance swaps one 3|1 hop merge against one 1+2 split, about +0.0015% κ.

## Files
- `lb.py` is the core.
  - `Word(W)` builds indices: register stays (`seg`), ops per register, owned live intervals, the owned-live profile, and projected-state checkpoints every 500 events.
  - `Cand` holds one candidate: original program minus deletions plus keyed insertions. Coefficients written as `'$name'` are unknowns.
  - `Cand.solve()` replays only the affected window (mod 2^61−1, 4-dim random projection), once with all unknowns at 0 and once per unknown at 1.
    - It solves the affine system so the window-end state equals the original. It also requires every pre-existing owned observation (source and destination content at each owned-touching op) and every CLEAR content to match.
    - It rationalises the solution and re-checks it.
  - `instantiate()` writes the word and drops empty INIT/CLEAR pairs.
  - `free_label` picks an owned label that is not live over the needed interval and keeps peak ≤ 50.
- `tpl.py` holds the templates.
  - `build_B(Wd, r, X, p, carrier, beta, snap)`:
    - loan c += β·r at A, placed just before c leaves A;
    - c's existing X-transfer into p carries ρ;
    - readers re-read p, or a snapshot of p;
    - at B: unknown settles p += ζ·r and c += ε·r, then r's write relocated as r += q·p.
    - β is enumerated from c's transfer coefficient; the other coefficients are solved.
  - `build_A(Wd, r, X, p, carrier, snap, early)`:
    - at A: p += α·r, swap r += b·p, loan r += β·c;
    - at X: p picks up r's earlier writes from their sources, directly or via a snapshot;
    - at B: settle r += ε·c. b, β and ε are solved.
  - Slides keep the timing legal:
    - `slide_earlier` moves r's late A-ops and p's late Z-ops before the cut;
    - `slide_later` moves r's B-ops after the settle, cascading through later stops.
    - Partners must sit on the same chart and be untouched in between.
  - `try_instance(Wd, r, X, p, side)` loops over carriers × snapshot/no-snapshot (and β on side B) and returns the first exact solution, or failure reasons.
- `check.py` `full(base, new)`:
  - fastx rows equal for all registers, plus structure;
  - every base owned lifetime's observation trace, CLEAR content included, present unchanged;
  - new lifetime count, peak, labels, non-dyadic count.
- `run7621.py` is the driver:
  1. exact census of both template shapes, gain-ordered by the convexity margin of x ln x;
  2. greedy `try_instance` over the list;
  3. each candidate is accepted only if `check.full` passes, peak ≤ 50 and PRICEKIT κ rises;
  4. after each pass it re-censuses; it stops on a pass with no hits.
  - It writes `<out>_<n>.json.gz` (n = instances landed) and `<out>_log.json`.
- `control.py` is the positive control. It reads (r, X, partner, side) from #7620's word as data and rebuilds those instances on #7617.

## Run it (Python 3.12 + standard library; everything is vendored in this directory)
`pricekit.py` (the exact pricer), `fastx.py` (randomised-exact replay) and `jl.py` (kappa of a native word under the signed #7113 caller, `data/7113_CALLER.json`) sit next to the scripts, and every path is relative to the script. Run from the package root or anywhere.
```
python3 engine/run_on.py WORD.json.gz [OUT_PREFIX] [MAX_PASSES]
    # census -> greedy loan + snapshot passes -> re-census on any P104 native word (about 1 minute on #7621's word)
python3 engine/run_on.py data/base-7621-word.json.gz /tmp/out       # writes /tmp/out_14.json.gz and /tmp/out_log.json = data/word.json.gz, data/instances.json
python3 engine/control.py                                           # controls on #7617 using #7620's instances as data; expect {'rebuilt': 39, 'fail': 6, 'no partner': 1}
python3 engine/control.py 258@829 464@526                           # the two named controls (same carriers and coefficients as SYLforge)
python3 -I -B check.py engine                                       # the packaged test: rerun on #7621, require JSON-equality with data/word.json.gz
```
Independent exact check of a result (not part of the engine): `python3 -I -B check.py core` on a package built like this one.

## Results
- Controls: 39/44 of #7620's shape instances rebuilt (89%); 39/46 counting the 2 courier stops. 258@829 and 464@526 match SYLforge exactly.
- #7621 → data/word.json.gz (hit_loan_14): 14 instances, κ ×1.00025679. Every check passes (`check.py core`, `controls`, `columns1`, `columns2` in this package).
- A second round on hit_loan_14 with an extended template variant (not shipped) landed 0. That round added compact snapshots that start only when the source is about to change, side-A write-after-read (r += q·s moved to A or B), and extra unknown settles at B for spread contamination. `tpl.py` here is the version that reproduces hit_loan_14 exactly.

## Remaining blockers on hit_loan_14 (85-place census)
| reason | count | meaning |
|---|---|---|
| nosol | 20 | contamination reaches registers that never meet r at B |
| no label | 17 | owned peak 50 is full over the snapshot interval |
| no carrier | 17 | no register runs A→X→B |
| A window | 15 | the carrier leaves A before r or p arrive |
| slides | 10 | a slide partner is touched in between |
| write after read | 2 | side-A write-after-read (r += q·s) |
| read before p at X | 2 | with no solution; r is read before p arrives at X |

## Next levers
- A second carrier, so a contaminated register can be settled where it meets a register holding ρ rather than r.
- Shared snapshots, or a reorder of busy owned lifetimes, to free peak-50 events.
- Carriers that are not consecutive (A→…→X→…→B) with in-transit settles.
- Census shapes with several sources or readers.
