# Exact logical growth of the all-target P104 relay correction

Philippe Van Velzen's published [relay-v2 word](https://github.com/philippeVV/integer-mult-bounds/tree/fac9e821d31bc199b49e8ed463074a50d1264311/research/p104-correction-screen/relay-v2)
restores all 1,031 arbitrary dirty helpers and supplies every row of `C = I-G/2`.
This package independently checks that construction and adds exact intermediate
logical growth bounds for the correction and its logical inverse-transpose.
It does not propose a new correction or supplier.

## Result

The correction has 1,239 independent inputs: 104 source values, 104 target
values and 1,031 unrelated dirty helper values. All 1,535,121 endpoint
coefficients are checked in each direction, including zeros.

| Logical program | Endpoint | Maximum row l1 norm | Largest coefficient denominator |
| --- | --- | ---: | ---: |
| Correction `S` | `Y += C X`; X and helpers unchanged | 70 | 8 |
| Logical inverse-transpose `S^(-T)` | `X -= C^T Y`; Y and helpers unchanged | 56 | 8 |

These are attained maxima over every cut of the correction's literal word.
They cover 12,784 scalar gates and 4,840 logical-identity frame moves. If every
logical input coordinate has magnitude at most B, every intermediate coordinate
has magnitude at most 70B forward, or 56B in the stated dual program. Integer
logical inputs remain in `(1/8) Z` at every cut. These bounds describe exact
logical arithmetic. They do not bound rounding-error accumulation or the
intermediate values of the intervening 4,058-event channel.

Here the fixture stores doubled integer roots r_t, and
`G_ts = (r_t dot r_s)/4`. The checker reconstructs those roots and this Gram
matrix without using the relay producer's geometry dump.

The first norm witnesses are Y72 after event 4522 forward and helper 269 after
event 12605 in the dual. Events use the zero-based indices of `inputs/WORD.json`,
whose initialization is event 0. The first denominator-eight witnesses are
helper 35 after event 8115 and helper 671 after event 10213, respectively.
[EXPECTED.json](EXPECTED.json) records the complete receipt and register indices.

The independent transport recount agrees with the predecessor:

```text
2427 H1 + 1094 H2 + 998 H3 + 96 H4 + 66 H5 + 157 H6 + 2 H7
rank mass = 9279 = 9 * 1031
```

There are 726 immutable-source reads, 5,362 helper shears and 6,696 target writes.
All helpers start at ZERO and finish at FULL. Reads and target writes occur
only at the original channel's cuts 0 and 4058; binary Gaussian elimination
checks nested moves and common operand frames independently of the published
checker's explicit subspace enumeration.

The original fixed 832-family, nine-stage, m=73, COPY56 coverage model allows
6,712 total rank units per call. The channel uses 2,368, leaving 4,344; this
correction overfills that allowance by **4,935**. More directly, even omitting
all idle and additional costs, the complete local zero-saving moment is
`9 * (2368 + 9279) / (73 * 832) = 104823/60736 > 1`.
Each child cost increases with nonnegative saving, so this fixed-template word
cannot pass its recursive moment. This corroborates the predecessor's cost
warning. It does not close other relay designs or changed coverage/templates.

## Why the checks establish these claims

Each scalar gate updates one dense integer row divided by a power of two.
Common factors of two are removed after every operation. The checker compares
every endpoint coefficient with the independently reconstructed rational E8
Gram formula, rather than comparing with another generated relay endpoint.
Unchanged rows cannot create a new maximum, so checking each changed row and
the identity initialization covers every row at every cut. Minimal dyadic
exponents give the exact denominator bound.

For an ADD `M = I + c e_d e_s^T`, distinct operands imply
`M^(-T) = I - c e_s e_d^T`. If `S = M_n ... M_1`, then
`S^(-T) = M_n^(-T) ... M_1^(-T)`. The dual therefore uses the **same chronological
order**, swaps source and destination, and negates the coefficient. Its complete
endpoint is checked separately. Its physical frames are not supplied here.

