# Complete low-rank channel extension

This is a conditional frame-model construction of `Y <- Y + (G/2) X` on all 104 P104 ports. It does not implement the `I-G/2` side correction or establish an admitted multiplication supplier or any new kappa.

The original delivery certificate remains unchanged. The D and T matrices have the same set of 104 distinct support masks, though 96 individual rows have different masks. Relabel target rows by their exact support masks and replace survivor labels a_k with b_k. This gives the same 32-chain delivery schedule for T. Supply its queries directly at singleton b_k frames, eliminating the private-copy stage. Reverse the events, transpose each scalar elementary operation, and orthogonally complement every frame. This yields a gather word from source singleton frames to full frames and query frame zero to b_k-perp. Those rank-eight hyperplanes equal the original delivery's gather frames exactly. The construction checks this using the reconstructed nondegenerate binary pairing, not coordinatewise dot products.

The gather's 32 dirty carriers are restored. Its eight query outputs are `q_k + sum_s T[s,k] X_s`, with arbitrary initial q_k. Before gathering, subtract `(D/4)q` from Y at frame zero. Run the gather, then the unchanged dirty-delivery wrapper with every target coefficient divided by four. Finally, subtract `T^t X` from the query registers at the common full frame. The resulting target contribution is `D T^t X / 4 = G X / 2`; sources and all 72 arbitrary dirty helpers retain their input logical values through the prescribed transports.

Exact profile: `{1:1074,2:58,3:86,4:104,5:48,6:24,7:8,8:8}`; rank mass 2368. Boundary coverage is `104*8 + 104*8 + 72*9 = 2312`, leaving COPY56. There are 4058 events, 280 independent input columns, and scalar prefix row-L1 bound 106. The helper inventory is `{9:72}`: 32 gather carriers, 32 delivery carriers and eight query parents. This inventory is not a global owner-packing certificate.

The producer checks exact rational columns and nested frames. The separately implemented free-chart checker reconstructs G from the frozen roots and checks all 280 columns with 443 freely noncommuting chart symbols. Missing initial query compensation, missing final query cleanup and a wrong transport phase are rejected. Concrete Gaussian/Clifford realization, extended labels, native compiler admission, global hosting, recursive precision and full supplier verification remain open. Free-chart cancellation does not prove those properties.

## Open next questions

The next construction must merge an `I-G/2` side-correction word with these frame paths. Appending it after source completion is not automatically legal. A separately supplied identity transfer would add a substantial private-copy charge and is not a claimed improvement. Whole-word integration must count every new child and residual, then pass native replay and chronological owner allocation before any kappa claim.

Credits: Adam Gall's PR1940 schedule, Josie Elliston's PR1071 P104 fixture, Ali Romman's PR1125 chain work, and all notices in NOTICE.md remain applicable. This adjoint gather and composed low-rank experiment was prepared by Rohan Arun with substantial OpenAI Codex assistance. No novelty guarantee or independent human review is claimed.
