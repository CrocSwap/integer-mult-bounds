# Validation receipt

Checked on Linux with Python 3.14.7 on 2026-10-13, from base
`f567884aeb8851b6e794af1184119a3bfbe1e631`.

* `python3 -I -B research/counter-reversal-audit/verify.py`: PASS;
  130,305 schedules, 16,376 literal executions, ten controls.
* `python3 -I -B -O research/counter-reversal-audit/verify.py`: identical PASS
  and exact match to every committed receipt field.
* `python3 -I -B research/counter-reversal-audit/test_audit.py`: six tests pass.
* `python3 -I -B -O research/counter-reversal-audit/test_audit.py`: six tests pass,
  including rejection of source drift in a separate optimized subprocess.
* `make selected-record-check machine-transfer-check`: PASS. The selected
  kappa stays `1661634653669567/10^18`; all 240 machine-transfer publication
  hashes and the offline checkpoint checks pass.
* `git diff --cached --check`: PASS before commit.

The initial draft proposed an additional false control: applying the positive-
width refined inequality at width zero. That control correctly failed because
that inequality is also an upper bound there. It was removed; the delivered
proof gives the sharper exact cost 2N at width zero, and the delivered control
rejects treating zero-width calls as free. The mathematical bound for positive
widths did not change. This was a failed test-design assumption, not a
counterexample to the new bound or the predecessor theorem.

No existing source or generator is modified. Repository-wide `make verify`,
the expensive selected supplier cold replay, and the Lean kernel were not run
for this isolated research addition. The offline machine-transfer check is
not a Lean rebuild or full finite supplier replay. No remote CI outcome is
claimed. No formal proof of the new statement or full multiplication theorem
is claimed.

The finite proof-relevant receipt is deterministic and excludes timings.
Source SHA256 and Git blob pins are in `SOURCES.json`; the completed domain,
seed and stopping rule are in `EXPECTED.json`. PR metadata and pinned issues
were refreshed before submission; `CLAIM.json` records that snapshot.
