# Default-precision false brackets in the archived PR1048 pricer

Both original `certify_c` and `certify_c_bad` at PR1048 commit
`07730cd8302c378607259a9ad0efb73e0b57a2f2` return a bracket that excludes the
true root on the two explicit profiles below. This uses their **unchanged default
34 terms and24 decimal digits**, without monkeypatching or disabling any valid
input assumption. The ordinary nonoptimized run also passes the original
assertions. This sharpens the maintainer's already recorded undecided-sign
finding into concrete false certificates and supplies a narrowly scoped repair.

Let m=9, W=10^64, a0=1/20, delta=10^-24, and

```text
lambda = 0                        (certify_c)
lambda = 2592/10^16                (certify_c_bad)
N = floor(9W / ((1+lambda) * 3^(1/10)))
profile = {rank1: N}
```

The profile is constructed by an integer tenth root; no numerical root estimate
is used to establish the mathematical result.

| Input count | Original returned bracket | Exact root location | Repaired result |
|---|---|---|---|
| N, either surcharge choice |[a0-delta,a0]|(a0,a0+delta)|[a0,a0+delta]|
| N+1, either surcharge choice |[a0-delta,a0]|(a0-delta,a0)|[a0-delta,a0]|

An exact degree10 integer inequality proves the side of a0. A simple rational
inequality proves the neighboring tick bound. The independent checker imports
neither the original pricer nor the repair and uses no logarithm/exponential
library. It also checks that the original floating nomination already encloses
the true root: the demonstrated failure occurs in the subsequent rational
bisection's treatment of an undecided upper sign.

`repair.py` maintains two strictly certified endpoints. An enclosure crossing
zero has a third status, **undecided**, which triggers increased interval order.
At a fixed resource cap it returns `UNRESOLVED` with the retained wider certified
bracket; it never calls that result a one-tick certificate. Exact grid roots can
also remain unresolved. The original interval routines are reused unchanged
inside their explicitly checked domain.

Run from the repository root:

```text
python -I -O -B research/profile-bracket-audit64/verify.py
python -I -O -B research/profile-bracket-audit64/independent.py
python -I -O -B research/profile-bracket-audit64/controls.py
python -I -B research/profile-bracket-audit64/verify.py
```

The main command reproduces both false brackets and two neighboring controls,
checks the repaired brackets, compares a normal small-profile bracket, and
exercises a capped undecided calculation. Ten rejection controls cover arithmetic,
coverage, source pins and interval validity, with two further controls for exact
grid equality and uncertified initial endpoints. `--write` regenerates EXPECTED;
normal verification compares it without mutation. VALIDATION.json records the
completed commands and the frozen selected-record check.

This is an audit of **abstract paid-profile arithmetic**, not a claim that the
large profiles arise from realizable suppliers. It does not refute the selected
PR589 bit endpoint or PR1094 kappa, change the selected record, rerun the full
PR1048 search, certify neighborhood exhaustion, or repair its other ordering and
search-scope claims. PR1048 remains deferred. The frozen context is base
`ce7ad1b6ab09452c3478723a2e96ed5ff212dc08`; future selected-pointer changes do not
invalidate the package. See PROOF.md and PROVENANCE.md.

@woklerx, substantial OpenAI Codex assistance. Apache-2.0. Original flemhhh
source and its DeepSeek assistance notice are retained in vendor/.
