# Paired-cube bit word with partner-pair source mixing

This package is a bit-side analog of PR #144's paired-cube decoder, for integration on upstream main
`d1d6c07`. #144 is merged there. Standard library only; run every script without `-O`.

| p | h | v | R | R/v | loss h(h-2) | deficit 2v-3l | W=2v+R | gauges | coarse a0 (cert) | effective a_b |
|---|---|---|---|---|---|---|---|---|---|---|
| 11 | 22 | 1320 | 18964 | 14.37 | 440 | 1320 | 21604 | 4290 | 5502556/10^10 | 5.4974380e-4 |
| **12** | **24** | **1760** | **20052** | **11.39** | **528** | **1936** | **23572** | **3960 (dim 20, 21)** | **6391212/10^10** | **6.3852054e-4** |
| 13 | 26 | 2288 | 33514 | 14.65 | 624 | 2704 | 38090 | 7436 | 5541517/10^10 | 5.5363601e-4 |

At p = 12 the word uses the annealed pair module `data/pair_module_p12.json` and the nested-prefix all-but-one
module (`nested_prefix` in the generator) and the L1 local-channel association (`local_l1`), and merges its
face-1/edge-01 and face-2/edge-02 outputs (variant u);
p = 11 and p = 13 keep the witness-cut modules, #144's balanced tree and single reads. In the repository tree the
p = 12 word runs a physical layer (`scripts/paired_cube_bit_physical.py`, frozen word in
`references/paired-cube/bit-physical`): late copies and late-read reuse raise its coarse saving to 6549403/10^10.

The accounting is PR #144's bit ledger:

- `m = 3h` and `W = 2v + R`;
- three copies of the local, source-data and target-data children;
- an exterior child of width `3 dim sigma` per gauge;
- `2v` finishing children of width 2;
- full `32 m^2` fallback.

The effective saving is `(1 - 1e-3) a0 + 1e-3 * 384599/1e10`. For comparison:

- PR #144's bit supplier has coarse `4617656/10^10`.
- The h=21 Fibonacci-strip bit word (PR I) has coarse `5201637/10^10`.

So p=12 is +7.0% over the h=21 word and +20.5% over #144's bit supplier.

## What the construction is

The word is a mod-2 decoder on transversal triples:

    x_T = sum_{c in T} star(c) + sum_{|S cap T|=1} x_S.

- **Ports and centres.** Coordinates are grouped into pairs, and ports are triples with one coordinate from
  each of three pairs; `p = 12` gives `v = 8*C(12,3)`. The point stars over Q have span `h - 2`, so the
  centre loss is `h(h - 2)`.
- **Side channels.** Disjoint cubes contribute nothing mod 2, so there is no disjoint-triple module. The
  face channels are #144's pair modules, with the matching selector. The edge channels are #144's
  all-but-one modules on `E00 + E11` and `E01 + E10`.
- **Within a cube.** Two of the three within-cube terms come from partner-pair sums mixed on the SOURCE
  registers (`LEMMA.md`). The partner term is a single-source root.
- **Compile.** The PR #144 ledger on rational frames, with these choices:
  - target cap `ker(3 chi_T - 1)`;
  - coordinate-padded maximum matching, with frozen arcs;
  - plain frames `span(n)` for additions of span dimension at most 8, the bit compiler's lifted-set rule;
  - PR #144 chronological gauges with a G-nondegenerate sigma.

## Run

    python3 paired_cube_bit_word.py --p 12            # regenerate out/*_p12.json (about 50 s)
    python3 paired_cube_bit_word.py --p 12 --check    # byte-identical regeneration of all p=12 outputs
    python3 check_paired_cube_bit.py --dir out --p 12 # independent checker + 5 mutation controls (about 20 s)
    python3 moment_certificate.py out/profile_p12.json --tree REPO --output out/certificate_p12.json
    python3 derive_pair_modules.py --witness data/source_witness_21.json.gz --tree REPO --check   # module pins

Replace 12 with 11 or 13 for the variants (their outputs are not packaged; p = 12 is certified).

## Status (PROVEN / COMPUTED / CONJECTURED)

**PROVEN, written:** `LEMMA.md`, the partner-pair mixing step. It covers the frames, the sequential order
with no cross-talk, and why a full #144-type involution is impossible on the bit side.

**COMPUTED, checked by `check_paired_cube_bit.py` with exact integer arithmetic:**

- The 19,973 exported frames.
- The decoder identity, including the stars and `sum_{|S cap T|=1}` terms.
- Root, centre and source geometry.
- Every role chain nested, and every target chain nested.
- Phase one equals the centre closure, and the gauge target sets equal the response supports.
- The partner-pair chronology.
- G-nondegeneracy.
- A literal F2 replay with arbitrary dirty scratch.
- An independent recount that equals the saved child histogram.
- All controls rejected.

**COMPUTED, exact rationals:** the moment certificate. The grid point passes and its successor is rejected.

**Inherited, not re-checked here:**

- the three-stage cover and completed-core sharing on the bit side (#130/#144 notes);
- the bit stage geometry per triple port (any triple has H0-norm 1);
- the weighted local-ring compile and fallback;
- the semantic assembly;
- the analytic and tape interfaces.

PR97/Swapnil's checkers assume all `C(h,3)` triples and single-target outputs, so they do not apply to
this subset-port, broadcast-root word. `check_paired_cube_bit.py` replaces them.

## Credits

- Paired-cube decoder, modules and ledger: icekylinx PR #144, with OpenAI GPT-6 Astra and Codex assistance.
- PR117 DAG: eumemic, with Claude assistance.
- Bit-side compile conventions (deferred readouts, plain or lifted frames): Swapnil Jain / Zhihao Chen
  PR97, and the h=21 bit compiler (eumemic, with Anthropic Claude assistance).
- p=11 and p=12 pair modules: cut from an h=21 Fibonacci-strip witness (eumemic, with Anthropic Claude
  assistance), which descends from
  ikeboy PR62's interval strips.
- Completed-core sharing: an664 PR128.
- The bit analog, partner-pair mixing, rational compiler and checker: eumemic, with Anthropic Claude assistance.