Forward composition inherits PR1991's source-bound channel statement: X and its
72 dirty helpers restore, and Y gains `G X/2` for arbitrary initial Y. The relay's
cut-0 work leaves X unchanged and only adds dirty compensation to Y; the core
does not touch the relay helpers. Insert the core immediately before the first
cut-4058 contact. Its target addition commutes with the relay's additive writes,
so the completed logical forward endpoint is `Y += X`. The 70/56 bounds apply
only to the correction, with the core omitted from its arithmetic. No full
channel-plus-correction growth bound follows.

## Reproduce

Python 3.12, standard library only; no network, Git or predecessor executable
imports during direct replay. The ordinary command writes nothing.

```sh
python3.12 -I -O -Werror -B research/p104-relay-growth/verify.py
python3.12 -Werror -B scripts/research_package.py --package research/p104-relay-growth
```

`--out PATH` creates a new receipt and refuses to overwrite an existing file.
The registered replay includes eight behavioral test groups. They reject lost
dirty compensation, changed coefficients and lost cleanup in both directions;
invalid frames, source contacts, cuts, indices and event-cap exhaustion; dyadic
exponent and numerator capacity exhaustion; source
corruption, receipt drift and output overwrite. Equivalent binary bases pass.
Endpoint-preserving inserted shears raise the measured norm to 81 and the
denominator to 16, checking that the scanner detects intermediate growth.
An optimized Git-free export leaves all its input bytes unchanged.

Local verification used CPython 3.12.15 on macOS arm64, with warnings treated as
errors. Ruff 0.17.1 checks E/F/I/B/UP diagnostics at a 100-column limit. A separate
sparse Fraction implementation, importing no candidate executable, independently
matched both endpoints, all growth witnesses and the frame/profile recount;
it also replayed the inherited 280-input core endpoint. That corroborating script
was a local review probe, not an additional registered proof artifact. No human
or proof-assistant review is claimed.

The implementation uses no recursion. The fixed input caps are 17,625 events,
1,239 columns, nine binary dimensions, dyadic exponent 64 and numerator width
256 bits, all enforced on the accepted path. The Python runtime requires dynamic
integer and list allocation, a deviation from Power of Ten rule 3. Live row
storage is bounded by one 1,239-square matrix plus O(1,239) temporary entries;
forward and dual matrices do not coexist. Input hashes and capacity rejection
bound this deviation. Verification covers the literal word and event exhaustion;
a future extension must preserve or explicitly revise those capacities. CI runs
Python warning diagnostics on every registered replay; the external Ruff check
is recorded locally rather than added as a repository-wide dependency.

## Open next questions

- Can the cell-tree design reduce its actual recursive bill enough to fit a
  complete supplier? Start by reducing merge loss in the published shared
  pools, then rerun the exact endpoint and transport recount. The current word
  already fails the fixed-template local-only moment; native lowering alone
  cannot repair that cost gap.
- What are the combined channel-plus-correction physical growth and accumulated
  rounding-error bounds? Insert the retained channel at the named cut and
  derive the suffix error propagation, with native charts and the private-copy
  lifetimes included. Correction-only row growth and denominators do not supply
  that precision theorem. Hosting, scalar/address work and all-size admission
  are further obligations, even for a cheaper replacement.

Structured next questions, selection nonce, overlap freshness and exact sources
are in [TASK.json](TASK.json) and [SOURCES.json](SOURCES.json). This audit does not
verify the predecessor's search optimality, pool census, universal lifetime-floor
arguments or caps against pending PRs.

## Credit

Philippe Van Velzen supplies the complete cell-tree correction, literal word,
published checker and its cost warning. The byte-identical source word and
original README are retained under `inputs/`. The model follows Hiroki
Kumazaki's PR2353, commdata2338's PR2393 and Ross Richardson's PR2445.
Rohan Arun's PR1972 supplies the channel witness; Chafik Boukhalfa's PR1991
supplies its native binding. Adam Gall's PR1940 and Josie Elliston's PR1071,
Ali Romman's PR1125 and their retained geometry/decoder lineage remain credited.
The coverage model comes from the PR1012/local-word-ceiling lineage.

Independent dense arithmetic, exact growth bounds and this audit package:
Nick Petalas. Apache-2.0. Existing source notices remain unchanged.
