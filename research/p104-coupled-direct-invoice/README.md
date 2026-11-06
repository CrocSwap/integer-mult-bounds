# Four-site coupled roots lose under the complete direct invoice

For q=2, n=4 and full sites 0,1,3,4, every shortest-query root with
compatible commuting actual-prefix projectors loses at kappa 0.00330720
under the retained #6726 native source, arbitrary positive binary-child
allocations and separately paid direct stage idles. The exclusion extends
through 0.004. It permits arbitrary ordinary coupling of all eight inputs
and every stage-rank pattern. Ordinary operations are optimistically free.

The exact finite maximum is below −0.06504536308798 per physical port;
a concave upper envelope excludes all larger allocations. The proof uses
only predecessor geometric lemmas and remains valid even when its relaxed
inventory includes an unrealizable rank 20 profile.

This does not cover new retirements, paid fragmentation, cross-stage idle
fusion, other full-site sets, larger roots or a changed native schedule.
There is no new kappa claim, selected-frontier change or new physical word.

Read [PROOF.md](PROOF.md) for the complete invoice, proof and open questions.
[ORIGINS.json](ORIGINS.json) pins exact source bytes and original notices.
[DIRECT-INVOICE-RESULT.json](DIRECT-INVOICE-RESULT.json) is the exact full
receipt; [CONVENTIONS.json](CONVENTIONS.json) records independent matrix
and literal-histogram checks.

Reproduce from the repository root with Python 3.12, standard library only:

```sh
python3.12 -I -B research/p104-coupled-direct-invoice/verify_direct_bill.py
python3.12 -I -O -B research/p104-coupled-direct-invoice/verify_direct_bill.py
python3.12 -I -B research/p104-coupled-direct-invoice/check_conventions.py
```

The full evaluator checks 62,007,750 exact pattern/allocation bounds and
normally takes a few minutes. It verifies the saved receipt without
writing files. `--write` explicitly regenerates that receipt. The matrix
and literal histogram checker is small and uses a separate Decimal
evaluation for the worst relaxed invoice; it is not a second all-allocation
proof or an independent audit of the complete native word.

Jerry Chen / @CubeJerry with substantial OpenAI Codex assistance.
Apache-2.0. Original predecessor notices remain unchanged in inputs/.

The registered command is `python3.12 -B scripts/research_package.py --package research/p104-coupled-direct-invoice`. It runs the complete outward-integer evaluator and both small-check modes. The complete optimized evaluator was also executed separately, as recorded in `VALIDATION.json`. `REVIEW.md` records separate source-aware AI review. Frozen predecessor bytes are authenticated by `ORIGINS.json`; these pending heads are not generic Git-history dependencies. No selected cold replay, full-history preflight, hosted CI or scientific admission is claimed.

## Open next questions

Can a literal paid fusion or retirement overcome this direct-invoice loss, or can a different root/site set produce a better complete budget? First exhibit the full arbitrary-input word, then recount every native, productive and paid term. The present proof does not cover those changed mechanisms. Detailed questions and blockers are in `PROOF.md` and `TASK.json`.
