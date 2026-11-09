# Chain-root caller on the merged G20 conjugation word

**Conditional ordinary BIT saving 0.00380058610508. Component bound only; no overall κ.** The chain-nested root caller (n=20, 3 thin queries, 18 local calls, 16 one-field idles, no supplier tree) runs on the local word of merged #5708 (`research/g20-conjugation-admission`, `WORD.json.gz`, SHA-256 `8dd441fd…c4b1`). The complete invoice has a raw crossing in **(0.00380058610514, 0.00380058610515)**, against 0.003507719059749 for #5708's own tree caller, an increase of 0.000292867045331. No input comes from an unmerged native word.

**Review question: the empty-field credit.** 111 of the 9,690 productive fields are the rank-1 targets of the empty field E, which carries only q. The gain rests on crediting them: without that credit the raw crossing is in (0.0032366, 0.0032367), below #5708's 0.0035077. #5708 credits its helper fields in the same way, but an outer use must feed E as an independent productive input. Is that credit acceptable, and can a consumer supply E?

Result summary (`check.py`, exact, about 15 s):

* Caller: 670 binary events (240 ADD, 393 SWAP, 18 LOCAL, 16 IDLE_ONE, 3 QUERY). 400 coefficients each: forward over F2[q,D^±1]/(q²−1), a separate transpose engine, the true integral inverse over Z[q,D^±1]/(q²−1), and a paired-address evaluation at moduli 101 and 10201. The time-reversed word passes the same engines, and forward-then-reversed is the identity.
* Local word: scalar replay, plus physical forward and adjoint replay of all 685 columns at address moduli 101 and 10201. An exact rational check on all 111 ports shows the word has the LOCAL form that the caller expects (`PROOF.md` section 2).
* Stream: 434,997 literal events, committed as `GLOBAL.jsonl.gz` (SHA-256 of the stream `ddc72b3d…a88c`), with 53,337 chronologically bound query descriptors. Each of the 18 calls checks main inputs, 415 helpers and 48 owned fields at return. Global endpoint: identity on 9,690 raw inputs, all dirty owned columns annihilated. A second pass recounts the bill from the emitted lines.
* Complete invoice: 9,690 productive fields, 53,337 paid jobs, rank surplus 753. Two separate rational-interval engines agree on the bracket.
* Finite admission: tested 0.00380058610513, uniform 0.00380058610512, cover loss 1e-14, tensor power 2048, reserve 2^-48, cutoff 13, floor 14, tail offset 1/5, γ<31/32, δ<19/20. Five acyclic levels start from #5708's completed backend 0.003507719059749 and reach the stated value.
* Controls: dropped LOCAL, QUERY, IDLE_ONE in both engines; shrunk and doubled idles; stray XOR; exchanged LOCAL roles; dropped native ADD and ERASE; wrong query rank; a free move on data; exchanged port lines; a physical query omitted; a skipped record in the stream; a short bill; a pin above the crossing.

## Scope

The native, ROW/spectator, owned-erasure, mixed-target compiler, ordinary-backend, precision, fixed-tape and analytic recovery premises remain, as in #5708. The merged status of #5708 is a lineage statement and not a proof of them. The enormous uniform word is not materialized. These are author checks; no independent acceptance is claimed. The caller is new and unmerged. It comes from the chain-nested root of #6833 and uses the integral reduction introduced in #6726; neither pull request's data or code is an input here.

The `IDLE_ONE` label is not on main. Each one is a paid query on one field, which is the same job as one half of the merged whole-idle primitive. A reviewer should confirm this reading.

Cutoff 13 and floor 14 replace #5708's 17 and 18. With only 9,690 fields, the completion ratio at floor 18 is 1.198, which fails. The completion-tail form with free cutoff and floor is the reviewed one (#4416, #4433). The guards `c^64<b^63` and ambient<256 are #5708's own, not part of #4433's statement; 13^k<14^(k-1) holds for every exponent k>=36.

**Orientation.** Reversal is unnecessary: the word has the LOCAL form in either orientation, and the forward and time-reversed callers have the same bill. The forward one is registered.

**Not examined.** Route legality and stage-block placement remain inherited premises, as in #5708. The ambient-cap lemma is not used for the admitted value.

## Reproduce

`python3.12 -I -B research/bit-chain-root-g20/check.py`, expected `PASS_CHAIN_ROOT_ON_G20_WORD`. See [PROOF.md](PROOF.md).

## Open next questions

* Can a reviewer accept this caller in place of #6726's fragment caller as the BIT dependency of the current towers? First step: check `PROOF.md` section 2 and the one-field idle reading against the retained native contract. It is blocked only on review.
* Does a different chain size improve the binary crossing on this word? First step: rebuild with `chainroot.build` on other child sizes and rerun this check. It needs a separate admission for each size.
