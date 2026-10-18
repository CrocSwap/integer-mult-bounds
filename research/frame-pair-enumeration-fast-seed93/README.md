# Faster exact frame-pair enumeration

Precomputed eight-bit neighborhoods accelerate PR968's complete frame-split
search while preserving every ordered solution and its existing exact checks.
On the recorded Windows CPython run, the enumeration median is **4.57x faster**;
the larger D/E/H replay is **2.97x faster** in a separate single paired timing.
Timings depend on the machine and load; correctness has no timing threshold.
See [BENCHMARK.json](BENCHMARK.json) for all three alternating kernel trials,
environment details, raw seconds and the broader timing.

The complete input has 1,260 second frames, 896 with eight solutions and
364 without solutions, yielding 7,168 exact decoders. The default verifier
runs both the pinned reference and candidate through unchanged source
sections D/E/H. It compares complete ordered solution streams, 57,344 exact
term ranks, every source check/log line, all 25 attainment cases and six
inherited rejection controls. Ten additional package controls pass, including
checking that source assertions survive an optimized caller.

```sh
python -I -O -B research/frame-pair-enumeration-fast-seed93/verify.py
```

Expected:

```text
PASS_FRAME_PAIR_FAST_S93 frames=1260 decoders=7168 term_ranks=57344 chain=25 inherited_controls=6 package_controls=10
```

Python 3.10+ and the standard library suffice. `--benchmark` reruns three
alternating kernel trials and replaces only the local timing artifact;
`--record` deliberately regenerates the exact certificate. Default execution
does not rewrite either artifact. It compiles the pinned source in memory
with its assertions enabled, without editing the predecessor package.

[PROOF.md](PROOF.md) gives the order-preservation argument.
[SOURCES.json](SOURCES.json) binds the exact consumed source after declared
CRLF normalization. [CERTIFICATE.json](CERTIFICATE.json) records all canonical
proof-relevant fields. The original selected construction is unchanged.

This is an optional research wrapper, not installation into the upstream
verifier or a measured whole-repository speedup. We did not replay sections
A/B/C/F/G, native suppliers, hosted CI or the all-size multiplication theorem.
All PR968 mathematical assumptions and all selected supplier obligations
remain. No new circuit, lower bound or kappa is claimed.

Prepared for @woklerx with substantial OpenAI Codex assistance. Apache-2.0.
Credit themilkman216 for PR968's exact enumeration and all inherited
geometric/rank checks. See [NOTICE.md](NOTICE.md), [CLAIM.json](CLAIM.json)
and [VALIDATION.md](VALIDATION.md).
