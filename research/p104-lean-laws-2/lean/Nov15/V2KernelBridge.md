# V2KernelBridge (LEAN-NEXT32, Nov 17)
Kernel-only helper-D0 floors: V2FloorKernel_j/_b covers composed with V2Bridge (bridge, bridge_0V, bridge_beta_V).
- v2kernel_helperD0_joint: 987754236107/2^30 (919.92) <= helperD0 + sum_h hcorr (79793/2^20) (instantiated at the kernel's theta; bridge holds for any theta in [0,1]).
- v2kernel_helperD0_joint_0V: 919.92 <= helperD0 when every helper is 0 -> 9.
- v2kernel_helperD0_beta: 941971821916/2^30 (877.28) <= helperD0 + sum_h hcorr 1.
- v2kernel_helperD0_beta_V: 877.28 <= helperD0 + B1 * #line-born helpers, helpers ending at V.
No IntFeasible hypothesis. Remaining hypothesis: hreal (Reach (relayE ...) (Lsub (LBj p)) (Usub (UHj p)) for all p : Fin N_joint / N_beta), the same object as in V2BridgeFinal (same V2FloorData pair list, Sub/Lsub/Usub/Reach/wcut; no adapter needed). It is a named data hypothesis (r7-taint extraction), not a consequence of class K.
Axioms (checked): propext, Classical.choice, Quot.sound. Compiles in 8 s, 2.4 GB peak via runlean.sh.
