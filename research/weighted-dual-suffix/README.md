# Weighted carriers on the dual-suffix rational-center producer

Under the inherited analytic, fixed-tape and newly proposed PR104 interfaces,
this finite candidate gives **κ = 39980858679/500000000000000 = 7.9961717358×10⁻⁵**,
**0.0986743% above PR108**. The strict complex saving is
**7997468953/10¹⁴ = 7.997468953×10⁻⁵**.

PR108's scalar graph, exact binary frames, all 24 rational centers, coordinate
order, odd divisor 21, retained-center corrections and stopped bit axis are
unchanged. We select a different set of 15,422 legal carrier links. The role
count stays 43,270, but their complete width histogram has a smaller moment.

The search used SciPy numerical minimum-weight assignment to suggest links,
with weights derived from the complete rank-dependent cost. Floating-point
optimization is not proof of optimality. The committed witness is the explicit
link list; verification requires neither SciPy nor trust in its optimization.

## Verification

```
python3 research/weighted-dual-suffix/verify.py
python3 research/weighted-dual-suffix/test_controls.py
make verify
```

The verifier regenerates PR104, PR107 and PR108 producers, then checks the
selected matching in the inherited C++ checker and an independent Python
implementation. The Python audit builds every active frame over GF(2), checks
nondegeneracy and operand nesting, then validates shared operands, strict carrier
order, exact frame inclusion and matching uniqueness. Both implementations
recount every paid histogram entry, including retained-center corrections.
The exact assembly has 47 strict constraints and seven margins. The next grid
points for complex saving and κ are rejected. Ten controls include duplicate
links, invalid donors, out-of-range uses, corrupted ranks, omitted loss, unpaid
cleanup, histogram mutations and exclusion of PR108 at this new saving.

Full repository verification is pending. A passing finite verifier does not
independently establish PR104's all-size opposite-bank, stopped streaming or
odd-grid interfaces. No global optimality or practical runtime gain is claimed.
See [proof.md](proof.md) for the unchanged proof obligations and local transfer.

Credit Rohan Arun with Anthropic Claude assistance for PR108; Rohan Gupta /
gupt1156 for PR55 dual-suffix strips; icekylinx for PR104 rational centers and
stopped products; the prior weighted-carrier work in PR44; and all contributors
credited in the inherited NOTICE and SOURCES. This refinement was prepared by
Rohan Arun with OpenAI Codex assistance, Apache-2.0.
