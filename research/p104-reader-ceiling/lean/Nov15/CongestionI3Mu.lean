import Nov15.CongestionI3Data

/-!
Per-chain flag-DP minima mu[i][k] (config i of `cfgs`, chain k): the minimum, over complete flags <z'_k> < ... < z_k^perp, of the number of
FORCED unique cells of chain k (F1 f1dp.py `flagdp(zp, z, cu)`).  DATA from internal notes,b}.log (a rerun of f1dp.py with per-chain
printing; per-config sums reproduce f1dp.log: 1936 each).  Python exact DP over the 29k-subspace lattice; NOT kernel-checked.
-/
namespace CongestionI3
def muTab : List (List ℕ) := [[242, 242, 242, 242, 242, 242, 242, 242], [242, 242, 242, 242, 242, 242, 242, 242], [242, 242, 242, 242, 242, 242, 242, 242], [242, 242, 242, 242, 242, 242, 242, 242], [242, 242, 242, 242, 242, 242, 242, 242], [242, 242, 242, 242, 242, 242, 242, 242], [242, 242, 242, 242, 242, 242, 242, 242], [242, 242, 242, 242, 242, 242, 242, 242]]
end CongestionI3
