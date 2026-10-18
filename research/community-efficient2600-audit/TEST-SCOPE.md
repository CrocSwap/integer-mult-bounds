# Shared tooling validation scope

PR2958: complete replay-selection module, including three new public-CLI inventory failure/selection controls, baseline rejection and normal/optimized candidate passes.

PR2928: branch-filter semantics, unsupported patterns, complete small-fixture CLI, record and exit-code tests. The unchanged CurrentTree/Skeleton source-inventory suites require large historical selected inputs absent from the sparse review checkout. Two attempted full runs record setup errors as well as the expected branch regressions; they are not counted as valid baseline controls or passes. An attempted static input hydration stopped at its explicit 128 MiB export budget. No scientific replay ran. The focused run excludes only those unchanged live-inventory suites and explicitly tests the installed selected workflow filters separately. No all-source or full multiplication replay is claimed.
