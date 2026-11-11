# Paid commutator rewrites of scalar words

Source: the OpenAI DukePrimeDegree root-coordinate proof. RootCommutator.adjacent_root_conjugation gives an exact three-root transvection identity; EliminationChain.param_val identifies the actual ordered product, and EliminationWordEntries.word_val_eq_sum_single gives the compatible triangular special case. These sources were inspected, not newly compiled. No ergodic or limiting argument is imported into a finite algorithm.

For three distinct registers a,b,c and rational q,r, replace the execution sequence

    a += q*b; b += r*c

by

    b += r*c; a += q*b; a -= q*r*c.

Substitution shows that both produce (a+q*b,b+r*c,c) from arbitrary initial values. Likewise, a+=q*b; c+=r*a equals c+=r*a; a+=q*b; c+=r*q*b. No zero-initialized helper is assumed. Dyadic coefficients remain dyadic under multiplication. The extra correction is an actual paid scalar gate.

If the original first and second gates have frames F contained in G, put all three replacement gates at G only when every preceding register frame lies inside G and every subsequent register frame still contains G. Recompute the entire frame chain and actual prefix envelope. When gates lie farther apart, move the first past intervening gates only if their elementary operators commute; our structural gate checks that neither target occurs as the other's source and handles scales conservatively. Then apply the same identity and retain every correction. An exact all-input and physical replay is required before claiming any accepted word.

For adjacent gates, let d_s and d_o be the dimensions of the shared and other first-gate registers beforehand; let f=dim(F), g=dim(G), and h the other register's next frame dimension. The old affected recursive costs at exponent a are

    (f-d_s)^a + (g-f)^a + (f-d_o)^a + (h-f)^a,

and the new costs are

    (g-d_s)^a + (g-d_o)^a + (h-g)^a,

omitting zero increments. Other registers' equal charges cancel. This gives a sufficient cost gate, but it is not assumed positive. A finite scan must also charge scalar precision and restoration.

On the checked pair35 provider, the adjacent scan found no improving legal window. A larger native C++ scan inspected up to 128 following events, respecting exact commutation, and evaluated603 complete candidate frame profiles. None passed its floating discovery-price gate. GF(2) frame legality was exact; the discovery price used ordinary floating arithmetic and is not a rational nonexistence certificate. No changed word or kappa gain is claimed from this route. This is a bounded test of a sufficient transformation, not a universal barrier.

The same native window test was then applied to the selected rank-sector provider: 547 full candidate profiles, no nominee passing the discovery cost gate. This follow-up is distinct from the 603-window pair35 screen above.
