# T74 handoff line: pinned κ ledger, 95 stated numbers and 82 release gates re-checked, independent-check map

**Research consolidation; no κ claim.** The T74 line has fifteen open conditional-κ PRs. Their descriptions and READMEs
contain many interlocking "exceeds PR#### by X" and "PR#### (kappa X)" statements. This package:
- pins each PR's own claim file;
- transcribes the numeric statements between pinned PRs from PR bodies and pinned package READMEs (coverage below),
  and recomputes each one with exact rational arithmetic;
- parses and checks the predecessor gates of every pinned `verify_release.py`;
- maps which claims have independent checks.

## Findings

- **The release gates are right.** 82 predecessor gates in 10 of the 12 pinned scripts are attributed to pinned PRs:
  - **55 EXACT.** The gate literal equals the named PR's pinned κ.
  - **17 ABOVE**, which makes them conservative:
    - PR2322's native-endpoint upper bracket (6 gates);
    - the PR2363 literal in the label slip below (5);
    - PR2436's κ rounded up at 24 digits, +1e-46 (6 gates, in PR2462 and PR2474). Each script repeats this gate three
      times, and its comment says "exact kappa".
  - **10 BELOW**, all PR2265's published 43-digit κ, a truncation 9.7e-45 below its pinned value. This is
    immaterial, since every margin over PR2265 is at least 1.28e-5.
  - Every gate passes, and the exact pinned values confirm that every named predecessor is exceeded. **So none of the
    errors below affects any κ value or release gate; they are text-only.**
  - The PR2269 and PR2309 scripts gate only on older PRs.
  - Nine unnamed gates, "the previous 1e-3000 fixed-grid-maximum package without the frame refit", have a literal
    exactly equal to PR2281's κ.
- **95 stated numbers checked: 84 consistent, 11 flagged.** 32 come from PR bodies and 63 from READMEs. Two of the
  consistent ones are quotes of PR2269's κ that also fit PR2281's, since the two agree to 90 digits. The 11 flagged
  statements fall into three classes:
  - **(A) wrong target:** five statements, three in PR bodies and two repeated in READMEs;
  - **(B) self-κ quoted as the predecessor's:** the READMEs of PR2435, PR2447 and PR2474;
  - **(C) stale copied boilerplate:** three READMEs.
- **One gate label slip.** In PR2374, PR2435, PR2447, PR2462 and PR2474, a gate whose comment and literal are PR2363's
  exact κ reports "does not exceed PR2322". The check itself is right, since PR2363's κ is above PR2322's. A second,
  correctly labelled PR2363 gate follows it.

## Ledger (pinned claim files at exact heads; `PINS.json`)

κ values are shown to 22 decimals, truncated (…). "Δ" is the exact difference to the previous row.

| PR | author | κ (pinned claim file) | Δ | construction step |
|---|---|---|---|---|
| 2265 | DreamingOfClouds | 0.0016834125885426074623… | (baseline) | PR1673 outer retune on PR2260's selective-borrowing supplier (T8 parent, not T74 words); included because the line compares against it |
| 2269 | jeremykothe2 | 0.0016962471390584742207… | +1.283455e-5 | 43 anticipatory dirty-borrowing aliases (PR2226) on the T74 words, under the inherited PR1673 outer |
| 2281 | jeremykothe2 | 0.0016962471390584742207… | +5.376787e-91 | PR2269 recertified at a 1e-3000 endpoint |
| 2288 | jeremykothe2 | 0.0016963109504150503355… | +6.381136e-8 | exact frame refit of the borrowed gauge44 word |
| 2302 | jeremykothe2 | 0.0016963957667360813401… | +8.481632e-8 | pivot-518/506 helper-donor kernels |
| 2309 | Dugongue | 0.0016965151242727336160… | +1.193575e-7 | 44th dirty alias with owner repacking (claim-file status `FROZEN_…_PENDING_STRICT_REPLAY`) |
| 2312 | jeremykothe2 | 0.0016968910672416183217… | +3.759430e-7 | helper width exchange |
| 2322 | Vlado-V | 0.001697060296258836 | +1.692290e-7 | four coherent helper handoffs |
| 2349 | jeremykothe2 | 0.0016970659941088806668… | +5.697850e-9 | owner relocations on PR2322's words |
| 2363 | mason-hale | 0.001697147064845350 | +8.107074e-8 | whole-role augmenting paths (owner map) on PR2322's words |
| 2374 | jeremykothe2 | 0.0016971949509017704265… | +4.788606e-8 | exact owner fill on PR2322's words |
| 2435 | jeremykothe2 | 0.0016985113436976293290… | +1.316393e-6 | entrance raise of 24 copy buffers |
| 2447 | jeremykothe2 | 0.0016985119240027614377… | +5.803051e-10 | pattern-optimal owner fill (PR2442) on PR2435's words |
| 2436 | tekuuu | 0.0016991608921398251600… | +6.489681e-7 | four lifted-target aliases composed with PR2435's 24 entrance raises, plus six owner-slot replacements |
| 2462 | jeremykothe2 | 0.0017035523129795943854… | +4.391421e-6 | port of PR2436's four aliases (with A-phase prelude and verifier/transport edits) onto PR2447's words, 430 helpers per call against PR2436's 428, with a claimed-optimal owner fill |
| 2474 | jeremykothe2 | 0.0017036763879936764890… | +1.240750e-7 | a fifth PR2436-style alias (helper 637 borrows retired source register 31) on PR2462's words |

