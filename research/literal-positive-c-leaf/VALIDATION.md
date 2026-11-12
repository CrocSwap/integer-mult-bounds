# Executed validation

Completed on 2026-11-12T04:11:07.837895+00:00 with Python 3.12.14.
C++ compiler: c++ (Debian 14.2.0-19) 14.2.0; compiled with -std=c++17 -O2.

All eight commands in VERIFY.json were executed successfully. The three author
normal/optimized structured output pairs are byte-identical. Both relocated
independent commands reproduce their saved structured receipts exactly.

```sh
python -I -W error -B bind_source.py
python -I -W error -O -B bind_source.py
python -I -W error -B check.py
python -I -W error -O -B check.py
python -I -W error -B check_big.py
python -I -W error -O -B check_big.py
python -I -W error -B independent/dense_check.py leaf.py
python -I -W error -B independent/peer/check.py .
```

## Exact receipts

- RESULT.json: SHA256 `ddae895317a1df60b94959694052b34a881763de4112f57a0efe4be01dd9bf1e`.
- SOURCE-GATE.json: SHA256 `66b0d2dcca39275434e2743b061aafe8b4968dec2440b6444c5058dc54f3b126`.
- BIG-RESULT.json: SHA256 `f499bde45dd018e991c480ebbc0d93a5d0a88495a438c7c099cf3dd5a1d4f3b8`.
- independent/DENSE-RESULT.json: SHA256 `fe3831e67a7db6ce9aca525d9ad02ff55e5751b9f12892d745b7afbb2782ae62`.
- independent/peer/RESULT.json: SHA256 `2c45ae6e55e35e5caabcabb21addae62fa1e9acf964f6128df71c1f107118826`.

## Coverage and limits

The author Python suite has seven complete m9 f1 successes (6,201,327 steps),
six rejections (908,755 steps), and three same-owner calls with retained private
history [42093,42093,42093]. Their step counts are [1305638,376628,1305638].
The cutoff fixture has 2049 encoded bits. All eleven source pins match.

The actual fixed m9 f2 table executes the entire 262,144-address, 2,621,440-bit
packet in 704,382,528 steps. Full output, public write counts, all heads, private
blankness, header and opaque exteriors match the direct tensor oracle. The
first-axis-only mutant executes 401,212,870 steps and is detected despite
normal retirement. The complete endpoint-only f2 fixture rejects in 36,898,051
steps with zero DATA writes; dirty private state is intentionally recorded.

The C++ interpreter checks its f1 count against the original interpreter. Its
run times in BIG-TIMING.txt are environment observations, not model costs or
complexity improvements. No reduced dimension replaces the author full f2 run.

The root uses separate full m9 f1 and explicitly smaller fixed-dimension
fixtures; its receipt does not claim a complete actual m9 f2 success. The peer
uses separate source/spectral proofs and isolated component/axis cost slices.
All independent artifacts are unchanged and their scopes are preserved.

No full MOVE, current old-codec/placement producer, nonleaf tariff, selected
cold replay, global-assumption discharge, human or proof-kernel acceptance
is claimed. See PROOF.md and REVIEW.md for the exact remaining obligations.
