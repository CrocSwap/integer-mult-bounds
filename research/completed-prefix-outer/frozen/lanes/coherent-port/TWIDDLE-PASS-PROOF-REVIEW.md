# Bounded review of the twiddle pass proofs

The proofs in `../temporal-reuse/TWIDDLE-PASS-COST.md` and
`../temporal-reuse/ACCUMULATED-TWIDDLE-CODE.md` pass in their stated
implementation models. The receipt pins the reviewed bytes.

The separate-round proof uses a legal tail value with `t^2=-1`.
The ordered conjugate of `diag(1,t)` has four nonzero entries. The
products `(1+t)(1-t)=2` show that none can be lost through a zero
divisor. Independent tensor choices give `2^f` input dependencies.
A pointwise binary ADD can at most double the support on one path.
Thus f depths are required when each depth is a complete-stream pass.
The cost conclusion uses the stated outer size relations and the
requirement to transport each round separately.

The complete-word proof retains the order `J E H0`. The current code
does not move past its own twiddle. For an odd port q, the two native
branches `C_all C_q` and `C_all C_q^-1` conjugate `Z_q` to opposite
signs of itself. The signs are preserve/flip for actual weights three
and seven. Diagonal twiddles preserve these parity classes. Later
rounds use other offsets, so the whole encoded word permutes the joint
parity classes and acts invertibly in each block.

Each raw FFT output row has a nonzero restriction to every relevant
input parity block. Right multiplication by an invertible block cannot
turn such a row into zero. This gives the stated complete-word
`2^(f*l)` support bound. It yields the full-pass cost conclusion but
does not give a lower bound for recursive or unequal-volume native
subcalls.

The reported ten-entry finite decoder cannot be one native C tensor
between native or scalar monomial maps: such maps preserve scalar row
support, and a native tensor has a power-of-two row support. This
review checks that implication. It does not repeat the source's
256-column finite calculation. An arbitrary real two-by-two map on
each complex coefficient is outside that monomial-wrapper statement.

`review_twiddle_pass_proofs.py` performs an independent exact check in
the ring with distinct generators `i^2=t^2=-1`. It checks the
two-point conjugate, both native inverse orders, unit products, both
Pauli signs, and the parity signs for all odd weights through seven.
It imports no producer. It uses explicit failure checks under
optimized Python.

The review does not repeat the upstream source-layout audit, the
producer's finite matrix replay, or native decoder admission. The
quoted outer twiddle and size relations are premises of this bounded
proof review. No general decoder impossibility, recursive cost bound,
or new multiplication exponent is claimed.
