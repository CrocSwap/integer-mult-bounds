# Actual carry descriptors from old low bits

This is a partial physical lowering of PR4989 helper462/frame506. It proves and implements the old-low-to-descriptor frontend on five tapes; it does not implement the complete payload low-type permutation or claim closure of the requested full route. N=8f and odd prime q are fixed compiler parameters, D=N², b=ceil(log2 q), w>=2, Q=q^(w-1), and L=bit_length(Q). All head movements in the emitted programs are single-cell moves. The alphabet is {blank,0,1,END,LEFT}. Program construction may perform exact integer arithmetic before inputs arrive; execution may not.

## A width-independent source coefficient set

Let A denote either the actual rational S8 or S8^-1, lifted by tensor I_f. For an output cell, select its eight old low entries u_j from one row and one tensor lane. Put a_j=4 A[j,col], Z=sum_j a_j u_j, l=Z*4^-1 mod q in [0,q), and k=(Z-4l)/q. The numerator is divisible by q. In the local ring modulo qQ, the source matrix entries are the modular representatives of A. Consequently the source's carry is exactly

    C = k * 4^-1 mod Q,
    new_low = l.

Indeed 4(sum_j u_j A[j,col]-l)=qk, and division by the unit 4 commutes with reduction. Replacing each rational A entry by its representative modulo qQ changes the sum by a multiple of qQ, hence changes the divided carry only by a multiple of Q. This proves equality with the source interpreter's `(total-total%q)//q % Q`; taking an ordinary rational floor before reduction is invalid.

For S8 every entry is integral. Column positive/negative sums give -1<=C_rational<=3, so k is one of {-4,0,4,8,12}. For S8^-1, its eight column positive/negative sums are respectively (1,0), (1/2,1), (1,1/2), (1,0), (3/2,1/2), (1/2,0), (1/2,0), (1,1). Since 0<=u_j,l<=q-1, the strict bounds -negative_sum-1 < C_rational < positive_sum imply -7<=k<=5. The common allowed code range [-7,12] therefore covers both directions for every odd prime q and every f. Tensoring selects one lane; it does not add f terms. This is a source-specific theorem, not a claim for arbitrary matchers.

## Literal old-cache decoder and dispatch

`controller.py` builds a finite local instruction graph. Its compiler states consist of a fixed bit position, the accumulated integer Z from completed low digits, and the partial next digit. There are at most (8b+1)(32q+1)2q such states. Reading an out-of-radix selected digit rejects. Fixed unit moves visit the eight specified old-cache cells, including the actual strided f>1 positions, then the cache end marker; there are no runtime addresses. At a leaf the compiler, not the running machine, computes l and k and emits literal writes of b bits for l and five bits for k+8. The old cache is unchanged and its head returns to its initial cell.

The linker then reads all five code bits through actual branch/move instructions. One of twenty fixed offset machines runs on the preserved binary Q input. Afterwards five literal writes erase the temporary code and all heads return. Thus this is not a host-selected call to `compile_offset(k)` during payload execution. The Python verifier's construction and endpoint decoding are observers, not machine operations.

The valid-input contract supplies a complete old-cache tape of D canonical b-bit low digits, an END marker, preserved canonical binary odd Q>=3 with LEFT/END markers, and three disjoint blank owned output/work tapes. As in the predecessor valid-input contract, the compiler does not certify an unbounded blank tape by inspecting one cell. It validates the eight consumed digit ranges and the cache endpoint; it is not a global GL-membership validator. The returned owned outputs are one b-bit new-low word and one marked canonical binary C+1 descriptor. The temporary quarter code is blank; old-low and Q inputs and all five heads are restored. The new-low output is retained for a later commit, and the old cache must remain owned until all cells have been processed.

## Literal quarter descriptor

For the fixed code k and an odd Q>=3, choose t so that k+tQ is divisible by four. If Q>=13, choose t in {0,1,2,3} by Q mod4, increasing t from zero to four when k<0. Then 0<=k+tQ<4Q and

    C+1 = (tQ+k+4)/4.

The finitely many smaller moduli 3,5,7,9,11 have explicit compiler-generated outputs. For large Q a finite scan recognizes its low two bits, size category and canonical positive ending, and restores the input head. A binary transducer multiplies each input bit by the fixed t, adds a finite signed carry initially k+4, and emits its low bit; its carry state updates to floor(total/2). These are compiler transitions between finite states, not runtime arithmetic instructions. It checks and drops the two zero low bits and emits the remaining quotient bits, flushes the final nonnegative carry, removes high zero bits and writes the final marker. The input and output heads return. Removed output symbols, including the provisional endpoint, are blank, so there is no stale descriptor suffix.

