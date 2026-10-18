# Cross-fed connector handoff: correct endpoint, failed parity pilot

**Scoped obstruction, not a new supplier or exponent.** A three-row typed
handoff really replaces four complete B calls by three, but the explicit
`B=J_n` parity implementation is **3n−2 scalar XORs more expensive** than a
closed-call comparator that retains its own source parity. This holds for every
n≥1. The apparent n−2 saving against four separately lowered B calls is not a
saving against that legal comparator. This is an obstruction to this precise
candidate/lowering, not to all cross-fed handoffs or all parity circuits.

## Boundary and exact arbitrary-dirty endpoint

Let x,y,z be distinct arbitrary n-bit rows over F2. Fixed linear maps A,B,C
need not be invertible or commute. The requested sequential calls are

    y1 = y0 + A B x0,
    x1 = x0 + C B y1,
    z1 = z0.

Call one delivers y1 and restores x0 before call two uses y1 as its source and
x0 as its target. External observation is permitted only at call boundaries;
complete internal calls may temporarily borrow a source and must restore it.
There are no extra full rows. Each elementary scalar gate can use one clean
scalar temporary, restored per gate, with common admission charged separately.

The closed type has z=z0. The first open type has x=x0, y=y1,
z=z0+B x0. The second open type has x=x0, y=y1, z=z0+B y1.
The following chronological word implements the handoff:

    y += A z; z += B x; y += A z;
    x += y;   z += B x; x += y;
    x += C z; z += B y; x += C z.

After the first line y=y1 and z=z0+B x0. The second line temporarily makes
x=x0+y1, adds B(x0+y1), and restores x=x0, so z=z0+B y1.
Only then is the second echo run. Its two C reads cancel C z0 and its B read
restores z. Thus the final map is

    x = x0 + C B y0 + C B A B x0,
    y = y0 + A B x0,
    z = z0.

This calculation is in the free noncommutative module; it makes no clean-z
assumption and does not exchange AB with BA. Reversing the literal shear word
is its inverse. The explicit verifier checks this symbolic identity and both
orientations for all 4,096 triples of 2×2 maps on all six dirty basis columns.
Linearity then covers all 64 incoming states for each map triple.

The middle step is the familiar paid mixed-source query, credited to
Arham Tahir's PR1340/1370. The distinct issue here is its cross-fed boundary:
the readout changes the next source and the next output aliases the old source.
The generic identity by itself is not claimed as a new algebraic mechanism.

## Why the concrete apparent saving fails

With complete, orientation-independent fixed-port macro prices the eager bill is

    I + 4 cB + 2 cA + 2 cC,

and the carried bill is

    I' + 3 cB + 2 cA + 2 cC + 2 cX.

Here cX includes the entire n-coordinate source shear and its source/target
access; it is paid twice. The difference is favorable only if
`cB > 2 cX + I'−I`. Port-dependent prices require actual per-call sums instead.
Admission, storage, control, head returns, coefficient access, frames and
hosting cannot be omitted from these complete prices. No recurrence follows
from this conditional accounting identity.

For a concrete fixed map choose B=J_n (every entry one). A complete B query can
be implemented without a clean full row by:

1. XOR source coordinates 1..n−1 into source coordinate 0: n−1 gates.
2. XOR that parity into each z coordinate: n gates.
3. Undo step 1: n−1 gates.

Thus cB=3n−2 and cX=n in the unit scalar-gate tariff. Four independent B
lowerings cost 12n−8; the candidate costs 11n−6. That suggests n−2 saved gates
when n≥3. But the eager **closed** echo has a cheaper legal lowering:

    output += R z;
    prepare source parity;
    scatter parity to z;
    output += R z;
    scatter parity to z;
    unprepare source parity.

The source is distinct from the output within each call, so both R reads leave
the prepared parity intact. Source and connector are restored at the delivery
boundary. Its B-related bill is 4n−2, not 6n−4. Using this in each of the two
cross-fed calls gives 8n−4. Therefore, writing R=2cA+2cC,

| Exactly specified program | Complete scalar XOR count |
|---|---:|
| Eager four individually restored B queries | 12n−8+R |
| Proposed three-query handoff, both source shears paid | 11n−6+R |
| Two closed echoes retaining parity within each call | 8n−4+R |

The candidate loses to the last row by **3n−2>0**. The comparator is a concrete
legal word, not an asserted optimal circuit. An even better comparator would
only strengthen the obstruction. Alternative fusion inside the carried word
is outside this exclusion and must be priced anew.

For the n=4 fixture, A=I+E01 and C=I+E10 each have five entries, and neither
commutes with J4. The exact scalar bills are **60 / 58 / 48**, respectively.
The full nine-bit and twelve-bit words are not inferred from these formulas:
the verifier executes all dirty inputs for n=1..4, all three words, and all
three reverse words (4,680 input assignments).

## Explicit tape and instruction bill

The data addresses are x=1..n, y=n+1..2n, z=2n+1..3n. Each scalar XOR visits
source s, target t, source s, then origin. A clean scalar temporary is XORed
with the source at the first and last visits. A gate therefore costs exactly
`2s + 2|s−t|` unit head moves, three data reads, one write, three scalar XORs
(including temporary preparation/restoration), and one fixed-width instruction
dispatch. Its unit tariff is `2s + 2|s−t| + 8`, plus a common once-only temporary
admission/release cost. All maps and instruction lists are fixed compiled
constants; no runtime matrix product or free coefficient generation is used.

