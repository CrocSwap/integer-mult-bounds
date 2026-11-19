# Joint rerouting after a P104 exterior port retirement

Retire either exterior port in the chart-278 sum merger and release **both** transfers of the original private route through chart 288. The exact price of any replacement with rational-linear scalar messages across $L$ independent copies is
$$
L[p(7)+p(2)+p(5)].
$$
The unique cheapest topology buys $L$ direct grade-seven sends from 278 to 127 and $L$ copies of the grade-two and grade-five legs through 288. Each new message can use all local native stock and earlier new messages, from any copy. The receiver may use arbitrary deterministic readout. The result covers all finite fixed routes on the 1,103 original chart labels with equal-span sharing, while the other native paid operators remain fixed. [Model and proof](PROOF.md)

| Retired exterior slot | Original grade | Best net change in the 48-call paid invoice |
|---|---:|---:|
| 95887 | 1 | +285.472830172972… |
| 100336 | 5 | +94.966797106425… |

Two independent public inputs require two scalar dimensions per copy at receiver 127. A separate three-coordinate input forces a pickup of independent information outside the source. The two cut constraints together establish the exact tariff even when replacement routes branch, use feedback or mix different calls. For a single copy exactly **9,275 distinct positive-edge multisets** attain the minimum total grade of fourteen, and only one attains the best tariff. Every one of these topologies admits a chronological rational-linear reconstruction. [Input witnesses](check_witnesses.py) · [Topology census](check_topologies.py) · [Price inequalities](check_prices.py)

The prior result in #7818 fixed both private transfers while paying for additional repairs. The present joint optimum releases and credits those transfers. The sum merger's best net charged price still increases. All slopes $t$ in the proposed private-payload edit $v_C+t h$ attain the same least supplemental tariff, with one readout correction vanishing at $t=\pm1/2$. This local result leaves the selected conditional exponent at 0.00363005817. [Previous merger](https://github.com/apoursh/integer-mult-bounds/blob/bf3c8a8fde5a111954c76518818431f3999dc276/research/p104-exterior-route-recoding/PROOF.md) · [Public coordination](https://github.com/CrocSwap/integer-mult-bounds/discussions/7111#discussioncomment-19756932)

## Reproduce

Run from the repository root with CPython 3.12 and its standard library.

```sh
python3.12 -B scripts/research_package.py --package research/p104-private-route-recoding
```

The four checks replay the two witness spaces, construct eight complete causal words, compare all 1,289 terminal operators, count minimum-grade networks and enclose all tariff gaps by rational arithmetic. An independent backward expansion checks the two affected outputs on all public coefficients. The bundled word reader checks compressed and uncompressed digests. [Operator construction](check_reconstruction.py) · [Verification manifest](VERIFY.json)

## Open next questions

Which modification to a surviving chart-278 ingress or an exterior reader can make a second independent plane coordinate available beyond rank two without incurring the grade-seven surcharge? A candidate must account for its impact on all 387 exterior outputs. Replacing a third native route can also change the set of charts that observe the side input, giving a concrete second cut to test before building a whole word.

## Attribution

Clear1nsight supplied the #7786 word, the #7795 receiver-cut evidence and the three-coordinate input. Ali Romman supplied the underlying #7776 P104 caller. The earlier #7808 and #7818 studies by apoursh supplied scalar route and merger calculations. This contribution's two-dimensional restriction, joint flow and side-information lower bound, complete two-chain census and reconstructions were prepared by apoursh with substantial OpenAI Codex assistance under Apache-2.0. [Source pins](SOURCE-PINS.json) · [Source notice](retained/PR7786-NOTICE) · [Paid-port notice](retained/PR7795-NOTICE) · [License](retained/LICENSE)
