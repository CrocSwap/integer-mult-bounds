# Five-shortcut Gaussian word with the stacked retune at 20-bit heights (enlarged budget)

Main author: floration. Label: **gamed** (resource tradeoff). It lifts the recurring cap 318292011, like #8078 and #8086.

- Base: p104-k7-shortcut-word, the five exact chart-3 relay shortcuts on #8027's rational word (5,669 transfers). It has Gaussian trial 17158764376/2^42 and Gaussian debit 1039776/2^23.
- Stacked ordinary side: floor retune (L = 4474, s = 186/25), #8076 child tariff 2401/1024 (clock base 1740), and no 256/255. Ordinary debit 1420718/2^20.
- With the new word the Gaussian side no longer binds. The ordinary side binds at its 20-bit ceiling. The prefix rule `cut[i-1]+2 < h[i]` with h3 = 2^20 − 1 fixes h2, and h1 is optimised over that.
- Profile: ordinary (62186, 986008, 1048575), Gaussian G = 66037, conditional **κ = 0.003899574328473**.
- That is +1.2259e-6 over #8086 (0.003898348449639), +1.3011e-6 over the capped shortcut-word package (0.003898273237647), and +1.2343e-6 over #8078.
- Resources: complete log2 C 685495960, entry conversion 973, log2 B 670966217, binary cuts (62500, 1048572, 2097211), funding floors (1047843, 66037).
- Official runner: all 7 scopes pass (`p104-shortcut-word-lift-20bit-official-replay.log`).
- Controls: h2−1, h3−1, G−1, the capped shortcut-word profile at the new rate, the inherited cap, the outer margin, the prefix at the previous cut, and the recurring bound minus one. Neighbouring h1 choices (±64) are lower.
- Open: the reserve-drop reading inherited from #8082, and the shortcut word's rational application (scalar compiler, chart-3 ordinary work), which is inherited from p104-k7-shortcut-word.
