# Exhaustive independent audit of full-query endpoint support

This audit independently stress-tests the algebraic support theorem in Chafik Boukhalfa / @chafreaky's PR1877. It adds a complete small finite-field census, independently found missing-premise witnesses and a rational sharp example. It does not re-audit the 112-port physical Fourier-frame obstruction or claim that finite fields certify complex rank.

## Statement being audited

Let L,R be r-by-n matrices, K be n-by-r, and let G be invertible with LG=R. Put Delta=G-I, J=I-KR, H=J Delta. If rank(R-L)=r and every K row is nonzero, the supports of rows of Delta and H cover all n ports. Indeed

    R Delta=(R-L)G

has full row rank. If Delta_i=H_i=0, then K_i R Delta=0, contradicting the nonzero row K_i. Further L Delta=R-L gives rank(Delta)>=r. The separate assertion rank(H)>=r needs J invertible; it does not follow from the support cover alone. Right-multiplication by G^-1 shows that G^-1-I has exactly the same nonzero row support as Delta. These arguments work over any field. They are the credited predecessor proof, independently checked here, not inferred from the census.

## Complete finite domain and new evidence

Over GF(2), enumerate all 168 invertible 3x3 G, every r-by3 L for r=1 and2, and every 3-by-r K with no zero row. Set R=LG, then retain rank(R-L)=r. This exhausts 1008 rank-one and 117936 rank-two full-query cases. All satisfy the cover. For invertible J, the 432 rank-one and 40560 rank-two cases also satisfy both individual rank floors. The exact attainable (source support,target support) pairs are recorded by the verifier; these are finite GF(2) spectra, not the 112-port complex spectrum.

The checker independently searches the complete 3-port rank-one matrix domain for witnesses violating the cover after removing exactly one of G invertibility, full rank of R-L, or nonzero K rows, while retaining invertible J. It requires nonzero query/read matrices and at least one nonzero K row, avoiding empty-query controls. A separate actual witness has full hypotheses for the cover but singular J and H=0, demonstrating why the target rank conclusion needs that additional premise. The predecessor's PROOF.md already states this premise; no error in it is alleged.

A separately multiplied rational sharp example is

    L=[1,0,0], R=[1,1,0], K=[1,1,1]^T,
    G=[[1,1,0],[0,1,0],[0,0,1]].

Delta has only row0=e1 and H has rows1,2=-e1, so the support sizes 1 and2 attain total 3. RK=2 ensures J invertible over Q. This is not a lift of a finite-field rank claim. It independently tests the original characteristic-zero algebra.

## Reproduce and limitations

    python3.12 scripts/research_package.py --package research/source-query-finite-field-audit

Read-only standard-library Python; explicit checks remain active under -O. The unchanged PR1877 README and PROOF are pinned by SHA256 and Git blob; no predecessor executable is imported. The exact head and complete overlap snapshot are recorded. This contribution is intentionally an independent proof-hypothesis audit. The actual112-port source instance, fixed-frame minors, native access costs, carrying the encoder through later work, hosting, precision, cold replay and all-size theorem remain outside this audit. No new supplier or kappa.

## Source-head refresh

Before publication, PR1877 advanced from the audited head `4d9fa6016682c910be06e55b1c974d53052aee76` to `6d455d2d71eb35ecf8e562711e5f719b994fe3f3`. The first 2386 bytes of PROOF.md, through “The verifier checks all four examples.”, are identical and include the audited algebraic theorem and hypotheses. SOURCE-REFRESH.json records both full-file Git blob and SHA256 hashes plus the identical section hash. The newer actual 112-port 8+104 sharp construction, generalized fixed-read frame obstruction and additional mutation controls belong to the credited predecessor and were inspected for scope, not independently verified here. The original immutable source pins remain the inputs to this audit.

## Open next questions

Can a paid chart transition or changed response space realize a complete useful source encoder? First pin an actual pair of native charts and price transport/restoration. The support theorem alone supplies neither a universal native-cost lower bound nor a construction.

## Credit

Chafik Boukhalfa / @chafreaky, PR1877, supplies the support theorem and source/frame proof; @aliromman /PR1862 the valid source encoder. PR1042/1094, E8/gauge44/native lineage retains its attribution in the pinned predecessor. New exhaustive audit and exact controls prepared for woklerx with substantial OpenAI Codex assistance, Apache-2.0. No independent human or formal proof-assistant review.
