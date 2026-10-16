# T37 whole-owner packing on PR1148's three-demotion k8 word

Conditional **κ = 0.001675129371412064** (complex side binds; PR589 bit supplier unchanged).

> **Outdated, recorded for completeness.** This was built on PR1148's head `98235a9c` (three demotions, T16 owners, κ 0.001675121647789207). It is +7.72e-9 over that head. PR1148 was later updated to joint entrances (0.001675560947524449), and rohanarun's PR1169 put T37 owners on the new word. Higher results now exist (see PR1193, PR1218, PR1280). No record is claimed.

## What it is
- **Word:** PR1148's three-demotion k8 word (tomdif), helper inventory `{4:44,5:44,7:38,8:114,9:240}`, unchanged.
- **Owners:** a literal T37 owner map (159,840 roles, 333 calls) reaching the all-replica relaxed optimum with idle `{1:834, 48:11374}`, under the 1024-bit charged prefix of PR942/PR962.
  - PR1129's nine-pattern chronology basis is infeasible for this inventory, which has 12 more width-5 helpers per call.
  - The flow was found with an LP over all 20 tight patterns, then a MILP restricted to the LP support (`PATTERN-FLOW.json`, `SEARCH.json`).
- **Code:** the package code and controls are PR1157/PR1129's `r480-owner-optimum` T37 machinery, retargeted to this word.
  - `README-TEMPLATE-PR1157.md` and `PROOF.md` are that template's documentation. The method is the same, but their numbers refer to PR1157's word, not this one.

## Verification
```sh
python3.11 -B research/k8-three-demotions-t37/check.py --work /new/dir
# PASS_K8_THREE_DEMOTIONS_T37_ALL_REPLICA_OPTIMUM_AND_ATTAINING_CONSTRUCTION 0.001675129371412064
```
The strict check covers the all-replica bound with its 18 controls, the literal owner construction, the independent owner audit, and the finite invoice and outer assembly.

## Credits
tomdif (PR1148, word); aliromman (PR1129, T37 owner optimum and admission code); rohanarun (PR1157 template, PR1169); chafreaky (PR795 dual, PR1131/PR1152); jon314159 (PR942); and the lineage credited in `NOTICE.md`. Prepared with Claude Opus 5.5 (Anthropic) via Claude Code, directed by Joel Pulikkan (GamingPuzzled).
