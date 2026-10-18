# Sharp 21-ADD positive-lift bound for the k8 leaver cells

The eight mutable-leaver cells used in the PR1005/1042 construction are already optimal in a precise local class: fixed twelve-register endpoint, arbitrary input dirt, and unit positive additions, or their fixed diagonal rational conjugates. Each needs exactly 21 additions: three source sums, three target transfers, and at least fifteen source-to-target additions.

This is a scoped obstruction to shortening those cells by monotone resynthesis. It is not an unrestricted rational lower bound or a paid-frame lower bound. No supplier, selected certificate, helper count, or kappa is changed.

Run from the repository root (Python 3.10+ standard library):

```
python -I -B research/leaver-monotone-optimality-seed21/verify.py
python -I -O -B research/leaver-monotone-optimality-seed21/verify.py
```

Expected:

```
PASS_LEAVER_MONOTONE_S21 cells=8 minimum=21 projected_minimum=5 controls=11
```

The default command independently recomputes all matrices, diagonal conjugacies, endpoint permutations, complete projected shortest paths, source binding and eleven controls, then compares the complete receipt. `--write` deliberately regenerates the receipt; it is not needed for replay. Acceptance uses explicit exceptions and remains active under `-O`. No predecessor modules are imported, no solver is needed, and no search cap is used.

`PROOF.md` gives the all-length counting argument. `CERTIFICATE.json` records all eight endpoints and twenty-four finite projections. `SOURCES.json` requires exactly twelve named source pins; text pins normalize CRLF to LF. Eight cell files are matched by name against the construction's coded list, including both unit and scaled operations.

Base: `ba82555c64e1879e4b7decce28186f208fcb8262`. The selected certificate at this base is PR1042, with unchanged kappa `1672188119205421/10^18`; this number is provenance only. The package does not read the mutable selected-result file during replay. It does not reconstruct the complete R480 word or rerun its native/hosted admission. In particular, the older R492 `gauge44-slots-t16/evidence/local/FULL-WORD.json.gz` is not treated as the selected rebuilt word. See the source-boundary discussion in `PROOF.md`.

The construction is Jeremy Kothe's PR1005/1018/1042 lineage. PR1049's independent audit already covers endpoints, leaver premises and accounting; this package adds the restricted sharp circuit lower bound. Prepared for @woklerx with substantial OpenAI Codex assistance. Apache-2.0; see `NOTICE.md` and `OVERLAP.md`.
