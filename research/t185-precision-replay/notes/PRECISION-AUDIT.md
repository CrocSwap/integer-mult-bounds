# Independent precision-only candidate audit

**PASS for endpoint arithmetic and driver scope; full release remains separate.**
The candidate keeps PR2863's T185 word, allocation and paid profile unchanged.
This is an explicit rational endpoint refinement, not a new construction.

Audited baseline head: `34328b1d5e5bebac62d5cabec993dfbfd7b2123f`.
Audited generated driver SHA256:
`8aa91da8b39f212ef786f7788682dce45d6217f399f02a063f62763d096cbfb7`.
The `driver40/` and `driver40-authenticated/` driver, helper and derivation
receipt are byte-identical.

Set

`C40 = 0.0017201008054168859279440070756063355312`

and `K40 = C40 - 10^-62 - 10^-86`. The exact positive gain over the full
PR2863 rational is

`7.07560633553120000009999999999999999000000009999999999999999e-27`.

`check_precision.py` uses this audit's independently implemented exact log
bounds and alternating `exp(-t)` polynomials. It accepts C40 and rejects
C40+`10^-40` with strict moment signs. It also independently checks the
conservative endpoint and its next grid point, accounting for the retained
surcharge as the exact extra rank-one coefficient
`32*73^2*sum(profile)/10^16`. The fine bracket lies inside the interval where
the separately audited LP dual is uniformly valid. Adding one rank-one paid
child destroys acceptance, as required by the actual negative control.

The independent source/AST comparison finds nine declared driver edits, all
of which reverse to the exact original driver bytes. There are 39 original
`need`/`assert` predicates and 41 in the new driver. The only replaced original
predicate is the fixed 24-digit κ equality, generalized to the declared DIG
while preserving strict superiority over the pinned full baseline. The two
added predicates authenticate the discovery helper before use and after
copying. The complete retained `check_moment` block is unchanged: original
coarse checks and both original fine engines must still accept/reject the
actual native and conservative endpoints during complete admission.

All affected numeric expressions agree with the original at DIG24:
supplier gap `10^-104`, root grid `10^-24`, floor `10^-70`, backoff `10^-46`.
The generated builder supports 26..70, so this is a source-reversal and numeric
roundtrip, **not** a claimed execution of a generated 24-digit wrapper.
Ordinary bootstrap grid 18, margin 28 and depth 12 are unchanged. No source,
native, frame, inventory, owner, precision invoice, control or release gate
is removed. I found no missing DIG-dependent scaling in the changed driver.

Reproduction (standard library only):

```sh
python3 -B check_precision.py \
 /workspace/scratch/bc9e58970b2a/continuation-20261016/pr2863/research/shared-kernel-packing \
 /workspace/scratch/bc9e58970b2a/continuation-20261016/outer-precision \
 precision-evidence \
 /workspace/scratch/bc9e58970b2a/continuation-20261016/source2833/code/assemble.py
```

Exit 0, approximately 0.10 seconds. `precision-evidence/RESULT.json` records
exact intervals, rational κ/gain, all source hashes and the predicate audit.
`PRECISION-RUN.json` binds this script, evidence and log. Full strict release,
the current-frontier comparison and an integrated source/manifest check remain
parent-owned requirements before claiming an improvement.

Prepared with OpenAI Codex assistance, Apache-2.0. Construction, outer transfer
and original-checker credit stays with the contributors named in PR2863 and
its retained sources; the endpoint generator belongs to the outer-precision
worker. No human peer review or maintainer acceptance is asserted.
