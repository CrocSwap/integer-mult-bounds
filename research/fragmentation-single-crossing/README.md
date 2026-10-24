# Prove the fixed p16 fragmentation invoice has one crossing

Every positive-integer fragmentation of the stated main/helper increments
has a strictly increasing moment on t in [4/5,1], and exactly one crossing
in C=1-t in (0,1/20). This removes S1 from the p16 sufficiency test in
[PR #5226](https://github.com/CrocSwap/integer-mult-bounds/pull/5226) for this
class. It does not improve kappa or prove a new native word.

[PROOF.md](PROOF.md) gives the class, weighted-tail argument and exact endpoint
sign. [RESULT.json](RESULT.json) records the certificate. [SOURCES.json](SOURCES.json)
pins the source invoice and S1 statement at canonical main
ff3cc58e370d0f678e529246f8c73e8094e18fcf, priority 7. The
[claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19151239)
excludes descents, extra jobs, coded interfaces and changed endpoints.

## Reproduce

Use CPython 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/fragmentation-single-crossing
python3.12 -I -O -W error -B research/fragmentation-single-crossing/verify.py
```

Expected marker: PASS_FRAGMENTATION_SINGLE_CROSSING. Both modes check the
complete invoice, 144 weighted tails, 96 integer partitions, 22 root intervals
and a rational exponential bound. The quantified proof covers every partition
assignment. No native, Lean, compiler, outer-ledger or selected replay ran.

## Open next questions

Test the weighted tails of one specified changed invoice. A negative tail
means this sufficient test does not apply; it does not prove multiple roots.
Then derive a suitable interval proof. TASK.json records this next step.

## Credit

Cao Yifan's PR #4610 supplies the source invoice. PR #5226 supplies the
fragmentation framework and S1 question; its README attributes the text to
Claude Opus 5.5 via Claude Code. The proof links these sources and retains
controller/native credit. New proof and checks: Ali Romman with substantial
OpenAI Codex assistance. Apache-2.0; author-checked, not independent acceptance.
