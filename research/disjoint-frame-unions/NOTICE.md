# Attribution and license

This contribution is by Stephan Arrington (@steph4n-gh), with substantial
OpenAI Codex assistance in implementation, experiment design, testing,
mathematical explanation and packaging. A separately tasked Codex worker wrote
the breadth-first graph oracle and reviewed the adapter. This is not independent
human peer review. New material is under the repository's Apache-2.0 license.

The unchanged disjoint-tensor construction, original frame-data verifier,
phase checks, complete historical audit, and dirty-restoration tests are Douglas
R. Colkitt's work, preserved at source commit
`1a74950ce5074b848243ba89d8022fbadba66105`. Their precise base-source hashes are
in SOURCES.json. The adapter retains the original descendant and source-union
calculations and rectangle guard, replacing only target-union computation.

The opt-in source-admission, complete-certificate comparison and alternating
fresh-process benchmark follow Ross Richardson's incorporated PR950 package,
`research/central-factor-packed/`, credited for that reproducibility pattern.
No packed coefficient kernel is used here. Existing source notices and upstream
Apache-2.0 material are unmodified.

Concurrent PR863 by Curtis Dransfield and PR981 by @ToikY change root
contraction/traversal recipes for this historical supplier. They are related
construction research, not dependencies or this verifier optimization. Their
source pins are not imported or represented as reviewed by this contribution.
