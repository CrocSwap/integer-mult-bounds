# Comparison with the pinned #7869 thin LP

At [#7869, `06c207a9feb3994a4b987dc3010657b6e85b7956`](https://github.com/CrocSwap/integer-mult-bounds/commit/06c207a9feb3994a4b987dc3010657b6e85b7956),
the `q1_k76.json` dual and `verify_q1.py` give the **modeled** bound

\[
\widehat c\le
\frac{49715125551675529173873011821938159}
     {385365782469381738054997774434304}
=129.007628111417802187\ldots.
\]

The certificate is a weak-duality upper bound, above `128.891` by about
`0.116628111418`. It is not a feasible-caller witness and does not prove the
LP optimum is above the bar. The JSON's `129.00694680218533` is a stored
floating-point optimum estimate; it is not the certified upper endpoint.
The verifier reports `leafshift` for this certificate.

The shipped [independent wrapper](replay_upstream_q1.py) runs the unchanged
upstream verifier for `k=76` and compares all 152 target/piece power bounds
with independently computed integer 100th-root enclosures at scale `2^110`.
It confirms the exact fraction above. This audits those finite power
roundings and the verifier's result; it does **not** prove the paper LP rows,
the frame-to-configuration bridge, or legal-word realization. The #7869
notes themselves say that the relevant `Q>=1` bridge and TRIPLE row are
not wired into one Lean theorem.

The objective is `104/k` times `2k-2 + sum (roleVal-1)` for integer role
partitions. The rows include main singleton incidences, DEEP, SET-RC2 for
`c<=3`, role count, LEAFAVG, leaf channel (LC), and TRIPLE-in-class. The
type LP does not impose this packet's two globally supported singleton hubs,
exactly 76 leaves and 73 other nonleaves, or the existence of a split role.
The existence of a global role-piece event assignment is a separate stronger
hypothesis in this packet, beyond ordinary stagewise `CallerEv.Match`; do
not infer that assignment merely from the fact that the LP enumerates integer
partitions.

At `e=0`, the #7869 aggregate triple row reads

\[
\sum_r\left[\binom{D_r}{3}+\binom{D_r}{2}(76-D_r)\right]
 \ge 3\binom{76}{3}.
\]

Under the two-hub assumption, each hub contributes one count to every
triple; the remaining role contribution can come from a role meeting the
triple in **two or three** stages. The common-piece cut in [PROOF.md](PROOF.md)
is a different conditional row. With one split degree-two role, it demands

\[
\sum_{r\ne\text{hubs}}\binom{D_r}{2}(76-D_r)
 \ge\binom{76}{3};
\]

only a role meeting the triple in **exactly two** stages contributes. The
rank-two sign obstruction eliminates a triple covered in all three stages
by other unsplit roles because their distinct full-event kernel vectors give
a common quotient. The degree-three and degree-four split cases allow the
explicit exceptional term `binom(d,3)`; no such term is needed when `d=2`.
Signature-cell fragmentation then adds further necessary constraints not
represented by that one averaged triple row. These statements are only
asserted under the packet's stated event-partition and frame hypotheses.

Finally, #7869's upper endpoint is for the **modeled** quantity. In the
`Q=T=1` type-B slice, #7852's exact identity adds the `IDLE_ODD` correction
to obtain `(104/76) repo`. If one combines the #7869 modeled bound with only
the generic 76-stage correction cap, the resulting outward real-invoice
upper is `129.105438967236`; it still does not cross `128.891`. The new
`128.879425704223` is an upper bound on the **corrected real invoice**, but
only for the substantially narrower split two-hub family. There is no
contradiction between the two statements, no proved legal caller of either
profile, and no claim here for zero-split or general callers.
