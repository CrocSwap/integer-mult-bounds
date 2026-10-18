# FANIN4 in an aligned coefficient stream

**A local reversible-stream construction. No new kappa or supplier admission is claimed.**

## Result

For four read-only source vectors and one arbitrary dirty target in the common
coefficient frame of F2[C2^2], the update

    z <- z XOR x0 XOR x1 XOR x2 XOR x3

can be performed in one synchronized scan. Each coefficient still pays all
four XORs. Compared with four complete singleton updates, the fused scan
reduces reads, writes, target-head returns, and call-record overhead. It uses
no scratch and leaves each source and the target head at its entry position.

The claim is deliberately local. The sources use identity maps and are already
aligned in the same coefficient order. This does not construct the full
63-mask connector, map FANIN4 into the selected supplier, or change kappa. It
does show a concrete physical stream realization for a higher-arity connector
step while retaining the full per-source addition charge from Cycle 43.

## Exact bill

For s sources and L aligned coefficients, each singleton pass reads its source
and the current target, writes the target, and returns both heads. The fused
pass reads all s sources and the target once, writes the target once, and
returns all s+1 heads.

| Resource | s singleton updates | One FANIN-s | At s=4, L=4 |
|---|---:|---:|---:|
| Data reads | 2sL | (s+1)L | 32 vs 20 |
| Data writes | sL | L | 16 vs 4 |
| Bit XORs | sL | sL | 16 vs 16 |
| Forward plus return head moves | 4sL | 2(s+1)L | 64 vs 40 |
| Call records | s | 1 | 4 vs 1 |
| Source-reference fields | s | s | 4 vs 4 |
| Target-reference fields | s | 1 | 4 vs 1 |
| Scratch cells / cleanup | 0 | 0 | 0 vs 0 |
| Frame transitions | 0 | 0 | 0 vs 0 |

If read, write, head-step, uniform per-record, and target-reference prices are
r, w, h, d, and t, respectively, the fused bill saves exactly

    (s-1) * (L*r + L*w + 2*L*h + d + t).

The source-reference fields and sL arithmetic XORs are fully charged and
unchanged. A variable-width encoding can use separate record prices d1 for a
singleton and ds for FANIN-s; its exact saving is

    (s-1)*L*(r+w+2*h) + s*d1 - ds + (s-1)*t.

Thus a differently sized fused record is charged explicitly. Any frame
conversion cost F is subtracted from this saving; it is zero only in the
fixed aligned-frame instance studied here.

## Exact interface and proof

The object is the coefficient vector space of F2[C2^2], with L=4. Every
source xj and target z is an arbitrary 4-bit vector. Source maps are identity.
All five tapes begin at lane 0 in the same basis order.

At each lane i, the fused schedule reads the four source bits and z[i], applies
four binary XOR gates to z[i], writes the updated target bit, and advances all
five heads by one lane. At the end it returns all heads by four lanes.
Therefore each lane of the target becomes

    z[i] XOR x0[i] XOR x1[i] XOR x2[i] XOR x3[i].

Sources are never written. The target is arbitrary and dirty. The map is its
own inverse because each source bit is unchanged and adding the same sum twice
over F2 restores z. The symbolic argument holds for every L; the exact verifier
exhausts every dirty state at L=4.

Four singleton calls apply the same four XORs in four scans. Their source and
target heads return after each call. The resource counts in the table follow
directly from these two schedules; the verifier checks both ledgers and the
complete state map.

## Reproduce

From the repository root:

    python3 -B research/fanin4-aligned-source-stream-seed9983a614/verify.py
    python3 scripts/research_package.py --package research/fanin4-aligned-source-stream-seed9983a614 --check-only

Expected verifier line:

    PASS_FANIN4_STREAM states=1048576 L=4 xor=16/16 reads=32/20 writes=16/4 head_moves=64/40 records=4/1 unit_saving=54 controls=6

The registered command is the package verifier. Only the standard library is
used.

## Predecessors and limits

- PR #2128 adds the two-source DUO connector word and notes that a real
  supplier-level physical realization was still missing.
- Cycle 43 PR #2249 proposes a query/addition floor for the six-source
  arity-4..6 abstract connector. Its intermediate source-call lower bound
  is under correction for schedules with more than two readouts; this local
  stream construction does not use that floor. This construction keeps the full tap price;
  it concerns the lower-level stream bill.
- PRs #2171 and #2207 implement ordered single-source controlled streams and
  fallback descriptors. This package studies one aligned common-target fan-in,
  not their selected rank-42 normalizer.

No full batch path is supplied. The 63-mask recursive interface, invocation
placement, source-frame alignment in a live provider, head-motion pricing in
that provider, and any effect on the selected exponent remain open.

## Open next questions

Can two or more source operators from an emitted multiplication-supplier frame
be put in this aligned common-target layout without spending the saved traffic
on source-frame conversion? It matters because this package assumes identity
source maps in one fixed frame. A feasible first step is to name one live
supplier's source/target roles and derive its exact entry and return permutation
bill for one FANIN4 call. The blocker is that no such supplier mapping is
established here.

## Credit

The source-call connector model and DUO comparison are due to the authors of
PR #2128; the proposed abstract six-source high-arity floor is recorded in PR #2249
and remains separate from this proof.
This package supplies the local fused scan and its complete stream bill.
Prepared by Cinna Davis with substantial OpenAI Codex assistance. New work is
Apache-2.0.
