# Validation

Environment: Linux x86_64, CPython 3.12.3, g++ 13.3.0; discovery was single-process and sequential. No Lean, Docker, GPU, full selected replay or concurrent artifact-regenerating suites were run.

Completed on 2026-10-23:

- `python3 -B research/independent-clifford-expansion/verify.py --write`: generated the exact full census and integer interval receipt. Authoring command only.
- `python3 -B scripts/research_package.py --package research/independent-clifford-expansion --check-only`: metadata and source pins pass.
- `python3 -B scripts/research_package.py --package research/independent-clifford-expansion`: `PASS_REGISTERED_RESEARCH_PACKAGE ... outcome=completed` after rerunning both actual complete censuses.
- `python3 -I -O -B research/independent-clifford-expansion/verify.py`: same exact mathematical receipt passes with Python assertions disabled.
- Exact censuses: 817,600 contracted and 18,641,280 uncontracted neighbors, 417 and 157 signed polynomials, zero invalid helper cases.
- All 153 tiny Lagrangians, 8,739 nonzero-axis images, 5,661 literal independent-axis pairs, 1,143 literal sequential compositions, three corruption controls and a positive rank descent calibration pass.
- Three final-source bounded discovery runs and all 1,960 accepted plateau moves are retained in DISCOVERY.json. Registered replay independently checks their final charts and complete paid/helper invoices. They found no profile improvement.

The first registered comparison exposed JSON integer-key normalization in the author's receipt comparison. It was corrected; the full registered and optimized commands above then passed. This was a serialization fix, with unchanged mathematical rank histograms.

The prepublication overlap refresh covered all 307 then-open PRs, 4,263 discussion records and the complete committed 6,824-record local inventory, with no coverage warnings. Relevant prior work is credited in README.md. Open/closed status and coverage are a snapshot, not scientific acceptance or proof of novelty. Canonical main advanced from the assignment base to 20a1e31bc6009b9b3f4d084bbaadc6350e34fcba; governing priorities, selected record and package inputs were unchanged.

Publication preflight also passed `check_research_commit.py --check-source-history`, including all 19 committed package/input files and ancestry of the pinned base. The official committed export and its integrity check passed. An isolated `python3 -I -B verify.py` replay from the read-only Git-free export reproduced the complete certificate. Export bundles are POSIX tar archives. Hosted CI remains a separate external result. No higher kappa, independent human acceptance, native supplier admission or full multiplication theorem is claimed.
