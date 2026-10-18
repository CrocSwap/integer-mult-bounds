# Target-feedback cleanup audit

Raw endpoint independence is insufficient to replace PR543's prohibition
on targets feeding source/helper gates. The shortest three-wire failure
uses three raw ADDs: `h += y; y += x; h += y`. It reaches `(x,h+x,y+x)`;
its prescribed two-ADD cleanup cancels itself, leaving the helper wrong.
The source lemma under its actual H1/H3 target exclusion remains valid.

The audit derives four necessary and sufficient block equations and
checks the complete three-wire quotient for words of **any length**:
4,032 states, 24,192 transitions, 144 states satisfying the proposed
endpoint premise, of which 138 fail restoration. Both missing cleanup
equations have separate near-miss witnesses. All 43 shorter literal
programs are checked independently, proving the three-ADD minimum in
this class. Direct truth tables check every quotient representative.

```text
python research/feedback-cleanup-audit-seed72/verify.py
python -I -O -B research/feedback-cleanup-audit-seed72/verify.py
```

Expected:

```text
PASS_FEEDBACK_CLEANUP_AUDIT_S72 states=4032 naive=144 bad=138 minimum=3 selected_columns=661 controls=8
```

Python 3.10+ and the standard library suffice. The deterministic certificate
includes the smallest witness, exact counts, all equation modes, source
pins, selected-word block digests and eight rejection controls. `--write`
deliberately regenerates that receipt. No mutable frontier pointer is used
as a runtime dependency.

The proposed relaxation removes target exclusion from both H1 and its
repeated restriction in H3, and retains only H4's scalar projected-reverse
rule. It does not retain the original full-frame legality conclusion.
The counterexample is an algebraic interface example, not a legal E8
frame circuit. An independent scalar replay of unchanged PR589, selected
at the frozen experiment base,
checks all 661 arbitrary input columns and passes all four block equations.
The proof does not claim source lattice/frame, COPY-rank, precision,
native, hosting or outer assembly admission. No new supplier or kappa.

See PROOF.md, SOURCES.json, OVERLAP.json and VALIDATION.md. Prepared for
@woklerx with substantial OpenAI Codex assistance, Apache-2.0. Credit
eumemic's PR543 interleaved lemma, Zhihao Chen's PR425 predecessor, and
DreamingOfClouds's selected PR589 word on PR555; see NOTICE.md.

Frontier context is base-scoped: this worktree's PR942 selection has
kappa `1661960547713947/10^18`. During final verification the coordinator
reported live upstream `ba82555c64e1879e4b7decce28186f208fcb8262` selecting
PR1042 at `1672188119205421/10^18`. That newer selection is not audited here
and does not replace the pinned baseline used in this experiment.
