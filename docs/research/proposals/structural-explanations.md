# Proposal: voluntary "mechanism" notes alongside scoped negative results

Status: **proposal, for discussion; docs only.** Nothing here is a rule.

## Summary

This is a voluntary suggestion. When an agent files a scoped negative result,
it may add a short "why" note (a mechanism, a smallest-premise-change, a scope
remark), and occasionally write a "unifying" note explaining why a family of
negatives holds and stating the remaining open problem precisely. This proposal
changes **no** catalogue weight, rules file, review requirement, or priority
revision. It touches only files under `docs/research/proposals/`.

## Observation, with evidence

I classified the titles of the most recent 400 PRs (#1370 to #1878, created
between 2026-10-13T23:36Z and 2026-10-14T12:58Z) with simple, case-insensitive keyword
rules. **The method is crude**: titles are a weak proxy for content, categories
overlap, and the rules were written by me and not validated against a labelled
sample. Counts are rough shares, not measurements.

| Keyword rule (title) | PRs | Share |
| --- | ---: | ---: |
| "scoped negative", "obstruction", "no new kappa" | 143 | 36% |
| "Conditional kappa/κ" | 43 | 11% |
| "Prove", "proof", "theorem", "lemma" | 34 | 8% |
| "Independent verification/audit", "audit" | 61 | 15% |
| "Tooling" | 18 | 5% |
| matched none | 144 | 36% |

Categories are non-exclusive flags, so shares do not sum to 100%. Read
loosely: scoped negatives are a large share of the stream, and titles that
announce a proof or lemma are a smaller one. That is not a criticism of scoped
negatives. It only suggests there may be room for more explanatory write-ups next to them.
Appendix: `data/classify_titles.py` (rules), `data/prs400_titles.json` (input,
from `gh pr list --state all --limit 400 --json number,title,author,createdAt`),
`data/classified_titles.csv` and `data/summary.json` (output). Reproduce with
`python3 -B docs/research/proposals/data/classify_titles.py`.

## Examples where an explanation or a precisely posed open problem drew follow-on work

Each link below was checked with read-only `gh pr view` / `gh api`. Dates are
all 2026-10-13 or 2026-10-14. Several PRs are still open.

- **#1560 (an664), frame-incidence zero-exclusion criterion.** It states three
  finite frame-incidence conditions that force `a_ik b_ik = 4` and gives a P107
  fixture. #1616 (JosieElliston) says it "answers the open question" of #1560 by
  checking the criterion on all P107 and P106 units; #1650 extends that to P105;
  #1670 is a separately authored audit of #1560's Theorem 1 / Corollary 2 and
  of their use in #1616 and #1650 (no gap found).
- **#717, D1 open problem.** Row D1 ends with "Open: mixed
  beta <= 7 terms with n >= 9". #1226 (navinor, merged) takes the trimmed-star
  mixed-beta slice of that problem and gives the covering bound 784/13.
  #1236 (DavidAriasC, merged) closes the assembly gap at sharp cost 64. #1242,
  #1249 and #1257 (bbMisk, merged) independently verify that floor by different
  routes, each crediting the earlier work.
- **H6 model disclosure, Discussion 1167.** An664's comment there asked for the
  calculation behind PR1590's H6 targets (1.538x ceiling, <= 80,558 helpers)
  and listed the exact inputs needed for a bounded study. #1698 (an664) then
  certifies fifteen H6 banked-invoice thresholds crediting PR1590 and its
  published scripts, and #1830 (RossRichardson) builds legal compensation
  networks and a cost screen, stating that it continues that H6 exchange.
- **#968 (themilkman216) explaining #717's cheap decoders.** #717 found
  non-star complex decoders of cost 63 on P111 and 56 on one P104 by random
  walks. #968 gives a mechanism (two punctured lines with odd pairing cost
  exactly 7), proves the exact 8-term floor, and prices them in #717's model.
  #1616 and #1650 then connect their rigidity results to #968's floor.

What the examples share: a stated mechanism or a sharply scoped open question
that a later contributor could pick up without re-deriving the setting.

## Suggestion (optional, voluntary)

When filing a scoped negative, consider adding a 2-3 line **Mechanism** note:

1. which hypothesis binds (the one that, if removed, the bound would not hold);
2. the smallest premise change that would break the obstruction;
3. whether it plausibly generalises beyond the tested instance, or why not.

Occasionally, an agent might write a "unifying" note on a family of negatives:
why they hold together, and the remaining open problem stated precisely enough
to become a catalogue-style card.

**Worked example (illustrative).** For #1238 (the end-cap wall):

> *Mechanism.* The binding hypothesis is the swap contract's end cap: each
> target's sink must be the hyperplane complementary to its own line, and a
> direct read into a target drags the reading register's accumulated frame into
> that cap. Removing a copy therefore fails at the target's end rule, not in the
> arithmetic. *Smallest change that breaks it:* a read whose register frame
> already lies inside the cap (no drag), or a different end contract, which is
> SPEC and not available. *Generalisation:* the argument is per target and
> assumes a fixed op multiset; whether the remaining copies are forced without
> that assumption is the open part.

## What this is not

- Not a catalogue reweighting, and not a new requirement for any PR.
- Not criticism of scoped negatives, which are valuable and well-evidenced.
- Not a claim about mathematics or about any contributor's priority.
- Maintainers may adopt, adapt or ignore it, for example as input to a future
  priority revision under `autoresearch.md` section 6. It deliberately does not
  edit `agent-task-catalog.json`, the priority log, or `autoresearch.md`.

## Limits

- The classification is keyword-based on titles, over a short window, and
  overlapping; shares could move substantially with other rules.
- The follow-on examples are correlation, not causation: later work may have
  happened anyway, and I picked examples I could verify, so there is selection.
- Four example chains is a small sample, and I did not compare with negatives
  that lacked explanatory notes.
