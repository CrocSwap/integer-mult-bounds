# Exact cover action for the QQ16 native components

This note fixes the representation of each alignment map used in
QQ16-NATIVE-COMPONENT.md and QQ16-CONSERVED-COMPONENT.md. Their
scalar formulas, native phases, line recipes and counts are unchanged.
The symbol P_rho in their alignment notation means the cover route
defined here. It must not be implemented as a payload permutation
within one fixed cover array.

Let d be a cover element, p a port, and z_1,...,z_lambda the physical
payload addresses. Different cover positions contain independent
arbitrary arrays. For a binary orthogonal g and binary vector delta,
define the combined array view

    (M_(g,delta)f)_p(d,z_1,...,z_lambda)
      =f_p(dg,z_1+d delta,...,z_lambda+d delta).      (1)

Each addition in (1) is binary XOR. All compact and other spectator
coordinates stay unchanged. The map has no amplitude phase. It
changes both the cover-owner index and the payload translation. It
does not apply g to the payload addresses. The exact composition is

    M_(g,a) M_(h,b)=M_(gh,a+gb),
    M_(g,a)^-1=M_(g^-1,g^-1a).                    (2)

Use the actual rho_v(p) and beta_p from the pinned native chart.
At a Y boundary before v, the alignment in both component notes is

    A_v(p)=M_(rho_v(p),p+lift_v(beta_p)).

At a completed X boundary at or after v it is

    A_v^X(p)=M_(rho_v(p),B_p beta_p+lift_v(beta_p)).

These are precisely A=ZD from sections 1--4 of the independently
checked interface-proof/BRIDGE-REVIEW.md. Here D changes the cover
index by right multiplication and Z translates the payload at its
new view position. The identity A T=T_common D proves that the
logical scalar word is conjugated by D, without an extra payload
operator. Its proof applies to arbitrary cover fields and tensor
powers; it does not restrict data to cover-invariant fields.

For a target p and source q in one chart, the relative path is

    A_v(p)^-1 A_v(q)
      =M_(rho_p rho_q, rho_p(delta_p+delta_q)).     (3)

The g and delta in (3) are exactly those used by the component phase
checker. That checker transports the source frame axes by g because
the source owner is dg. It does not certify a payload-only substitute
for (1). Such a substitute is false on arbitrary independent cover
inputs, even if it has the same binary frame calculation.

The map counts in the component invoices count one combined
bijection (1) as one map, and count its inverse separately. They do
not say that computing a cover product or a tensor translation is
free. The complete supplier must price their physical realization.
For each fixed port, d to dg is a bijection. A common-frame scalar
word can therefore use these views without merging independent
owners or copying a complete extra bank. A full emitted word must
still record the cover action, phase correction, source reads,
target writes, and all helper-owner conflicts.

The binding source pins are:

    interface-proof/BRIDGE-REVIEW.md
    d01b5f4959f7c91f835496d050dfae3eeab9dee2f581571c316a42571eaa1cd3

    interface-proof/BRIDGE-OPERATOR-REVIEW.json
    c905a19d70f34c435c5f5454c6190bbfb1ce4594b1513bf76156acf620d7c6fc

The latter review checks all 1008 actual entry/exit recipes and
32256 selected data owner routes. This note uses that result; it
does not repeat the owner audit. An earlier informal schema message
gave a payload-only interpretation. Equation (1) replaces that
message before native word emission.
