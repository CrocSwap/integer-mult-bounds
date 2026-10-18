# QQ16 numerical contracts, from relative error to bit circuits

Use this map before assigning another precision or arithmetic task for the
zero-retention QQ16 decoder. The [observation-contract map](qq16-controller-scope-map.md)
answers which records recover inputs. This page follows the different question
of implementing the recovered decoder with finite precision and accounting for
its arithmetic. It does not admit a supplier or change
[the selected result](../../certificates/selected-result.json).

The source checkpoint is main `d08a1e413c881ae3ff6a1a8b0c7d042b093517b6`,
priority revision 5, checked 2026-10-16. PR2707 and PR2736/2771/2807/2811 are
incorporated scoped research in the [round-1600](community-efficient1600-review.md)
and [round-1700](community-efficient1700-review.md) reviews. PR2876 is pending
at the head below. Its primary checker was replayed for this navigation audit;
that does not promote its evidence status. Check the
[canonical numerical thread](https://github.com/CrocSwap/integer-mult-bounds/discussions/2727)
and live overlap before taking a handoff.

## Fix the word, norm and units first

The word is [ywz65's PR2707](../../research/qq16-line-normalized-decoder/README.md),
following Arham Tahir's PR2681. It uses all 224 current X/Y fields, produces
224 owned original-array outputs in F17 and never writes the borrowed fields.
It retains no early value across B1. Its 3,823 events include 336 signed lines,
464 maps, 2,704 scalar ADDs and 312 CLEARs. The ideal native invoice counts
336 positive rank-one children and 672 wrappers. Negative signed lines use
positive children with output-XOR wrappers; the two counts describe different
parts of the implementation. Zero early retention still needs output and
scratch storage.

Throughout this page, `D=2^(h*lambda)` is the number of complex payload
coordinates **per owner**, `N` is the number of owners, and positive integers
`h,lambda` specify the factor width and tensor depth. The norm is the maximum, over owners, of the payload
Hilbert norm. `B>0` bounds the supplied post-B1 current fields in that norm.
This page uses `k` only for the line's precision reserve and `ell` for the
pair circuit's exponent-input width. The source papers use these letters
differently. These results concern the added decoder; inherited F0/B1 work
and its entry errors are separate.

## What each result supplies

| Source | Input premise and established output | Boundary of the result |
| --- | --- | --- |
| [PR2736, completed-error lemma](../../research/qq16-zero-retention-defects/PROOF.md) | On the actual operands, a completed ADD has destination defect at most `u*(norm(dst)+abs(c)*norm(src))`; a line or map has defect at most `u*norm(operand)`. For `0<=u<1/199144`, exact owned CLEARs and ideal line/map isometries give all-cut error at most `B*2919388*u/(1-199144*u)`. Choosing `u<=2^(-b-22)` gives strict error below `B*2^-b`, for integer `b>=0`. | Twenty-two is a sufficient relative-error guard for this majorant. It is neither component precision nor a minimum. Child interiors, wrapper/map implementation and the entry bound B are not supplied. |
| [PR2771, direct rounded lines](../../research/qq16-rounded-native-line/README.md) | For a common component grid step delta over one complete signed line, nearest-even pair arithmetic with exact wrappers has error at most `lambda*sqrt(D/2)*delta`. Scan the actual input block, put `e=floor(log2(max absolute component))`, and choose `delta=2^(e-k)` with `k=b+22+ceil_log2(lambda)+floor(h*lambda/2)`. Zero blocks return zero exactly. This supplies PR2736's line premise. | A fixed absolute grid alone does not imply that state-relative premise. This direct implementation initially uses unlimited exact dyadic arithmetic. It does not supply a cheap recursive child tariff or the other physical caller premises. |
| [PR2807, finite dyadic format](../../research/qq16-finite-dyadic-format/README.md) | Add an entry grid `2^-Q0 Z` and `B<=2^E`, with nonnegative integer `Q0,E`. The fixed word admits `Qmax=Q0+3*k+6` fractional bits and sufficient signed component width `W=Qmax+E+20`. Quarter ADDs, maps and CLEARs are exact; checked finite arithmetic simulates the unlimited reference without overflow. | These are sufficient bounds for this direct implementation, not precision minima. A norm bound alone does not bound arbitrarily small dyadic inputs. Native semantics and the error theorem are inherited; complete-word fixtures use substitute isometries. |
| [PR2811, pair circuits](../../research/qq16-rounded-pair-bit-circuit/PROOF.md) | For four signed w-bit components, set `L=w+2`, `ell=bit_length(L-2)`. Given a legal `0<=d<=L-2`, the exact nearest-even pair has `52*L-4*d+8` fixed-exponent gates or `24*L*ell+52*L+4*2^ell+4*ell+4` runtime-exponent gates. | The exponent is supplied. Its discovery and validity check are outside this circuit. AND/XOR/OR/NOT gates, free wires/constants/fan-out and irreversible evaluation define the model. These counts are not tape time, reversible cost or recursive rank. |
| [PR2876, common block-scale scan][scan] **pending** | For integers `q,w>=1` and fixed `0<=p<w`, read q signed w-bit components. Return `d=0` on a zero block, otherwise `d=max(0,floor(log2(max abs input))-p)`, plus zero and grid-admissibility flags. The scan costs `w*(4*q+2)-2*p+S(w-p)+3` gates, where `S(n)=sum(popcount(i),0<=i<n)`. Set `q=2*D`, `p=k`; compute d once before the complete owner-local line and share it across its pairs and factors. | The entry-grid/range invariant comes from PR2807. Choosing a separate scale per pair can change the operation. Exponent lifetime/cleanup, physical fan-out/workspace, scan travel and a complete consumer remain unpriced. |

The first three results compose under their stated exact-permutation, ownership
and entry premises. The last two provide a Boolean implementation and subtotal
for the signed-line arithmetic. They do not transfer the original rank-one
recursive price to direct pair loops. Their scalar allowances, gate counts
and physical movement costs have different units and cannot be added without
an explicit caller model.

## One common example and its incomplete bill

For `h=73`, `lambda=1`, `b=64`, `Q0=64`, `E=0`, PR2807 gives
`k=122`, `Qmax=436`, `W=456`. Its stronger within-line component bound allows
`w=W-3=453`, `L=455`, `ell=9` in PR2811. The resulting runtime pair circuit
has 124,028 gates. This count does not cover arbitrary 456-bit pair operands.

In the pending PR2876 model, one scan per line per owner costs
`3624*D+1984` gates. There are at most `lambda*D/2` pair evaluations per
line per owner. For all 336 lines at `lambda=1`, the arithmetic subtotal is

```text
pair circuits: 20,836,704*N*D
block scans:    1,217,664*N*D + 666,624*N
combined:     22,054,368*N*D + 666,624*N gate evaluations.
```

These are symbolic circuit counts at `D=2^73`; no circuit of that size was
materialized. The subtotal excludes the word's other scalar ADDs/CLEARs,
wrappers/maps, physical movement/address/control, storage and the output
consumer. Entry/F0/B1 costs and errors are additional. A finite format and
this subtotal do not establish a favorable complete moment.

Do not apply these constants to PR2540's retained-record word merely because
the desired logical outputs agree. Its chronology and error recurrence differ.
The [retention/movement thread](https://github.com/CrocSwap/integer-mult-bounds/discussions/2617)
prices other specified words and storage protocols. Ross Richardson's
[floor-grid](https://github.com/CrocSwap/integer-mult-bounds/discussions/2727#discussioncomment-18957511)
and [reversible-lifting](https://github.com/CrocSwap/integer-mult-bounds/discussions/2727#discussioncomment-18958062)
results have distinct rounding/restoration contracts; this page does not
transfer their constants or claim that nearest-even execution is reversible.

## Open next questions

The next useful task is a complete caller obligation, not another unbudgeted
local gate optimization. Pin one admitted child/caller and state its post-B1
input encoding, norm bound B, entry grid Q0 and error budget. Then specify
owners, signed payload layout, output/scratch lifetimes and where the single
block exponent survives all tensor factors. Charge scan and circuit evaluation,
the other scalar instructions, wrapper/map movement, addressing/control,
storage, cleanup and output consumption in one model. Unknown costs stay
unknown. Stop if a required owner/lifetime is unavailable or the fully charged
optimistic budget already fails.

This closes navigation to the five numerical results. It leaves caller entry,
physical realization and supplier admission open. The
[family expansion gate](research-family-status.md#contribution-acceptance-and-family-expansion-are-different-gates)
still applies before another dependent construction round.

## Exact sources and replay

| PR | Exact source head | Evidence at this checkpoint |
| --- | --- | --- |
| 2707 | `efa51a6c7ffec6edd556a98deedfe9deeba65809` | Incorporated local decoder, round 1600; ideal native proof inherited here. |
| 2736 | `eba0d6111a773cd13f5c0afb4354af2c85d04c3a` | Incorporated scoped lemma, round 1700; primary checker replayed. |
| 2771 | `e707681c3f6db70d0432501403e2122794a36ade` | Incorporated direct line, round 1700; primary checker replayed. |
| 2807 | `6fbab8c4b95cdf75dfcbb33806c31349408d73a2` | Incorporated finite format, round 1700; primary checker replayed. |
| 2811 | `3d07cfe7f5035bccf7975616b0f3bd53a3b78ca8` | Incorporated pair circuit, round 1700; primary checker replayed. |
| 2876 | `28c5c068b64c18074ab4044e47a7c9f52eb6e5de` | Pending; exact-head primary checker replayed separately. |

The [navigation audit package](../../research/qq16-numerical-contract-navigation/README.md)
pins retained receipts and dispositions, snapshots the pending README/receipt,
cross-checks the example and checks the source links. Its replay is a small
source-binding audit, not a repeat of all predecessor suites:

```sh
python3.12 -Werror -I -B scripts/research_package.py \
  --package research/qq16-numerical-contract-navigation
```

Primary-checker replay commands, environment, rejecting controls and limitations
are recorded there. No full selected cold replay or proof-assistant check was
run for this navigation contribution.

Credit Nick Petalas for PR2736/2771/2807/2811, Arham Tahir for PR2681/2876,
ywz65 for PR2707/2540, Ali Romman and the retained QQ16/native/geometry lineage.
Ross Richardson's separate floor and lifting contracts retain their credit.
The round-1600/1700 maintainer reviews establish the incorporation labels.

[scan]: https://github.com/CrocSwap/integer-mult-bounds/blob/28c5c068b64c18074ab4044e47a7c9f52eb6e5de/research/qq16-block-scale-scan/README.md
