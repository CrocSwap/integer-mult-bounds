# Fixed-dispatch packing ceiling

Keep PR643's 72 calls (71 U4 JP8, one ST2 JP8b), admitted supplier words,
complete helper roles, geometry, and finite-invoice convention fixed.
Every owner segment has integer capacity at most 48. After assigning every
required helper width once, total unused capacity is
106988 = 2228·48 + 44.

For 0 < q < 1, the idle contribution to the exact normalized moment is

    73^q / (73·7168) · Σ g^(1-q),

where g ranges over positive gaps. The fixed supplier contribution is
independent of the assignment. Strict concavity of x^(1-q), with f(0)=0,
means moving positive mass from a smaller positive gap into a larger gap
below 48 strictly reduces the sum. Repetition leaves at most one positive
gap below 48. Thus every feasible map has idle moment at least that of
2228 gaps of 48 and one gap of 44.

This is a relaxation: the transfers need not respect time windows or physical
families. A literal map attaining that gap profile attains the relaxation and
minimizes the moment for every q in (0,1) among maps with these fixed inputs.
The witness in this package is checked against actual native widths, all
35,424 roles, time windows and physical-family constraints.

All ranks are below 73, so the normalized moment increases strictly with q.
At q=0, rank mass 520704 is below 73·7168 = 523264. At q=1 the supplier
contribution alone is 260348/7168 > 1. The positive root therefore lies in
(0,1), and the κ conversion q/(1+q) is monotone. This packing maximizes the
moment-limited exponent ceiling for these fixed inputs; other admission
conditions remain separate. The decimal κ is an exactly certified lower
bound, not the exact root.

There are 16,128 owner segments of total capacity 387,072 and 280,084 required
helper-width units. This proof does not bound different suppliers, widths,
dispatch, scheduling geometry, or invoice conventions.
