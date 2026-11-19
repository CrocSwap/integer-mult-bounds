# Exact causal obstruction for the six paid pairs

Let $u$ be the earlier row increment relative to the old row evaluated on its actual stock. Let $v$ be the analogous later increment. Both are rational linear forms in the 1,289 public coordinates. The exact additive pulse columns are proportional across the protected observations. Preserving one observation where those columns are nonzero forces $v=ru$, with the nonzero ratio $r$ in the table. Slot 95914 feeds only the old outlet 88. The old outlet reaches only chart-127 terminals, so removing those two old legs does not contribute to any protected observation or relevant producer stock. [Scope, pairs and reproduction](README.md) · [Exact result](STOCK.json)

The later producer's stock atoms are $b_i+t_i u$, where $b_i$ are their original forms and $t_i$ is the earlier pulse on each atom. This dependence is nonzero for all six pairs. For `95982/98182` the earlier edit reaches the later producer through the retained arrival `98175`. If the later row is changed by local coefficients $\beta_i$, then

$$
\left(r-\sum_i\beta_i t_i\right)u=\sum_i\beta_i b_i.
$$

The checker expands the original $b_i$ and proves their independence over the rationals. A zero prefactor would force all $\beta_i=0$, inconsistent with $r\ne0$. Thus the earlier increment belongs to the original later-stock span even when the later producer reads a modified arrival.

For four pairs, all $b_i$ vanish on the exact witness so both increments vanish there. For `88919/95502` and `88952/95503`, the combined pulse instead vanishes identically on all ten direct-sender stock atoms. Both routes leave those atoms zero at the witness. The 901 retained receiver arrivals also remain zero. Receiver 127 has no public input stock or paid egress. The new arrival is a rational form of the ten zero direct-sender atoms, so the collapsed program returns zero at terminal `155442`. The literal word returns one.

The replay checks an omitted later correction and a reversed later sign for each pair. Omitting input coordinate 1288 changes the direct-sender stock. The pair-specific recoding controls preserve all 1,288 protected observations with nonzero earlier increments `2645/4736` and `−565/14208` for `88919/95502` and `88952/95503`, respectively. Both recodings still lose terminal `155442` after the collapse. [Portable verifier](verify_stock.py)
