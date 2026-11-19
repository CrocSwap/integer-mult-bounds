Apache-2.0 (see `LICENSE`). Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.

The object of study is other people's work: the P104 native graph and 2048-call caller block of PR #7761, the
48-call caller block of PR #7786 (both by Clear1nsight), and the PRs they build on (see the CREDITS.md files in those
PRs). This package states and proves facts ABOUT those constructions; it does not replace or endorse them.
#7761's graph data is not redistributed here: it is identified by its graph sha256 and rebuilt from #7761's posted
files by our own `lean/tools/bridgegen/apply.py` (as in #7783). From #7786 only the `caller` object of its
`evidence/application.json` (file sha256 `88486d49f2ba1fc0e6c9f4a7402c82e91c44026cf90cd1387d1e5c45cf5e88d3`) is
copied, verbatim, to `lean/tools/callergen/app7786-caller.json`; #7786's graph is not used.
The Lean sources, generators and checks are new; toolchain and Mathlib pin are those of the earlier Lean packages.
