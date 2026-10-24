# Attribution and retained sources

- The frozen raw invoice `INPUT.json` is `research/joint-helper-lattice/RESULT.json`
  from Cinna Davis / 1337isnot1337's PR4470 at
  `b9a13c1673e0e9697de410de16e8bbf3207a7363`. It is unchanged on checked main
  `b91956876e5b4122fd89179f1b57557ff8378f15`.
- The unchanged `upstream_moment.py` is zxv's
  `research/higher-moment-strictification/verify.py` on that main. Its source
  header and all original code remain intact. Only its arithmetic functions
  are invoked; the complete package's source and construction replay is not run.
- The construction retains zxv's native/controller/compiler work, Jacob Alan
  Sussman's mixed-target recursion, Cinna Davis's query-thinning and frame work,
  and the scalar, Clifford, geometry, precision and outer-ledger contributors
  credited by the upstream package and selected review.
- Aaron Wang / navinor's PR1669 and its handoff motivated the screening question.
  The new alternating-Taylor screen does not copy or execute its implementation.
- New experiment and documentation: SHIN09-git with substantial OpenAI Codex
  assistance. No independent human or proof-assistant review is claimed.

Sources retain Apache-2.0. See LICENSE and the exact paths, hashes and links in
SOURCES.json. The new work is also provided under Apache-2.0.