The carry-state set is finite: initially -3<=k+4<=16, 0<=t<=4, and the update contracts its magnitude. The positive integer C+1 is at most Q, so trimming terminates at a one bit. This proves correctness for arbitrary binary length, rather than extrapolating the 40-bit fixtures.

## Explicit physical and compiler costs

A decoder execution uses exactly D b right moves, D b left moves, 8b input-bit branches, one endpoint branch, and 3b+15 output writes/moves, plus a halt/continuation. Five-bit dispatch and retirement add fewer than 64 transitions. The offset code has at most two forward input scans, at most two input returns, one output emission and two output scans/returns; expanding its branch/write/unit-move loops gives the conservative bound 256L+1024. A complete linked invocation is therefore bounded by

    64 D b + 256 L + 2048 transitions,
    2 D b + 4 L + 32 visited cells.

Visited cells include the temporary code cells subsequently erased. These bounds include sparse-cache strides, source/head restoration and descriptor output, not merely mathematical arithmetic. The actual code returns all five heads to zero; translated origins give the same counts.

The pre-input compiler has O(b q²) logical decoder states; each emitted edge/leaf expands at most O(Db+b) fixed movement/write instructions. The twenty offset machines and their dispatcher have constant size independent of q,N,w. A deliberately loose explicit instruction envelope is 10^6 D q² (b+1)², and schoolbook pre-input bit work is O(D q² (b+1)^4), including primality validation, sorting and finite coefficient computation. These are nonzero functions of N and q. The iterative state construction has no Python-recursion-depth dependence. No GL_N(F_q) enumeration is needed for this descriptor frontend. Runtime width w does not enter compilation.

## Actual first fixture and the direction boundary

For the assigned q5,w4,f1 old low I+e01+4e12, actual cell5 gives l=4,k=-4 and C=124. This reproduces the nonzero carry used by PR4989's omission control. The API also admits low I+3e05: it is a transvection and hence invertible, and actual S8 column0=2e5 gives l=1,k=4,C=1 at cell0. The unchanged source interpreter runs its full forward/native/inverse route and restores this input. This second example is an allowed actual-source input, not a report that the predecessor's arithmetic is wrong.

PR5019's supplied machine maps `(p,x,g,y,z)` to `(p,x,g,y +/- (c*x+C),z)`. Its inverse only changes the sign; it still preserves x. For later target a>=1, take x=high[a-1], y=high[a], c=0, P=Q^(a-1), G=1, and S=Q^(D-a-1) Z_spectator on each complete low fiber. This consumes every high/spectator bit. At target0 there is no earlier complete Q high axis, so the identical call does not typecheck. On a fixed low fiber its prefix extent may be one; a finite low prefix cannot supply an arbitrary-width Q axis either. Adding an artificial Q axis multiplies payload volume by Q and is not a linear adapter.

There is a valid conditional repair, so this is not an impossibility theorem: an already completed OLD swap of high0/high1, the supplied c=0 shift on the later field, and the same OLD swap back perform the cell0 translation. The repair has two OLD calls, one shear and their real source/output installations. It does not become free by renaming the two axes. The earlier PR5019 unit-carry predecessor has the same later-y contract; neither its inverse nor the signed-dyadic unit-scale work supplies an uncharged axis reversal.

## Full-fiber tariff gate and exact unfinished boundary

Let T=|GL_N(F_q)| and H=Q^D Z_spectator, so V=T H. Descriptor production over all D coordinates and all low types is at most T D (64Db+256L+2048), which is O_{N,q}(V) since L<=Q<=H. Given descriptors and correctly isolated low fibers, PR5019 shear calls cost at most 1024 D V per direction. A physical sequential output installation/erasure can be charged linearly; it is not part of the implemented frontend. The cell0 repair additionally costs `2 T A_OLD(H,w)` for the completed OLD supplier, plus linear transport. It increases a fixed route's existing OLD call count rather than proving an asymptotic obstruction; P3 must still use the changed constants.

A full low-type permutation could be compiled by enumerating the finite low types and emitting sequential block passes, with a nonzero T-dependent tariff. That construction, its exact full-array layout binding, the complete low-cache lifetime/retirement, and source/output installation are **not implemented or validated here**. No paid full-fiber controller is inferred from the descriptor theorem. The bounded pivot therefore ends with a physically implemented source frontend and the conditional repair invoice, not the requested complete lowering. Reopening requires one concrete full-fiber controller with all those operations and measured/derived counts; a few more scalar residue tests would not close it.