## Flagged statements (ids refer to `STATEMENTS.json`; `b` = PR body, `r` = README)

Each suggested correction is checked as CONSISTENT by the script.

| id | statement | true value | the printed value is actually | suggested correction |
|---|---|---|---|---|
| 2302b2 | PR2302 body: "exceeds PR2288 … and PR2269 by 8.48163E-8" | vs PR2269: 1.48628E-7 | PR2302 − PR2288 | "exceeds PR2288 by 8.48163E-8 and PR2269 by 1.48628E-7" (the PR2302 README already says +1.48628E-7) |
| 2374b3, 2374r5 | PR2374 body and README: "… and PR2312 by 1.28957E-7" | vs PR2312: 3.03884E-7 | PR2374 − PR2349 | "… and PR2312 by 3.03884E-7", or "… and PR2349 by 1.28957E-7" |
| 2435b2, 2435r4 | PR2435 body and README: "… and PR2312 by 1.31639E-6" | vs PR2312: 1.62028E-6 | PR2435 − PR2374 | "… and PR2312 by 1.62028E-6" |
| 2435r1 | PR2435 README: "exceeds PR2374 (our previous package, kappa 0.0016985113436976293…)" | PR2374: 0.0016971949509017704… | PR2435's own κ | "kappa 0.0016971949509017704…" |
| 2447r1 | PR2447 README: "exceeds PR2435 (our previous package, kappa 0.0016985119240027614…)" | PR2435: 0.0016985113436976293… | PR2447's own κ | "kappa 0.0016985113436976293…" |
| 2474r1 | PR2474 README: "exceeds PR2462 (our previous package, kappa 0.0017036763879936764890…)" | PR2462: 0.0017035523129795943854… | PR2474's own κ (the PR2474 body quotes PR2462 correctly) | "kappa 0.0017035523129795943854…" |
| 2288r6, 2302r6, 2312r8 | PR2288 / PR2302 / PR2312 READMEs: "this package … exceeds PR2265 by about 1.28e-5" | 1.290e-5 / 1.298e-5 / 1.348e-5 | PR2269 (or PR2281) − PR2265; the sentence was copied from PR2269's README | "by about 1.29e-5" / "1.30e-5" / "1.35e-5" |

## Independent checks per claim (as of this snapshot; not exhaustive)

- **PR2269:**
  - PR2315 reproduces the words, the 437-helper fill and the moment root. It checks only the b → κ arithmetic, not
    the outer.
  - PR2286 audited the written side conditions of the inherited PR1673 outer stack at PR2044's parameter point (head
    322949a5). They were not re-substituted at PR2269's point.
- **PR2312 → PR2322 pricing change:** PR2359 (AAAmirinu) independently reconstructs the raw paid-frame change. It
  checks pricing only.
- **PR2322 words, which PR2349, PR2363 and PR2374 share:**
  - PR2402 certifies that every legal whole-helper owner fill (unsplit helpers, unchanged PR2269 bin stock) has
    b < 0.001697195759.
  - PR2442 shows that PR2374's idle multiset is the bin-pattern integer optimum, unique within 1e-12, and that every
    such fill has b ≤ κ(PR2374) + 1e-15. So PR2349 and PR2363 have no owner-level headroom above PR2374 on these
    words.
  - PR2406 (jeremydiviney) caps every scalar and handoff frame refit of these words with fractional whole-helper
    packing at b < 0.0016972. Its hypotheses include fixed helper endpoints and fixed prefix/cut frames. PR2435's
    entrance raise changes frames outside those hypotheses.
- **PR2435:**
  - PR2446 independently reproduces the words, the 289,044-role owner map and the root. It finds that the change is
    frame-only.
  - PR2472 (RossRichardson) binds and checks the 24 raised-entrance wrappers, which is the local entrance delivery
    PR2446 left open. Its stated premises are logical restoration and whole-family hosting.
  - PR2453 prices the mechanism.
- **PR2447:** PR2466 checks its owner map (R-a..R-g), recount and root, and shows that its idle multiset is exactly
  PR2442's optimum. It does not re-check admission.
- **PR2436, PR2462, PR2474:** no independent check found. Search covered PR titles and bodies through #2479, plus the
  checks reported by this package's reviewers.
  - PR2478 (mdumitrean) reports an `audit_local.py` gap. It states that T74 claims are not affected because their
    admission runs the native chain.

## Reproduce

From the repository root, standard library only:

```sh
python3 -I -B research/t74-claim-lineage-ledger/ledger.py --fetch
```

