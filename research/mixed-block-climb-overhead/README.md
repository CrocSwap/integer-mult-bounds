# Mixed charged/free block profiles: the aggregate test is essential

This is a correction to one inference in Aaron Wang's AI-assisted
[PR3039](https://github.com/CrocSwap/integer-mult-bounds/pull/3039), at exact head
`f0d6a48245e44fc29cfe077d21ca2521c2a8d941`. Its isolated charged-group
calculation remains valid. It does not imply that every group in a passing
complete call must be free: profitable free groups can offset a few charged
ones. The source's broader wording appears in its README and PR description.
The exact README is retained unchanged in `sources/pr3039-README.md`.

**Cost-alphabet result only.** No block decoder, changed native child,
dirty-state realization, supplier admission or new kappa is constructed here.
Arham Tahir's [PR1605](https://github.com/CrocSwap/integer-mult-bounds/pull/1605)
already supplies the full-reblock overhead allowances. The new contribution is
the explicit mixed-group counterexample to PR3039's broader inference, and the
adjacent boundary in the small family below. This does not reopen PR679's
native direct-sum/tensor-child obstruction or Ali Romman's PR1429 fixed-block
theorem. Counting co-frame groups alone cannot supply a new child identity.

## Exact model and witness

Keep PR1605's width 73, stock `896/9`, old idle mass 1646 fractionally packed
at rank 51, and local profile

```text
H = {1:2412, 2:418, 3:432, 4:142, 5:82, 8:8}.
```

At `a = 35491136290869/20000000000000000`, put `c(r)=(r/73)^(1-a)` and

```text
F(P) = [sum_r P[r] c(r) + (1646/51)c(51)] / (896/9).
```

This is PR1605's primitive-saving screening target, 21/20 times the retained
upper bracket for the primitive ceiling. It is not a five-percent kappa claim.
Every added transport is paid on top; none receives old idle credit.

Partition all 2412 payload units into 150 free rank-16 groups, one free
rank-10 group, and one rank-2 group with one additional paid rank-2 transport.
The complete profile is

```text
P1 = H - 2412 H1 + 150 H16 + H10 + 2 H2
   = {2:420, 3:432, 4:142, 5:82, 8:8, 10:1, 16:150}.
```

Payload mass remains 2412; the one transport adds two units to the full local
mass, 5586 -> 5588. Nevertheless

```text
0.998883185907233 < F(P1) < 0.998883185907234 < 1.
```

That charged pair is individually dearer than its two original singleton
children: `2c(2)>2c(1)` since `1-a>0`. Its loss is offset elsewhere in the
call. This is a counterexample to the cost-alphabet implication that a passing
mixed profile must have no charged groups. It establishes no physical
realization of either the free groups or the charged pair.

## A sharp boundary within one seven-member family

For integers `0<=q<=6`, split the twelve-unit remainder of the full rank-16
partition into `q` rank-2 payloads and, if positive, one free remainder of
rank `12-2q`. Give each of the `q` pairs exactly one paid rank-2 transport:

```text
Pq = H - 2412 H1 + 150 H16 + 2q H2 + H(12-2q),
```

where `H0=0`. Its extra rank mass is exactly `2q`. The last two cases are

| q | Complete local profile | Extra mass | Exact moment enclosure |
|---|---|---:|---|
| 5 | `{2:429,3:432,4:142,5:82,8:8,16:150}` | 10 | `(0.999994967530944, 0.999994967530945)` |
| 6 | `{2:430,3:432,4:142,5:82,8:8,16:150}` | 12 | `(1.000271925593698, 1.000271925593699)` |

Thus five charged pairs pass and six fail in this family. This is not an
optimum over arbitrary partitions or physical programs.

For completeness, the family moment increases strictly with q for every
`0<a<1`. With `n=12-2q`, its increment before normalization is
`2c(2)+c(n-2)-c(n)`, setting `c(0)=0`. Subadditivity of the concave power
gives `c(n)<=c(n-2)+c(2)`, so the increment is at least `c(2)>0`.
The two strict boundary signs therefore settle the entire family. The
verifier also computes all seven profiles directly.

The correct aggregate criterion is

```text
F(H) - sum_groups [k c(1) - payload_cost(group)] / (896/9)
     + total_added_cost / (896/9) < 1.
```

If a hypothesis imposes the additional tariff on every nontrivial group, the
corresponding per-group exclusion can close that uniformly taxed construction.
An isolated loss cannot establish that hypothesis or exclude a mixed call.
PR1605's uniformly taxed family remains excluded on its original premises.

## Reproduce and coverage

From the repository root, Python 3.12 or later, standard library only:

```sh
python3.12 -I -B research/mixed-block-climb-overhead/verify.py
```

Expected: `PASS_MIXED_BLOCK_OVERHEAD charged_pairs=5 next=6_rejected no_new_kappa`.
`--write` regenerates only this package's `RESULT.json`. The checker executes
the authenticated unchanged PR1240 log/exp engine directly from source bytes;
it does not load its bytecode cache. It retains the full other-child and idle
bill, checks all seven profiles and exposes false passes caused by omitted
transports and illicit idle refunds. The unchanged baseline fails the target;
the mixed family still fails at `a=1/99`.

These are exact rational enclosures and a written concavity argument, with an
independent internal mathematical check recorded separately. They are not a
formal-kernel proof or independent human review. No selected cold replay,
physical/native/hosting/precision admission or hosted-CI success is implied.

## Open next questions

- Can an actual changed child/caller contract realize any mixed profile?
  First give the exact arbitrary-dirty-input operator, source access and
  restoration word, and price its helpers, adapters, buffers, owner remainders
  and native work. The direct-sum/tensor distinction and the absence of a
  physical construction remain blockers. This calculation supplies no reason
  to repeat a co-frame census without that contract.
- A proposed impossibility proof for mixed free/charged groups needs a global
  constraint forcing enough charged groups, rather than an isolated loss.
  First state that constraint for a named chronological word, then evaluate
  its complete moment. No such constraint is established here.

## Sources and credit

Scientific base `d8e0f83f00191df62174b641e9fff055c357f641`, priority revision 6.
`SOURCES.json` pins the selected-record context, original catalogue, three
live predecessor files and the unchanged PR3039 README. The source claim is
reviewed at that exact head, not all possible future revisions.

Credit: Aaron Wang with opencode assistance (PR3039's local transport screen);
Arham Tahir with OpenAI Codex assistance (PR1605's integer partitions, exact
target and overhead budget); Douglas Colkitt (PR1240's model and interval
engine); Ali Romman (PR1429's fixed-block contract); Greer Guthrie (PR679's
native batching obstruction); and the selected Rohan Arun/Jeremy Kothe/Hao Yan
and retained construction lineage credited in the predecessor packages.
Prepared by Ross Richardson with substantial OpenAI Codex assistance,
including an independent internal mathematical specialist. New work Apache-2.0;
the unchanged predecessor source retains its authorship and license.
