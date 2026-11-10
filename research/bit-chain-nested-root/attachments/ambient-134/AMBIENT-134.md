# Added proof note: actual 134-axis geometry for BIT saving 0.00385248

**No claim changes.** This note adds a finite comparison for the conservative working geometry of `research/bit-chain-nested-root`. The saving, tested value, caller and invoice are unchanged.

The committed certificate passes the largest target to the compiler, so its record states `ambient: 127^768` and log power 610, and `verify.py` uses `h=127` in its route charge. All 18 stages keep separate seven-axis blocks beside the eight-axis native interface, so the conservative working geometry has A0=8+18·7=134 axes, while the largest target stays 127. The same substitution was identified and repaired for the #6726 source in #6916's BIT audit; that repair does not transfer between sources, so it is done here for this one.

At A=134^768, tested 0.0038525, theta 42/43, `ambient134_check.py` proves by exact arithmetic:

* the exit comparison 2·15^(768·43)<=134^(768·42);
* log power **617** replaces 610, with j=29663 and H=296630000000000, and (H+1)^617<2^j, while the preceding grid point fails;
* routes 285684·8·(10·134²+10·134)=413441884800, plus visible 182425128, total 413624309928<10^12;
* owned bank 3051882<10^7, unchanged;
* ordinary completion from the canonically admitted saving 0.0034, with atom 1/250: 0.0034 -> 0.00385 -> 0.00385248, so the earlier 0.00374998 step is not needed.

The tail inequalities at power 768, cutoff 15, floor 16 do not depend on the ambient and are unchanged. Controls reproduce the committed power 610 and the published 596 and 603 of the #6726 source.

**Limits.** This uses the ambient-cap lemma of open #6916, whose review scope excludes other sources. The lemma's hypotheses for this source are the same completed-job, spectator, adapter and chronological premises already retained. The delayed-cover exclusion list for this caller's compiled word is finite for the same reason, but is not enumerated here. This remains conditional on the five retained framework assumptions and on the native word of #6726.


Reproduce: `python3.12 -I -B research/bit-chain-nested-root/attachments/ambient-134/ambient134_check.py`, expected `PASS_AMBIENT_134_FOR_BIT_CHAIN_NESTED_ROOT`.

Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.
