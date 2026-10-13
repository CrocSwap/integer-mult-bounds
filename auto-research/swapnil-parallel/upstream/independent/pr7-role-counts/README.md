# Independent recount of PR #7's role counts

This is an independent re-implementation, written from the construction note of
CrocSwap/integer-mult-bounds PR #7. It recounts the bit-producer and complex-producer roles
that our witness assumes. No code from that PR is executed.

```sh
python3 export.py 26 /tmp/local26.txt          # local paired degree-three producer, n = h - 2
clang++ -O2 -std=c++17 global.cpp -o /tmp/global
/tmp/global 28 /tmp/local26.txt                 # merging, star resynthesis, rebuild check (~1 GB)
python3 complexside.py 28                       # complex producer
python3 local.py 8 10 12                        # exact small-h support checks
```

Expected values: 11240978 merged additions, 10857762 final additions, 983178 output uses,
11840940 bit roles; and 61022 additions plus 32816 injections, giving 93838 complex roles.
These match PR #7's certificate.
