# Seven core ingresses are necessary and sufficient for the P104 chart-278 collapse

On the rational word of #7786, replacing the route $278\to288\to127$ by a direct send from 278 to 127 requires **seven incoming scalars from chart 3**. The original chart has six. This remains true when all ten old ingress payloads and all nine other egress payloads at 278 may be jointly recoded and all 901 surviving receiving deposits may change. The lower bound even grants arbitrary many extra messages from the other two original donors, 11 and 58. A seventh core ingress attains exact recovery on all 1,289 rational input coordinates. [Proof and precise communication model](PROOF.md)

Six exterior observations force the full six-dimensional image of the original core traffic modulo the two other donors' stock. This confines all possible six-channel recodings to a fixed 18-dimensional space. A nine-coordinate input kills that space and all old receiver deposits, while the required receiver output is one. The seven-channel realization preserves all original surviving deposits and requires a 299-term rational ingress. With the original ports kept funded, its exact paid-port surcharge is **94.9667971064257…** signed units across 48 rational calls. The selected multiplication bound is unchanged. [Exterior rank certificate](check_exterior.py) · [Separating input](check_input.py) · [Independent adjoint reconstruction](check_separator.py) · [Seven-slot recovery and price](check_repair.py)

The previous direct and cooperative routing results fixed the other paid observations. Here the nineteen local paid rules and the consequent receiver deposits may change. The earlier six-pair study considered specific pairs of paid payloads and protected the receiving arrivals. [#7795 paid-pair analysis](https://github.com/CrocSwap/integer-mult-bounds/pull/7795) · [#7807 direct-send result](https://github.com/CrocSwap/integer-mult-bounds/pull/7807) · [#7808 cooperative routing](https://github.com/CrocSwap/integer-mult-bounds/pull/7808) · [Coordination claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/7111#discussioncomment-19756126)

## Reproduce

From the repository root run the registered package with CPython 3.12. The checks use the Python standard library and authenticate the retained source word. All scalar, rank and tariff certificates use rational arithmetic.

~~~sh
python3.12 -B scripts/research_package.py --package research/p104-receiver-ingress-repair
~~~

## Open next questions

Can a change at a distinct donor or a retired funded port move useful information to chart 278 at a lower cost? Start with the nine-coordinate input in the proof and identify a chart supplying a scalar outside the certified 18-dimensional space. Check the full rank of the affected exterior pulse columns, protected terminal recoverability, and the complete signed bill. The current construction gives a concrete comparison against the best existing core-only augmentation.

## Attribution

Clear1nsight supplied the rational word, its four-return continuation and the paid-pair handoff, following the signed P104 framework of Ali Romman and the contributors in the retained notices. apoursh's direct and cooperative repair results supplied the frozen cut, the source reader, and the receiving-terminal recoding used in the construction. The present variable-stock threshold, exterior rank argument, separator and seventh-port realization were prepared by apoursh with substantial OpenAI Codex assistance under Apache-2.0. [Retained source pins](SOURCE-PINS.json) · [Original notice](retained/PR7786-NOTICE) · [Predecessor notice](retained/PR7795-NOTICE) · [License](retained/LICENSE)
