# Compatibility of served controls, cascade frames, and butterfly reassociation

This is a conditional finite composition and an overlap audit. It retains the
completed-core, weighted compiler, restored-row, Clifford, analytic and fixed-tape
interfaces of its predecessors. It is not a proof of those all-size interfaces.
See NOTICE.md for source attribution and candidate.py for full commit pins.

## 1. Exact operation and role correspondence

Start with PR223's served word, freshly reproduced from PR200 by PR223's
patch.py. It deletes 373 pure-copy roles and their 373 initial copy operations.
All composite-node operations survive in their original sequence.

This supplies an unambiguous way to recover the compaction maps: align the
composite-node sequence, find the original control of each now-served operation,
delete precisely those control roles and their copy operations, then compact
the remaining indices in order. The verifier checks every resulting operation,
including its control marker and original operation frame. Each deleted role
must have exactly one initial source copy and one surviving served consumer.

Matching by node label alone would be insufficient: multiple source-copy
operations can have the same label. The verifier deliberately avoids that
ambiguity. The maps are used for every predecessor overlay index.

## 2. Cascade frames

All 6,191 entries of the PR211 frame witness retained by PR217 refer to
surviving operations. Apply their exact rational bases using the operation map.
One entry intersects a served operation. For that operation update both the
served frame declaration and its passive source-chain stop.
It is original operation 15154, compacted to 14781, serving passive source
1270. This is also one of PR217's overridden pair-frame locations; its
butterfly is among the blocked plans, so the cascade refinement survives here.

The emitted word is then read by a fresh instance of PR223's Candidate, so
aliases, read times, physical ports, and register chronology are reconstructed
from the actual changed program. Its exact geometry and ledger checks establish:

- the defining decoder and all abstract operand/root frame containments;
- containment of every changed operation's value span and nondegeneracy;
- nesting of every physical role chain, including all donor-recipient splices;
- the passive chain line -> mix -> served frame -> full;
- the actual target chronology and the complete telescoping rank deficit.

Refining these frames changes no scalar addition or value. All frame transition
costs are recomputed from the actual chains rather than subtracted as a headline
gain. Fresh cleared-Gram determinant witnesses cover every used frame, including
every passive-chain stop. Their checked factors retain the q > 2^80 range.

## 3. Which butterflies survive

PR217's butterfly replaces the two pairings (a,d), (b,c) by (a,c), (b,d),
then combines them. The total four-source value is unchanged over the integers,
and therefore over F2. The paired frame witnesses and every affected operand
are checked on the emitted graph.

Of the 440 frozen plans, exactly 67 have all four original auxiliary roles
available and their expected original controls. They have disjoint role sets
and are applied with the same bases and graph changes as PR217.

Each of the remaining 373 plans contains exactly one deleted served-control
role. These deleted roles exhaust the 373 deletions, one per blocked plan.
The plans' operation indices themselves survive; it is a required auxiliary
control role that no longer exists. Consequently these 373 frozen rewrites
cannot be pasted into PR223 unchanged.

This is a compatibility statement about these particular serialized plans.
It does not prove an upper bound or rule out a redesigned served butterfly.
In particular, adding PR217's full numerical gain to PR223's saving would not
be justified by these witnesses.

## 4. Finite physical replay and terminal sinks

The unsunk combined word is checked on all formal F2 columns. The original
34 terminal substitutions are then applied by PR223's served-aware terminal
compiler. All 20,261 columns of the resulting physical word are checked in
F2 and in both integer decoder directions, including arbitrary dirty registers,
source restoration, retained adjoint responses, and literal reverse cleanup.
The integer decoder is not asserted to be the identity; its F2 reduction is.

Seven additional adverse word/chronology controls include a one-leg butterfly
(only half the reassociation applied), a served read from a carrier, missing
compensation, a missing partner, a stale read, a missing passive stop and a late
served mix. The terminal compiler also requires its three existing controls
to fail. The prime coverage audit rejects a missing witness record.

No scalar gates are added by the frame overlay or the 67 reassociations.
The served word's conservative scalar bill and the terminal compiler's
nonpositive scalar delta remain available. Child ranks and their multiplicities
are freshly recounted from physical paths.

## 5. Packing and conditional arithmetic

The overlay preserves every gauge, alias pair, root-role ID, terminal selection
and source count. Therefore PR223's chart and completed-bank construction has
the same incidence and stock, but consumes the freshly recounted child profile.
These preserved interfaces are checked explicitly before invoking the inherited
packing code. The record identifies the emitted combined word by its canonical
SHA-256; it does not label the old served payload as the effective program.

There are 16,741 live physical auxiliary chains, 2,200 surviving rank-20 gauges,
and 34 removed terminal sinks. The unpacked stock is 20,261. Three copies give
packed stock W = 55,283, rank mass 3,974,568, and deficit 5,808 at m = 72.

The paid moment, including the inherited 10^-16 rare-class fallback, is
recomputed exactly. The ordinary seed pays its atom/adapter toll, three finite
ordinary levels are composed, and PR193's unchanged complex supplier feeds
the unchanged balanced assembly. The independent rational moment engine,
adjacent-grid exclusions, 47 strict constraints and seven final margins are
checked afresh. No floating-point root is used as a certificate.

## 6. Limits of the replay

This command replays the changed finite bit supplier, its prime/packing
interfaces and conditional arithmetic. It reproduces the served-word derivation,
but does not rerun every predecessor aggregate or the full complex supplier
proof. The complex proof/certificate and all-size contracts remain explicitly
pinned dependencies. It does not run the repository-wide make verify suite,
formalize the entire multiplication algorithm, or establish practical speedup.

Newer five-stage submissions existed when this experiment was prepared.
Its contribution is the compatibility result and independently replayable finite
composition, not a claim to the strongest current bound.
