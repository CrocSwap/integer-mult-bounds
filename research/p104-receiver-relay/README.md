# All minimum-grade cooperative repairs of P104 receiver 127

On the rational word of #7786, delete transfers 95914 and 88 and let the 1,103 original charts exchange any finite number of new nested-span messages to restore receiver 127. Keep the surviving paid rules, chart assignments and exterior terminals fixed. **Every successful repair spends at least seven total grades. Exactly ten positive-transfer topologies attain seven, and the incumbent is the unique cheapest at the enrolled target.** The result allows arbitrary deterministic local encodings. All ten attaining paths also work as exact chronological rational-linear programs. [Proof, scope and tariff table](PROOF.md)

Every seven-grade path must run from 278 through 288 to 127. It may pass through 561 before 288 and through one of 239, 267, 477 or 1100 after 288. The unique runner-up, through 561 alone, adds **0.257824154185337662623932…** signed units across the 48 rational calls. Even the most expensive of the ten adds less than 0.722. Every other positive-transfer topology adds more than **47.224621260611063462113308** units. The best saving from rerouting this frozen cut is exactly zero. The selected multiplication bound is unchanged. [Exact price verification](check_prices.py)

The direct-send optimization in #7807 allowed communication only into the receiver. Here relay charts may pool old stock, exchange new messages and forward the result. The proof contracts equal-span labels, traces a necessary information path, identifies a second independently necessary waypoint, and exhausts its two intervals in the actual atlas. Equality constructions preserve the complete 1,289-coordinate operator. [Earlier direct-only result](https://github.com/CrocSwap/integer-mult-bounds/pull/7807) · [Coordination thread](https://github.com/CrocSwap/integer-mult-bounds/discussions/7111#discussioncomment-19755743) · [Source pins](SOURCE-PINS.json)

## Reproduce

From the repository root, run the registered package with standard-library CPython 3.12.

~~~sh
python3.12 -B scripts/research_package.py --package research/p104-receiver-relay
~~~

The three standalone checks below also work from a read-only export without Git or network access.

~~~sh
python3.12 -IB check_paths.py
python3.12 -IB check_operators.py
python3.12 -IB check_prices.py
~~~

## Open next questions

Can an edit to an existing ingress at chart 278 or 288 eliminate the mandatory waypoint? A concrete first test is to identify a surviving ingress whose recoded payload is nonzero on witness D at chart 278 while preserving the 901 old receiver deposits and all exterior terminals. Such a modification changes the frozen-stock hypothesis. Its altered bill, propagation to later readers, restoration costs and productive credits would all need to be checked against the signed target. [Earlier six-pair constraints](https://github.com/CrocSwap/integer-mult-bounds/pull/7795)

## Credit

Clear1nsight supplied the four-return word in #7786 and the first three-coordinate separating input in #7795, building on the signed P104 framework from Ali Romman and predecessors credited in the original notices. The other inputs, source reader and frozen direct-cut calculation come from apoursh's #7807. The cooperative path classification, constructive subdivisions and signed separation were prepared by apoursh with substantial OpenAI Codex assistance under Apache-2.0. [Retained original notice](retained/PR7786-NOTICE) · [Predecessor notice](retained/PR7795-NOTICE) · [License](retained/LICENSE)
