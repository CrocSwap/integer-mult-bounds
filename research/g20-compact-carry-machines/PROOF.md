# Carry invariant and packet

For a released column a/d, d is 1 or 4. Let N=sum a_i x_i, with 0<=x_i<q and q odd. Put L=sum min(a_i,0), P=sum max(a_i,0), and U=max(0,P-1). Then L<=floor(N/q)<=U. For each integer j in [L+1,U], read the input least-significant row first and update

`c_j <- floor((c_j + sum a_i bit_i - j bit_q)/2)`, starting at zero.

After ell rows, c_j equals floor((N_low-j*q_low)/2^ell). This follows by induction using division with remainder. At the final row, c_j>=0 exactly when N>=j*q. Thus the quotient is L plus the number of nonnegative c_j. The source low-input checks use the same recurrence for each x_i-q; each comparison has only states -1 and 0. They reject x_i>=q after the final leading radix bit.

The first two input rows give N modulo d and q modulo d. For odd q and d=4, q is its own inverse modulo d. Let r=N*q modulo d. The unique carry c with N-c*q divisible by d and with 0<=(N-c*q)/d<q is

`c=u-((u-r) mod d)`, where `u=floor(N/q)`.

The packet is the five-bit encoding of `4c/d+16`. This is the retained PR6474 identity. The verifier binds every actual column and checks its packet envelope against a separate modular oracle.

# Complete finite table

The possible aggregate digits form the exact subset-sum set of a_i. The model alphabet contains each such digit and either radix bit. The producer enumerates states from the all-zero vector until every outgoing edge stays in the table. Finiteness also follows from the preserved bounds `L-max(j,0)<=c_j<=P-min(j,0)`. The checker verifies every edge by the defining floor inequalities and checks a path to every listed state through the enumeration order. Hence the table represents all finite aggregate streams, including a superset of the valid canonical inputs.

The initial partition groups states by quotient output. Each later partition groups states by their output and the prior class of every successor. The certificate records every partition. Its checker verifies both directions of this equivalence: equal observations have equal labels, and equal labels have equal observations. The last partition is stable.

By induction, the partition after k refinements identifies precisely the states with the same output after every word of length at most k. Distinct final classes therefore have a finite distinguishing word. Stability makes each class a bisimulation and proves that merged states have the same output for every continuation. Reachability plus these two facts proves minimality of each quotient component for its own unrestricted aggregate alphabet. The terminal packet and input validator have additional structure; this result makes no minimality claim for their composition.

# Packed execution and cost

Each quotient state uses ceil(log2 m) bits, where m is its model's compact state count. All output values use five bits with offset 16. Transition entries are packed at the exact index width; the one-state component needs zero transition bits. Metadata gives model dimensions and bit offsets. The checker compares every packed output and transition with the certified component before running any packet cases.

The largest m is 2406, so 12 quotient bits suffice. Eight input comparison bits, two numerator-residue bits, one high radix-residue bit, two phase bits and one final radix bit give a total of 26 retained bits. The first odd radix bit is implicit. Phase zero also records that no row has been read. These are representation counts, not a physical machine-space optimum.

All tables together use 3,718,922 significant bits, rounded to 464,866 bytes. The emitted metadata uses another 2,679 bytes. Each input row performs bounded aggregate-digit work and one packed transition lookup; output uses one five-bit lookup. A tape realization must charge address travel, input layout, scratch and cleanup. The Python indexed reader does not establish those costs. The paid recursive invoice and selected kappa are unchanged.
