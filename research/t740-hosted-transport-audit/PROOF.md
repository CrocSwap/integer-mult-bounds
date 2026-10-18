# Independent certification of the hosted transport premise

Fix the eight canonical live inputs in SOURCES.json. They specify the base
fill, ten-copy lift, 145-row exchange journal, global order, dispatch, provider
widths, plan, template and 112 port recipes. The scope is the same literal
T740 completed-call projection as PR3309 at
`94d97babee3fdb68c6f84f3013949841eec7061c`.

For each hosted row, let t be its global call time, o its destination owner,
j its child and r its physical stream. Hosting occurs before the caller's
data events at t. Let k count the times of o's local stages strictly before
t. The first subsequent local block starts at the template event s_k. A
same-time hosted event therefore has cut k before that local event.

Let e_j be j's residual insertion. Scan the stream-touching events backwards
from e_j and let b_j be the last prior event that shears into or out of r,
or permutes r. If no such event exists, set b_j=-1. A sufficient condition is

```text
b_j < s_k <= e_j.
```

This is derived with a reverse last-touch scan. It differs from the
predecessor's forward test of every proposed child/cut interval. Local shears
touch both of their rows; paired bridges touch both X and both Y rows.
Permutations touch all rows in this fixed terminal event. Diagonal phases
commute with one another. For a shear I+cE_ds, a diagonal phase on a row
outside both d and s commutes with the shear. The condition therefore moves
each hosted phase forward to its own residual site. It does not assume a
phase on a read-only shear source is transportable.

The independent checker reconstructs all ten copies directly from base rows.
Every journal entry must have the exact lifted preimage and preserve its
call/helper identity. The source hashes fix every base row and edit. This
proves complete row coverage without relying on the predecessor's expanded
payload digest. The actual caller's dispatch supplies its helper width.
Each slice is in range, touches the plan's residual physical stream and
satisfies the reverse-barrier condition. Integer occupancy masks reject
overlaps; a final mask m satisfies m&(m+1)=0, so its occupied coordinates
are exactly a compact prefix. Residual axes are the complementary suffix.
All 82,880 owner/port contexts are visited.

Thus every original full axis appears exactly once across its disjoint
hosted slices and residual complement. After transporting the slices, their
product is the original full-child phase. The translation and the formal
residual multiplier remain at the original insertion. Other hosted diagonal
phases commute with this transport. Calls belonging to other owners have no
data events on these context streams in the inherited projection.

The new checker compares all nine transport fields to PR3309's unchanged
receipt: owners, ports, contexts, hosted-row count, journal count, per-context
row range, allowed cuts, full cut histogram and residual profiles. The
observed rows per context range from 28 to 45. This is a source-premise
certificate, not a numerical sample of phase values. Authentication of the
retained proof is distinct from proof admission.

PR3309's full-child algebra and PR3297's inverse are not replayed. Conditional
on those written results and the inherited completed-call model, the newly
checked premise supports the all-context normalization and residual-rank
consequence already claimed by those predecessors. It supplies no new native
implementation, cost bound, supplier admission or kappa.

The five control groups include a source-stream barrier, same-time versus
later chronology, wrong-stream plan, occupancy overlap, corrupt journal,
manifest schema/usage/inventory changes and a real private verifier process.
Controls supplement the written commutation argument. They are not an
independent human or proof-kernel review.

## Open next questions

The normal form for all 112 ports and rational inverse remain separate
verification obligations. A changed contract must state the altered word,
arbitrary-dirt endpoint and full invoice; this fixed-source certificate does
not classify it. Predecessor attribution and scope are retained in README.md.
