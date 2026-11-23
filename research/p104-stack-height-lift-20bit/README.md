# Stacked retune at the largest 20-bit Gaussian height (enlarged budget)

Label: **gamed** (resource tradeoff: lifts the self-imposed recurring cap 318292011, like #8078).

Stack: floor retune (L = 4474, suffix 186/25, #8080) + #8076 child tariff 2401/1024 (clock base 1740, entry 17→22) + #8082 ordinary reserve drop (no 256/255) and Gaussian debit 1039017/2^23. Ordinary debit 1420718/2^20 (directed log2F·2^20 = 1420717.197). G = 2^20 − 1 = 1048575, minimal ordinary heights (8192, 36093, 570250).

- Conditional **κ = 0.003898348449639**: +8.450e-9 over #8078 (0.00389834), +1.180e-7 over #8082 (0.003898230327195).
- log2 C 427339440, entry conversion 746, log2 B 196651337, funding floors (537891, 1048575), binary cuts (8290, 44447, 614761).
- Controls as in p104-height-lift-20bit, plus every parent ordinary booking fails the stacked allowance.

The reserve drop is a reading of #8042's written proof (see #8082), not an executable check.