The verifier emits each separate resource count for all three programs and
n=1..4. This is a declared deterministic tape model, not a native wall-time
measurement. The per-gate origin returns avoid hidden boundary head debt.
No bound is claimed for arbitrary port-dependent prices or for other tape
lowerings. The scalar obstruction alone suffices to reject this pilot's claimed
scalar improvement; it is not a universal hardware dominance statement.

At n=4 the emitted tape totals, excluding the same admission constant, are
**1804 / 1764 / 1540** for eager / carried / parity-retained closed, respectively.
Their head-movement counts are **1324 / 1300 / 1156**. The concrete tape fixture
therefore also favors the strengthened closed comparator.

The verifier independently walks the literal four-visit path for every input
of every n=1..4 forward scalar program, checking both the resulting tape and
the complete head-movement sum. In particular source 3, target 1 visits
`0→3→1→3→0` and costs ten moves, not six. This backward-visit control catches
the erroneous shortcut `2 max(s,t)` used in an earlier unpublished draft.
All gates restore the scalar temporary and return the head to zero.

## Reproduce and evidence scope

From the repository root, Python 3.12 standard library:

```sh
python3.12 -I -O -B research/cross-fed-connector-handoff/verify.py
python3.12 scripts/research_package.py --package research/cross-fed-connector-handoff
```

The output status is `PASS_CROSS_FED_HANDOFF_OBSTRUCTION`. Four controls reject
omitting the connector patch, omitting the source-shear undo, moving the second
read before the patch, and closing on the wrong source. Their exact matrices,
input, incorrect output and expected output are printed for reproduction.
`SOURCES.json` pins the retained source bytes; no predecessor executable is
imported. The written n-universal proof is not proof-assistant formalization.
No selected full cold replay, hosted caller, physical supplier admission,
recursive profile, precision transfer, contraction or new κ is supplied.

Local validation uses macOS arm64 and CPython 3.12.12, through `uv run
--python 3.12 --no-project` for the registered replay and optimized direct
command. The registered runner checks the package metadata and source pins.
The final publication replay includes the literal tape checker and corrected
backward-return tariff; earlier unpublished tape numbers are superseded.

## Scope, overlap and credit

Base: `0b1cccf86e2f5132ed286a26ef0a681a495740ea`; selected record unchanged.
The local task card preceded computation. Parent advisory claim:
<https://github.com/CrocSwap/integer-mult-bounds/discussions/1884>.
The final 2026-10-14 overlap snapshot covered 541 open PRs at 13:20:07Z and
528 Discussion/comment/reply records at 13:21:27Z, both complete pagination.
The final exact cross-fed/source-handoff query returned only this local package
and the parent's advisory claim.
Exact searches included source handoff, source-switch, cross-fed, role rotation
and alternating source. No search establishes novelty; code diffs and arbitrary
nested files were outside helper coverage. Closest full PR bodies were read:

Before publication, targeted live queries rechecked PR1739, PR1780 and PR1524;
all remained open at the exact heads listed below. No full concurrent overlap
refresh was launched. The cached search cannot rule out subsequent work.

- woklerx PR1439, `3852c2d03044895cebdc9b31b0c7131a617774d2`: independent-u,
  same-source coherence adapter. This package's second source is its first output.
- Cinna Davis PR1739, `e33645b34521460bce61f9fb913f98f506d34d4d`: changed B and
  source update; importantly it also insists on a strengthened parity-retaining
  baseline. The present result applies that accounting discipline to cross-fed
  source-role switching; it does not claim to invent strengthened comparators.
- Ross Richardson PR1780, `15a91b5d634023a3a14129cbb240854c4b188111`: imposed
  source-update chronological optimum, not this aliased output/source contract.
- tennisbowling PR1524, `5c1f39788a0fc669b7e37e27785c63e85788c350`: offline
  independent-source uniform tariff. Its sources are not output aliases.
- Arham Tahir PR1370, `8a9b633879b5bfe03400a6c09c31bae7568e6261`, and PR1340,
  `f1dcab36fa63f8226f70dd07e26f44afb9d39b51`: the paid mixed-source query already
  used here. Its retained proof is a live pinned source, not a novelty claim.

Credit Ross Richardson's PR934/943 dirty connector lineage and Ali Romman's
frozen owner-catalogue boundary. This result neither contradicts that catalogue
nor duplicates the order-three/order-four dirty-frame discussions.
Prepared for Adam Gall with substantial OpenAI Codex assistance in derivation,
implementation, checking and prose. Apache-2.0; no independent human review.

## Open next questions

Can an actual hosted cross-fed caller beat a comparator that receives the same
permitted source/decoder fusion? This matters because a nominal removed B call
need not remove real work. First extract a caller's typed ports, allowed source
borrowing, complete map lowering and actual lifetime charges, then compare both
literal words before fitting a recurrence. The blocker is that no such caller
or tariff is provided here; the concrete J_n pilot fails the saving gate.
