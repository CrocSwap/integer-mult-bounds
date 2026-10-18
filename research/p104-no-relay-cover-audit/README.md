# P104 no-relay correction: exact access-cover minimum 4,580

The frozen P104 source/target frame paths require **at least 4,580 monotone
carrier lifetimes without relays** to supply `C = I - G/2`, under the explicit
model below. This strengthens Philippe Van Velzen's **4,480** lower bound and
independently validates its weighted-cover calculation.

The access-cover relaxation has minimum **exactly 4,580**: a 0/1 dual marks
4,580 required correction entries, and a matching primal uses 4,580 admissible
rectangles to cover all 4,992 entries. Each carrier covers at most one marked
entry. See [CERTIFICATE.json](CERTIFICATE.json) and [RESULT.json](RESULT.json).

This is a finite certificate and written scoped proof. **The upper certificate
is a support cover, not a scheduled 4,580-carrier circuit.** It ignores scalar
coefficient compatibility, availability within each read/write phase and dirty
restoration. No supplier, paid recursive profile, simultaneous-stock bound or
new κ is claimed. Evidence is author-checked, with two separately implemented
certificate replays; no independent human review or proof assistant is claimed.
The claim is in [Discussion #2245](https://github.com/CrocSwap/integer-mult-bounds/discussions/2245#discussioncomment-18942790).

## Delta and predecessors

Philippe Van Velzen's [correction screen](https://github.com/philippeVV/integer-mult-bounds/tree/7dfc7a176d7de4e7eabaf553a0b187c1bd647546/research/p104-correction-screen),
at `7dfc7a176d7de4e7eabaf553a0b187c1bd647546`, introduced the no-relay
frame-chain screen. Its 4,480 floor is the ceiling of `24831791/5544`. The
statement that one carrier covers at most 12 entries alone gives only
`ceil(4992/12)=416`; the stronger result uses nonuniform weights. We reproduce
its fraction and per-entry capacities, give the explicit program-to-cover
implication, and strengthen it with matching primal/dual certificates. This
refines its relaxation; it does not claim the predecessor's bound was false.

[PR #2353](https://github.com/CrocSwap/integer-mult-bounds/pull/2353), head
`2704eadf6b5205d4b965e9c6fc6dce28b89783cf`, independently audits the **208**
monotone-relay floor and explicitly excludes this no-relay calculation.
Its freely retimed relay theorem and this frozen-clock no-relay theorem have
different hypotheses. PRs #2251/#2345/#2358 concern pooled correction dimensions.
This account's PR #2172 prices cut-2429 nested exchanges and PR #2190 concerns
a fixed room's capture order. None supplies this access-cover optimum.

## Model and chronological premise

Keep the **unchanged order** of all 4,058 events in PR #1972's word, retained
by [PR #1991](https://github.com/CrocSwap/integer-mult-bounds/pull/1991).
There are 104 independent sources `X_s` and 104 targets `Y_t`. Frames are
subspaces of `F2^9`; equality and inclusion are independent of basis choice.
The correction network inserts operations between original events and may
not retime the original X/Y paths.

A carrier lifetime starts with source-independent contents, possibly arbitrary
dirty data. It may read original sources, perform input-independent rational
scalar linear operations on itself, and add its contents to targets, always
in an equal frame. It may follow any nested increasing frame chain, including
jumps and arbitrary intermediate frames. Transport preserves logical scalar
coefficients. Reinitializing a physical register starts a new lifetime.
There are no helper-to-helper value transfers, target reads, retained-channel
helper reads, source writes, source-dependent initialization, descending
transports or cross-frame source access. Targets receive additive writes only.
Dirty restoration is relaxed, which can only favor a proposed construction.

The exact frame replay checks that every X starts in a line and ends in the
full nine-dimensional frame, every Y starts at zero and ends at dimension
eight, the original word never writes X or reads Y, and:

```
last source transport: cut 1533
first target transport: cut 2526
```

A cut counts completed original events. A carrier reading a full-frame source
cannot later enter a target frame monotonically. A source-dependent carrier
cannot write at the zero frame: all source labels are nonzero and its initial
source projection is zero. Thus every useful source read precedes every useful
target write. Direct source-dependent X-to-Y writes are also unavailable on
the frozen clock.

The separation hypothesis matters. A checked two-dimensional boundary example
reads `x0` and writes `y0` in `<e1>`, climbs to `<e1,e2>`, then reads `x1` and
writes `y1`. One carrier produces triangular support
`{(y0,x0),(y1,x0),(y1,x1)}`. Its two diagonal entries cannot share a rectangle
in the separated-read/write model. This is not a P104 counterexample; it
shows why arbitrary retiming cannot silently be imported from the relay model.

## Carrier envelope and complete enumeration

Let `S(V)` be the source indices whose retained path visits frame V, and
`T(W)` the target indices whose path visits nonzero frame W. The source
contact frames of a carrier form a chain ending at V; its target contact
frames form a chain starting at W, with `V <= W`. Its matrix contribution
therefore has support inside

```
B x A, where A = union S(U) along a source chain ending at V,
             B = union T(Z) along a target chain starting at W, V <= W.
```

Granting all contacts at each visited frame is a favorable relaxation.
Intermediate frames without original contacts can be removed. Coefficients
need not be constant on a rectangle: only support containment is used.
Repeated writes, self-rescaling and cancellations cannot create source
dependence outside this envelope.

The primary checker computes all maximal source unions by

```
A(V) = maximal({S(V)} union {S(V) union a : U < V, a in A(U)}),
```

and target unions by the reversed recurrence. Dimension gives an acyclic
ordering. Induction covers every contact chain. Dropping contained unions is
safe because extension uses union; dropping contained rectangles preserves
nonnegative dual constraints and set-cover minimization.

The reconstruction gives 221 source frames, 220 nonzero target frames, 550
maximal source-chain unions, 549 maximal target-chain unions and 5,724 nested
frame pairs. Its 5,804 rectangles reduce to **4,638 maximal rectangles**.
The separate `independent.py` uses explicit sets and complete recursive chains,
without prefix dominance pruning or primary-checker imports. It generates
**6,942** rectangles and checks the same primal/dual on that larger family.

The doubled E8 coordinates and the fixture's 16 removed lines reconstruct C
in sorted port order. Its support has 48 entries per row, hence **4,992**.
The checker also binds this to the frozen frame labels: `C[t,s] != 0` iff
the initial source label lies in Y_t's endpoint. Every rectangle lies in
this support, and their union equals it. Native operator realization remains
inherited; the present checker does not re-prove it.

## Primal/dual proof

**4,368** entries occur only in singleton maximal rectangles. They contribute
one dual unit and one necessary cover each. The other **624** entries have
270 nonsingleton maximal rectangles. Their incidence graph splits into
24 three-entry and 24 twenty-three-entry components, with at most 14 choices
per component.

The certificate lists **212 additional marked entries** and **212 additional
rectangles**. Each replay checks directly that all 4,580 marked entries are
distinct support entries, every admissible rectangle contains at most one,
and the 4,580 selected rectangles cover all 4,992 required entries.

Every nonzero coefficient of C must have a nonzero contribution from at least
one carrier. Cancellation elsewhere cannot create a nonzero sum from zeros.
Each carrier covers at most one marked entry, proving the **4,580 lifetime
lower bound**. The matching cover proves the relaxation's upper bound.
The fractional cover optimum is also 4,580: its primal and 0/1 dual agree.
No solver or search-status report is trusted for acceptance.

`generate.py` deterministically proposes the certificate using exhaustive
subset cover and a separate maximum-independent-set search in each component.
The component optimum distribution is `{2:25, 4:4, 6:5, 8:12, 10:2}`.
The replays check the resulting inequalities without rerunning optimization.

## Reproduce and validation scope

Python 3.12, standard library only, from the repository root:

```sh
python3 -I -B research/p104-no-relay-cover-audit/verify.py
python3 -I -O -B research/p104-no-relay-cover-audit/independent.py
python3 scripts/research_package.py --package research/p104-no-relay-cover-audit --check-only
python3 scripts/research_package.py --package research/p104-no-relay-cover-audit
```

Expected primary success line:

```
PASS_P104_NO_RELAY_COVER_AUDIT pairs=4992 covers=4638 optimum=4580 previous_floor=4480 controls=12
```

The second replay reports `all_chain_rectangles=6942`, `primal=4580`,
`dual=4580` and two additional controls. Both default replays write nothing,
survive `-O`, and work in a Git-free export with the two pinned inputs.
The repository metadata check additionally needs Git provenance.
The registered hook also runs `test_verify.py`: five public-CLI tests cover
a read-only export, source/certificate/receipt corruption, deterministic
regeneration and refusing to overwrite an occupied output path.

Optional deterministic regeneration uses a fresh output path:

```sh
python3 -I -B research/p104-no-relay-cover-audit/generate.py --out /tmp/p104-cover-new.json
```

The output is byte-identical to `CERTIFICATE.json` in the recorded environment.
The primary `--out NEW.json` writes a fresh receipt exclusively; the ordinary
replay instead compares the recomputed receipt to `RESULT.json`.

Twelve primary controls cover transport rank, X overwrite, puncture drift,
duplicate/out-of-support/over-capacity dual entries, omitted/inadmissible
primal rectangles, wrong optimum, exhaustive tiny-poset comparison,
interleaved timing, and relay/source-preload boundaries. The second replay
independently checks a missing cover and overweight dual. Exact scientific
input hashes are authenticated before replay.

Unrun obligations: native phase recipes, all 280 scalar endpoint columns,
chronological coefficient realization, restoration, relay-enabled networks,
retained private descents, global owners/hosting, productive coverage pricing,
precision, all-size/compiler admission, selected cold replay and a complete
multiplication theorem. Neither 4,580 nor 212 is asserted to be a paid child count.

## Open next questions

The support relaxation is solved: reweighting it cannot beat 4,580. If a sharper
no-relay model is useful, test actual contact times or coefficient compatibility
on one twenty-three-entry component, starting from its minimum cover. This can
raise a necessary count, but the no-relay route was already unfavorable, so it
should not displace central relay or changed-interface work.

For a useful construction, allow explicitly priced relays or retained descending
values and derive a replacement envelope. Start with one target's acquisition,
dirty restoration and complete local bill; check the active Discussion #2245
handoffs first. This certificate does not impose 4,580 on those networks.
Structured questions and blockers are in [TASK.json](TASK.json).

## Credit and provenance

Philippe Van Velzen / `philippeVV` supplied the no-relay chain model, per-entry
capacity method and 4,480 floor at the exact fork head above. kumagi / #2353
supplied the separate relay audit and its explicit scope boundary. Rohan Arun /
#1972 supplies the frozen scalar/frame word at
`fd82d172f46933fd253c2c6de4bd5eaff5429cfd`; Chafik Boukhalfa / #1991 supplies
the native realization and retained inputs. Adam Gall / #1940, Josie Elliston /
#1071, Ali Romman / #1125 and the retained geometry/compiler lineage remain
credited. Gonzalo Mier / #2173, Gareth Davidson / #2251 and AAAmirinu /
#2345/#2358 own the separate pooled-space/prefix results.

Base: canonical main `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority
revision 4. [SOURCES.json](SOURCES.json) pins scientific inputs and catalogue
provenance. No predecessor executable is imported or modified.
[TASK.json](TASK.json) records assignment, scope refinement and overlap.

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.
OpenAI Codex performed the derivation, implementation, checking and writing.
New work is Apache-2.0; existing source notices remain unchanged.
