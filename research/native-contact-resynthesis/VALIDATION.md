# Validation and freshness

Author-checked on 2026-10-23 with CPython 3.12.3, Linux x86_64.
The scientific input is pinned at base
`b91956876e5b4122fd89179f1b57557ff8378f15`. Before submission canonical main
was fetched and this isolated branch fast-forwarded to
`bee95ce88` (full object recorded by Git). AGENTS.md, autoresearch.md,
CONTRIBUTING.md, priorities, catalogue, selected result and the frozen
round-three input were unchanged across that update.

Completed on the submitted scientific bytes:

```sh
python3 -I -W error -B research/native-contact-resynthesis/verify.py
python3 -O -I -W error -B research/native-contact-resynthesis/verify.py
python3 -B scripts/research_package.py --package research/native-contact-resynthesis --check-only
python3 -B scripts/research_package.py --package research/native-contact-resynthesis
```

The standalone runs and registered replay return
`PASS_EXACT_PRELUDE_MAIN_ENDPOINT_CAPS_NO_NEW_KAPPA`. They check all 24 output
caps and 384 actual forward/backward paths, each source containment as a
positive fixture, two exact intersection engines and five rejecting controls.
Metadata/pins return `PASS_PACKAGE_METADATA_AND_PINS`; the launcher returns
`PASS_REGISTERED_RESEARCH_PACKAGE`.

The selected-baseline binding helper also passed; it is metadata orientation,
not a fresh scientific replay. No unrelated historical suite, native phase
replay, Lean build, full compiler or outer transfer was executed.

Overlap search at 05:43:56 UTC covered 6,636 local notes at the pinned base,
300 open PRs and 4,086 Discussion records, with complete reported pagination
and no warning. The source round-three README, its independent audit,
PR4919's general shared-map handoff, Discussion4840's different local native
application, and the live round-three contact-rewrite claim were read.
No matching source-bound early-line path certificate was found in that
coverage. Arbitrary code diffs and unpublished work were not searched.

Committed-byte/source-history and export checks run after the scientific
commit are reported separately in the PR. Hosted CI is not represented by
these local checks. No independent human or formal-kernel review is claimed.
