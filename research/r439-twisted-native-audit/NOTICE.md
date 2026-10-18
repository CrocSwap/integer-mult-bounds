# Attribution and license

Hanson Sun (@bbMisk), with substantial OpenAI Codex assistance in implementation,
verification and writing. One agent; no independent human review. New work is
Apache-2.0 under the repository license.

Sagar Thakrar's PR1868 supplies the twisted helper contract, three absorption
moves, both candidate words and their three-ADD savings. Its README and proof,
with the original author/AI/license notices, are retained unchanged in
`vendor/pr1868/`. PREDECESSOR.json pins their exact origin. The present package
claims only the native replay and its supporting verification work.

The parents are Sagar Thakrar's PR1062 and Gareth Davidson's PR1188. Their
lineage includes Davidson's PR1122/980/952/915/926, Sricharan Vagvala's PR967,
Aaron Wang's PR1015, Ross Richardson's PR923, and DreamingOfClouds's PR589 on
eumemic's PR555/543. The semantic interface work of woklerx/PR1194 and Arham
Tahir/PR1311 remains separately credited.

The native compile/staging conventions follow Davidson's PR1122/1188 harnesses,
which credit Sagar Thakrar/PR837 and Sricharan Vagvala/PR967. The unchanged
exporter and C++ programs retain the notices of Dylan Crow, DaysSky, Zhihao
Chen and the PR249/266/315/496/527 checker lineage. The pinned nlohmann JSON
header retains its own MIT license. Boost is an external build dependency
under the Boost Software License; it is not vendored here.