`--fetch` fetches each `refs/pull/N/head` whose pinned head is absent, falling back to the pinned commit itself.
Expected final line:

```
PASS_T74_CLAIM_LEDGER prs=16 statements=95 (body 32, README 63) consistent=84 (ambiguous 2) flagged=2288r6,2302b2,2302r6,2312r8,2374b3,2374r5,2435b2,2435r1,2435r4,2447r1,2474r1 gates=82
```

**What the offline run checks:**
- every claim file, README and release script against its git blob, and the claim files also against sha256;
- every README quote against its pinned README:
  - the whole normalised quote, or, where the transcriber elided text, its fragments in order within 400 characters;
  - each quote must contain its stated number;
  - each must name its target or carry a `context` naming it within 800 characters before it;
- every statement, with exact rational arithmetic;
- the gate parse, which must account for every `if Fraction(kappa_decimal) <= Fraction(` line;
- controls run through the same functions:
  - 315 negative controls, all rejected:
    - each consistent number ±1 in its last printed digit;
    - each consistent difference attributed to a wrong target;
    - each README quote with one digit changed;
    - each pinned file against a wrong blob;
    - three synthetic gates: one above the source κ, one in an unparsed shape, one with a swapped label;
  - 11 positive controls: each suggested correction must be CONSISTENT.

The flagged set with what each printed value matches, the ambiguous set, the BELOW gates and the label slips are all
asserted. Any change to `PINS.json` or `STATEMENTS.json` that alters them fails the run.

**Live drift check.** PR bodies are not in git. `--live` uses network access and the GitHub CLI to compare each pinned
head with `refs/pull/N/head`, each body hash with `BODIES.json`, and each body quote with the current body. Any drift
ends with `DRIFT_T74_CLAIM_LEDGER …` and exit status 3. At this snapshot it ended with `live_drift=0`. It covers the
pinned PRs only; it cannot discover new PRs or comments.

**Rounding rule.** A number agrees when the true value, rounded half-even or half-up to the printed digits, equals
it. "About" and "approximately" get no extra slack. Under truncation, 2288r6 alone would also agree. A κ quote agrees
when it is a prefix or a correct rounding of the target's pinned κ; it is reported as ambiguous when it fits other
pinned κ too.

All results were run on CPython 3.14.4. The registered Python 3.12 replay was not run locally.

## Scope and limits

- **What is checked.** The numbers stated in PR bodies and pinned READMEs between pinned PRs, and the predecessor
  gates in the 12 pinned `verify_release.py` scripts. No κ, outer ledger or construction is re-derived. Each κ is read
  from its PR's own claim file.
- **No parsed gates for PR2322, PR2363 and PR2436.** They have no `verify_release.py`. For example, PR2436's
  `budget/price_composition.py` compares against PR2435's κ truncated to 18 decimals; that check is not parsed here.
- **Transcription coverage.** Statements were found by regex sweeps of the 16 bodies and READMEs, followed by reading
  each hit, plus two adversarial review rounds that found ten statements the sweeps had missed. Not included:
  - comparisons with unpinned PRs, such as PR2260, PR2220 or the selected PR1094 ("1.464% of κ");
  - ratios to PR2322's packing cap ("about 98.66%", "about 98.6678%");
  - values attributed to unpinned audit PRs, such as PR2436 README's "PR2435 pattern optimum has root approximately
    0.0016985119240";
  - statements in other files (RELEASE.json, REVIEW.md, scripts other than the gates).
- **Snapshot.** Heads are pinned as of 2026-10-15 (newest: PR2474 head 5298f86c). PR2309's own claim file marks it as
  pending strict replay, so it is listed for ordering only.
- **Not pinned.** PR2482 (mdumitrean), opened after the snapshot, is a superseded conditional construction composing
  PR2309 and PR2302 (κ 0.0016965999…, between PR2309 and PR2312). By its own statement it is not a leading bound.

## Open next questions

- **PR2436, PR2462, PR2474.** Are their owner fills exactly optimal for their words, and do the words recount to the
  reports? First step: run PR2442's `owner_optimum.py` and PR2446/PR2466's checker on the pinned files.
- **Machine-readable predecessors.** Could each claim file record its predecessors as `(PR, exact κ)`? The release
  gates already hold these values. Exposing them would make this check automatic and would remove class (B) and (C)
  slips, which come from hand-written comparison sentences.

## Credits and licence

- PR authors as listed in the table (GitHub handles).
- Independent checks referenced:
  - thakrarsagar (this package's author): PR2286, PR2315, PR2402, PR2442, PR2446, PR2453, PR2466;
  - AAAmirinu: PR2359;
  - jeremydiviney: PR2406;
  - RossRichardson: PR2472.
- Two rounds of two adversarial AI reviewers of this package found the missing statements, the PR2281 and PR2436
  omissions, the PR2447 mislabel, a missed gate shape, tautological controls and several wording errors in the
  check map.

Prepared with substantial AI assistance (Claude Code, Anthropic, Claude Opus 5.5). No independent human review is
claimed. Apache-2.0.
