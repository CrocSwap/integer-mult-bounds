# Retiring an exterior-invisible P104 port has an exact repair cost

Chart 278 in the rational P104 word sends two payloads whose **sum** determines every output outside receiver 127. Either paid send can be retired by putting that sum in the other slot. Exactly two of the receiver's 902 required outputs then change. Replacing the retired port with a direct grade-seven send repairs both outputs on all 1,289 independent public coordinates. This is the cheapest additive repair under the enrolled tariff, even with arbitrary relays and free local readout. [Proof and communication model](PROOF.md)

| Retired send | Old grade | Best corrective grade | Net paid surcharge across 48 rational calls |
|---|---:|---:|---:|
| 95887 from 278 to 561 | 1 | 7 | +285.472830172972… |
| 100336 from 278 to 660 | 5 | 7 | +94.966797106425… |

A two-coordinate input proves the lower bound. All surviving paid values at rank three or higher vanish, yet the receiver at rank nine must return one. Exactly 933 ascending routes attain the least total grade for either retirement. The direct route uniquely minimizes the strictly concave tariff. For independent copies, even joint rational-linear coding needs one corrective unit of information per copy across each of seven cuts. [Cut, route and tariff checks](check_cuts.py)

The search also resolves the zero-addition case before choosing a particular merger. Fix the ten incoming payloads at 278. All ten outgoing payloads must equal their original functions even if they may be recoded together and all 902 receiver readouts can change. A full-rank modular minor separates the ten-dimensional source stock from the entire 902-dimensional receiver demand. More generally, the number of additional rational-linear receiver deposits required is exactly the rank of the two allowed port shifts, which ranges from zero to two. The additive repair price above uses the two literal sum mergers with the other paid payload rules fixed. [Rank certificate](check_rigidity.py) · [Causal repairs and operator comparisons](check_mergers.py)

The exterior kernel was identified while studying a different retirement through chart 288. Here that route remains funded. The paid surcharge rules out savings for these two explicit mergers and their corrective networks. The selected multiplication bound is unchanged. [Earlier exterior calculation](https://github.com/CrocSwap/integer-mult-bounds/pull/7814) · [Rational source word](https://github.com/CrocSwap/integer-mult-bounds/pull/7786) · [Coordination claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/7111#discussioncomment-19756389)

## Reproduce

From the repository root run the registered package with CPython 3.12. It uses only the Python standard library. The source reader checks the compressed and uncompressed word hashes. Ordinary and optimized Python both preserve the verifier's checks.

```sh
python3.12 -B scripts/research_package.py --package research/p104-exterior-route-recoding
```

## Open next questions

Can one keep the sum merger and also modify the surviving private route 95914 through chart 288 to lower the price? With one added scalar and the original chart-278 ingress stock, begin with a private change proportional to the retired form. Two independent change directions already introduce a rank-two deficit at the receiver, as the proof shows. Recheck the causal stocks after the change and account for every funded transfer.

## Attribution

Clear1nsight supplied the rational word and paid-port studies, based on Ali Romman's P104 caller and the contributors named in the retained notices. apoursh's earlier work supplied the source reader, exterior pulse method, adjoint replay and directed tariff check. The whole-receiver rigidity argument, two explicit port mergers, sparse separating input, seven-cut batch bound and repaired words were prepared by apoursh with substantial OpenAI Codex assistance under Apache-2.0. [Source pins](SOURCE-PINS.json) · [Source notice](retained/PR7786-NOTICE) · [Paid-port notice](retained/PR7795-NOTICE) · [License](retained/LICENSE)
