# Rounded residues and the hidden QQ16 input

This extends commdata2338's exact 66-port counterexample
[PR2384](https://github.com/CrocSwap/integer-mult-bounds/pull/2384) to arbitrary
nonlinear rounded observations and decoders under an explicit finite-capacity
contract. Subexponential transcript capacity cannot reconstruct its bounded
dyadic hidden line, even to one input ulp. This does not certify an actual
rounded controller's error bound or reject a changed observation contract.

For a fixed owner/payload domain of size W, the overgranted tuple below has
m=39888W real components. Suppose each component lies on the (p+g)-bit
fractional grid, within R(p)*2^-p of its ideal value, and all other retained
metadata has at most D_p states. Then its capacity is at most

    C_p = D_p * (2 floor(R(p) 2^g) + 1)^m.

Exact recovery requires C_p >= 2^(p-1)+1. Recovery with worst-case absolute
error at most2^-p requires C_p >= 2^(p-3)+1 for p>=3. Fixed W, polynomial R,
g=O(log p), and log2(D_p)=o(p) therefore fail eventually. There is no claimed
useful small-p threshold: W can be enormous. For growing depth/count use the
exact capacity inequality in [PROOF.md](PROOF.md), not the fixed-W corollary.

## Complete declared observation boundary

Fix the retained19-event QQ16 logical schedule, A/T/U partition, four X/Y pair
banks, and PR2384's66ordinary read ports S. At every owner/payload point grant:

| Observations | Complex scalar slots |
| --- | ---: |
| Initial X/Y values on S, all four pairs | 528 |
| All A/T and S values after each of19events | 19*(128+528)=12464 |
| Completed-X ordinary descendants after events1 through18 | 18*384=6912 |
| Five eight-component forward query histories | 40 |
| Total | 19944 |

Indices are zero-based: event0 is F0, event1 is B1. At the terminal rotation,
completed X is the new Y side. Former-Y final X is not granted. Repeated reads
of a stored value and deterministic postprocessing add no information. We count
both real and imaginary components despite the hidden family being real.

This is a complete *defined* contract, not every internal primitive of an
unspecified native implementation. Any additional retained intermediate value,
branch identifier, timing information or precision-dependent control record
must appear among the m components or D_p states. Extra source reads and early
original-A records change the contract. PR2540/PR2651's early records are an
explicit escape, not targets of this result.

## Source binding and validation

The predecessor at b9ef408b1cb0fcd34ab1f1bdbe645573d5de188f is retained
byte-for-byte in vendor/pr2384 with its notice. Its verifier authenticates six
main inputs and two archive members, proves all-owner routes and the19-event
zero transcript, and rejects eight controls. We replay its complete receipt
before deriving the integral hidden line and observation ledger; the wrapper
only redirects its source root to this checkout.

The line is v=2w for that exact witness. Its nonzero ordinary fields have
coefficients {-2,-2,-2,+2} on ports{44,49,58,70}. Its original selected fields
also have integral coefficients and coefficient L1 norm at most2. Original
A0(identity)=1. Thus x_k=k*2^-p*v, 0<=k<=2^(p-1), is a unit-box p-grid family
with zero exact observations and distinct demanded coordinate k*2^-p. The
fields are constant in payload addresses at any fixed finite depth.

New finite checks cover normalization, the complete slot ledger, one-ulp
packing, a sharp nine-transcript toy boundary, exact grid-interval counts,
and two deliberate escapes: finer output precision and extra side metadata.
The written pigeonhole proof establishes the universal result; finite controls
do not replace that proof or sample away the all-owner source identities.

Run Python3.12+, standard library only:

```sh
python3 -I -O -B research/qq16-rounded-transcript-capacity/verify.py
python3 scripts/research_package.py --package research/qq16-rounded-transcript-capacity
```

Replay is read-only, works in a Git-free dependency export, and compares the
complete typed receipt. --write creates a new receipt exclusively.
[VALIDATION.md](VALIDATION.md) records actual commands and outcomes.

## Scope and family decision

This closes only the bounded-precision nonlinear escape under the specified
error, quantization, observation and metadata hypotheses. Larger error, finer
outputs, exponentially many metadata states, a growing observation count,
extra reads or a changed consumer can escape. No native error theorem, physical
cost floor, supplier admission, new kappa or multiplication impossibility follows.

Revision5 decision: finish this precision audit and stop. The complete boundary
is the tuple plus metadata above. Proved quantities are information capacity and
the source line; the scalar count upper-bounds observation storage. Native work,
hosting, restoration and actual rounded errors remain unknown, not zero costs.
The consumer must change the boundary or meet its capacity requirement. This
does not expand the newer early-record construction.

Base1884c509, priority5, picker93caa43d0e7c6f6fdbd0977d213fdccc. The baseline
binding command passed before this refinement of uniform-transfer-audit.
SOURCES.json/TASK.json retain exact provenance, overlap coverage and limitations.

Credit commdata2338(PR2384), kyzer1023(PR2354), adamgall(PR2093),
AliRomman(PR1969), and the retained joint-query/QQ16 authors. Prepared by ywz65
with substantial OpenAI Codex assistance in proof, code and writing.
Apache-2.0; retained notices remain intact.

## Open next questions

Can a specific rounded controller prove a uniform observation error and count
all metadata at its actual coupled depth/precision? Inventory the emitted
boundary and bound each component error, then evaluate the exact capacity
criterion. Until then this is a conditional audit, not rejection of that
controller. No further exact-linear coefficient census is proposed here.
