# Final mathematical cross-check and sufficient scope

Disposition: the phase-completion proof and the normalized T372 comparison are sound under their stated hypotheses. This is a second-pass mathematical review by the application author, using an alternative projector argument and a fresh exact profile calculation. It is not an independent-author or human peer review. Root separately reports an independent rerun of the phase tests with the same passing report; that execution is distinct from this review.

## Prime-phase completion: alternative verification

For a prime p, let A be the complex matrix represented by the received integer phase table, with A*A=pI. The matrix P=I−AA*/p is an orthogonal projection of rank one. Each diagonal entry is 1/p because every row of A has p−1 entries of modulus one. Set z=pPe_0. Then z_0=1 and A*z=0. Rank-one positivity gives |P_(i,0)|²=P_(i,i)P_(0,0)=1/p², so every |z_i|=1. For i≠0, its formula is z_i=−Σ_j A_(i,j) conjugate(A_(0,j)). The prime root-count lemma in the supplied proof therefore identifies z_i with precisely the missing phase. This verifies the algorithm without relying on the orthogonal-completion proof route used in its documentation.

The root-count lemma is correct: the prime cyclotomic relation forces all autocorrelation coefficients, after subtracting the constant one, to agree. Their sum forces L=p−2 and Σc_a²=Σc_a=p−1. Nonnegative integer multiplicities are consequently zero or one. The incoming and completed column-pair histogram tests use the separate p-term vanishing criterion, not the p−1-term unit-modulus criterion. Both cases, including p=2, are handled correctly.

The checker first enforces literal preservation of received integer codes, so a phase change to an old column cannot pass merely by preserving orthogonality. The first appended phase is zero, removing the otherwise unavoidable global phase freedom. The fixture comparison correctly checks the original missing column only up to that global phase.

**Sufficient statement for the final package.** For every prime p, any integer p×(p−1) phase table whose pth-root columns are exactly orthogonal is extended by the algorithm to a p×p phase table representing H with H*H=pI. Every received code is preserved literally and the new column has first entry one. The independent checker certifies this conclusion for the supplied input and output using integer histograms. Thus one missing orthogonal pilot column can be restored from exact prime-phase data. No tolerance for noisy phases, multiple missing columns, absolute erased-column phase recovery, communications performance or mathematical novelty is claimed.

## T372 versus the full pinned PR2848 profile

The exact comparison claim SHA-256 is aceb1394b3e8f3abcc9b1a0dc82756ab937ffbefc2f37305a229a00ccc5137e9. Its profile SHA-256 is ea57a40446e596bdcf1348772790ae6be4df9766e4b502c277ee81025226697b. The new profile SHA-256 is 868cfdbcb73413f43b2d834d296f5cca261ed863a5ac54a69d08527f24a13ce7. Reading those actual files afresh gives

    2·new − 3·old = 2H_32 − 2H_5 − 3H_2 − 3H_16.

The new and old replica counts are 372 and 248, and both normalize at 744 after multiplication by two and three. The new rank mass is 24,212,736; the old rank mass is 16,141,824. Their normalized mass difference is exactly zero.

For every 0<p<1, strict subadditivity gives 32^p<2·16^p and 32^p<16^p+2·5^p+3·2^p, since 32=16+5+5+2+2+2. Adding proves that the displayed normalized cost difference is strictly negative. The common positive normalization factor in the moment does not change its sign. Hence the comparison is about the complete paid profile, not an unnormalized local rewrite.

The directed moment receipt proposes the lower endpoint 0.001718659357407250209979 minus 10^-46 and 10^-70. Subtracting the full pinned PR2848 rational claim gives exactly 21227558005129/25000000000000000000000>0. The strict rational comparison and both rank-mass identities were recomputed during this review. This finite comparison does not, by itself, discharge native, source-access, hosting, precision, recovery, ordinary-recursion, BIT, analytic-transfer or all-size hypotheses. Full admission remains attached to root's separately bound release receipts.

## Prose and immutability checks

The application README and proof were inspected for ordinary words adjoining decimal digits; no such prose defect was found. Unicode mathematical notation is preserved. Mathematical variables, phase codes, filenames, IDs and hashes are unchanged. The 29 selected files still match the frozen phase manifest. No phase source, fixture, T372 data or existing proof file was modified by this review.

Reviewed phase proof SHA-256: 3ecfedb393147ae8f10293f11af7e0ad31f5c6473cf85aeb370f7191b7aaf475.
Phase manifest SHA-256: ade5f93cbafd785005b55fe102ed2d0fdd2d88fafc05343362922a0b48e63abc.
