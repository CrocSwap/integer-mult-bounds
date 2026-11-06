# Independent analytic derivation draft

2026-11-06. Worker B. The derivation below was completed independently before receiving worker D's rank21 result; the write tool was aborted by delivery of that result. No worker D fixture or derivation has been read at the time of this sealing.

Take the selected query columns (0,1,3,4) as basis for n=4. Their Gram is K=(sign(i-j)) on four q-blocks, invertible; K^-1 has scalar rows (0,1,-1,1),(-1,0,1,-1),(1,-1,0,1),(-1,1,-1,0).

A<=B and D<=C may be assumed by replacing endpoint stages A,D by AB,CD. B contains queries 0,1 and C contains queries 3,4 from actual prefix compatibility. Thus B union C=I. The joint B-only and C-only sectors are supported, in M=K P coordinates, on pairs01 and23 respectively. Any B-only sector not carrying A is supported on singleton query1, and vanishes because the corresponding K^-1 diagonal block is zero. Likewise C-only must carry D. Thus the possible nonzero sectors are AB,BC,CD,ABC,BCD,ABCD.

For a two-query sector matrix M on an adjacent pair, M J M=M where J=[[0,I],[-I,0]]. Set its ordinary projection P=M J. (Order corrected during verification.) For low-cost sectors AB,BC,CD denote P_X,P_Y,P_Z. The adjacent cross maps are F=[[0,-I],[I,-I]], satisfying F^3=I. Set P=P_X, Q=F P_Y F^-1, R=F^2 P_Z F^-2. Their orthogonality constraints become PQ=QP=QR=RQ=0 and P N R=0, R(I-N)P=0, where N=[[I,0],[I,0]] is rank-q idempotent. Conversely those identities reconstruct three orthogonal sector projections in the full4q-dimensional query space.

The two-sector bound: for M_X,M_Z, put v=(I,-I)^T. Their cross contractions imply rank(M_X v)+rank(v^T M_Z)<=q and rank(M_Z v)+rank(v^T M_X)<=q. Since M=M J M and J is the sum of two rank-q cross terms using v and a complement, rank(M)<=rank(Mv)+rank(v^TM). Hence rankX+rankZ<=2q, and rankB+rankC>=6q.

The analogous three-sector rank bound <=2q is false as an abstract reduced projection system. At q=2, let Q=diag(0,0,0,1), P=diag(1,1,0,0), and R have top-left3x3 block [[1,1,-1],[0,1,0],[0,1,0]] and zero fourth row/column. Let N have rows [[0,0,0,0],[0,1,-1,-1],[-1,0,0,-1],[1,0,0,1]]. Then N is rank2 idempotent, P,Q,R have ranks2,1,2, and all reduced identities hold. Conjugating N to the displayed standard idempotent gives candidate low sectors of total rank5. The remaining common sector has rank3. To lift to total stage rank21, need the CD sector's last diagonal Gram block invertible, allowing a rank2 endpoint-D projector in the rank3 complement. This last condition was not checked before receipt of D's successful witness.
