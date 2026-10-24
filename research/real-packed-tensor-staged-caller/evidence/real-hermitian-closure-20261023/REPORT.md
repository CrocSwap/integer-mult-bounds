# The actual Gaussian Core already separates the two real channels

The proposed real/Hermitian packing does not presently change a normalized recursive rank moment. The actual PR3935 compression Core runs the same real scalar solver twice—once on each component—with the same page, dimensions, shifts and coefficient streams. One complex packet already carries exactly two independent real packets. Relabelling them as two jobs doubles both their real-dimension reward and their scalar child work. A top-level reduction from three complete Tensor calls to two remains a possible finite outer optimization, requiring its own implementation and numerical proof; it supplies no recursive κ gain by itself.

A source-chain correction is decisive: the inspected runtime is **Tensor → physical Core → Interior/BandedSolve → FftWord → RingProduct**, not Tensor → RawGaussian → Gaussian → Full. The rational-unitary classes belong to a different proof/reference chain. No adapter identifying them as these runtime children was found or assumed. This packet stops the recursive κ claim at that missing interface and the real-work cancellation; it does not claim a universal barrier to real FFT algorithms.

## Exact sources and read-only scope

The outer caller is JoyboyBrian's PR5095 head `e65f47db55b9a3779fbf7fe23e93a8a4c5eb3ce1`, `research/physical-tensor-crt-sandwich-recovery/{sandwich.py,sandwich_sources.py,PROOF.md}`. Its exact-head snapshots and authentication are retained in `outputs/outer-bilinear-interface-20261023/appendix5095-sources/` and `APPENDIX-5095-SOURCES.json`; this packet read them without running the loader. The source Tensor is Jose Manuel / jmbarrancoml's PR3935 head `f687fa171ef760fa98a4be1289717b47dd4ee0b3`, `research/physical-gaussian-tensor/`.

The actual nested source pins declared by those frozen loaders are:

| Child | Exact head | Source-bearing parent |
|---|---|---|
| physical Gaussian expansion | `1a86a8fb73bb7a0982fff99852a031832c191902` | Tensor `inputs/expansion-export.tar.gz` |
| physical Gaussian Core | `7ab67b4a84d28cd562b9711aa315ca5b47822b37` | expansion `inputs/core-export.tar.gz` |
| physical FFT word | `9b5474f47b0ea9a3c76bb5b1b577fb36704815e0` | Core `inputs/word-export.tar` |
| physical ring product | `62264289adb01f3ba4930cd0154c75887f96203c` | FFT word `inputs/ring-export.tar` |
| branchfree Gaussian reference | `8922e3b3f0fd7772b0fb42028eb2532984c3ab42` | Core `inputs/branchfree-source.tar` |

`SOURCES.json` records archive SHA256s and text-member hashes. Only selected text members were copied into this packet's `sources/`; no repository module, source loader, constructor, executable fixture or replay was run. The frozen centre0 package was not changed. Monitor scope clearance through #5096 was targeted and is not exhaustive novelty evidence. This packet does not touch Joy's #5018 allocator successor.

## Complete parent ABI and real dimensions

PR5095 accepts **two independent** length-q streams of nonnegative radix-2^b digits. Each stream enters as the real array a_j/2^(b+2), padded with S-q zeros; the independent real dimension before padding is q for each operand, hence **2q total**. The two digit streams are retained separately in the bilinear product even if encoded as one complex input. They are not 2q independent complex coordinates.

The parent executes two forward complete normalized source transforms T=R F_s, the scalar coordinatewise product on every one of S source frequency coordinates, and one complete opposite-sign Tensor. The inverse recovery scale is S²2^(2b+4). Source R is multiplication of the stored frequency indices by the per-axis t_i and commutes with frequency negation. For H=T(a+i b), define H#_j=conj(H_(-j)); the exact packing formula is

    T(a) T(b) = (H²-(H#)²)/(4i).

Frequency negation is j_i→-j_i mod s_i, with source layout R retained. This is not the index map of the inner physical solver's record reversal. The actual digit bounds a,b<1/4 give |a+i b|<sqrt(2)/4<1/2, within Tensor's entrance half-disk. Arbitrary real half-disk arrays would instead need a paid/charged rescaling or larger admitted radius: packing two values each of magnitude1/2 can have magnitude sqrt(2)/2.

Tensor's `boundary()` flips the imaginary sign at **both** entrance and return for `opposite=True`; it executes the same interior call sequence. Its `run()` body performs expansion on all axes, a chirp call, then compression on all axes. Source-level citations are frozen `tensor__tensor_engine.py:170–198,220–248`. This gives an opposite complete transform, not a child-pair involution permitting half of its internal calls to be skipped.

## One complete nontrivial child decomposition

Take the literal Core branch with a nonempty interior cell, of interior length ell greater than band=2w; the cell has ell+2w records. This is a symbolic census of the actual nontrivial branch, not a claim that a new numerical catalogue was constructed. For a full page let N be the number of such cells, m the selected source count, n the complete halo count and k the returned core count.

`gaussian_page.Header` binds input_width=p+2, shift=P-p, work width greater than P, core_offset/core_length within m, positive even band=2w≤2p, and m≤n≤2m+2. Each input is one signed complex p-grid record. The source/output disk bound is |z|≤1. Page and source are borrowed distinct tapes; the returned k complex records are parent-consumed and the child return cleared. The runtime has owned blank scratch, not408 independent native dirty-helper jobs. Its scratch must not be credited as such jobs.

For **one real component**, `Core.scalar()` does:

| Literal step | Child count and dimensions | Source lines |
|---|---|---|
| Gather selected component; scale by2^(P-p) | one m-real-record selection | `gaussian_core.py:45–82,198–202` |
| First cell pass | one `Interior(ell)` per nonempty cell; boundary-only clipped cells use no Interior | `gaussian_core.py:101–132,203–210` |
| Global Schur boundary solve | one `BandedSolve(boundary_length,band,width,P)` | `gaussian_core.py:211–223` |
| Reconstruct and second cell pass | one further `Interior(ell)` per nonempty cell, then real normalization and core extraction | `gaussian_core.py:163–187,224–236` |

An `Interior(ell)` uses **five real diagonal passes**, **two same-h lower convolutions** and **two ordinary record reversals** (`gaussian_interior.py:180–193`, with the second reversal inside `lower(reverse=True)`). Its real factors are weights, inva, f, invf and h, with

    0<q≤1/4,
    f_j=product_(t=1..j)(1-q^(2t)),
    h_j=(-q)^j/f_j,
    0<weight_j≤1.

All are real signed rational/dyadic streams. The similarity weights need not be reflection symmetric; realness alone does not supply a frequency-reflection pairing of different cells. The record reversal is **j→ell-1-j**, not j→-j mod ell. No complex twiddle occurs in this Interior factorization. Any complex FFT twiddles are hidden inside its integer-word multiplication child, whose complete endpoint is an exact integer product rather than a partial Gaussian query.

Each lower convolution executes four signed-magnitude word products—(++),(--),(+-),(-+)—with fixed coefficient-recombination signs (`gaussian_convolution.py:138–180`). It does not omit a pair because an upper-level operand was real. `FftWord.run` chooses its base versus RingProduct branch from the common width, not from component identity; Core uses a fixed4096-bit crossover. This gives the following exact structural census:

| Completed scalar workload | Interior calls | Lower convolution calls | Word calls from these convolutions | BandedSolve calls |
|---|---:|---:|---:|---:|
| one real component | 2N | 4N | 16N | 1 |
| one complex Core / two real components | 4N | 8N | 32N | 2 |

The word-call column excludes the additional real diagonal, norm-check and band-solver word arithmetic; these also remain present. Nothing in this census assigns a native Gaussian rank to a word call.

`Core.run()` calls `scalar(...,component=0)`, repeats the **same** page, then calls `scalar(...,component=1)`, and interleaves both returned components (`gaussian_core.py:260–272`). Every solver-child call above is duplicated with identical dimensions, coefficients, kernel q, grid and shift. There is no real/imaginary asymmetry in those solver call counts. Input norm checking is performed while gathering the first component, and the final paired norm is checked once after both passes; these shared validation details are not a deleted recursive solver call. Scratch cleanup and complete-return checks apply to both passes.

## The all-width condition and cancellation gate

For this fixed real page, the exact counterpart satisfies

    Core(a+i b)=Core_real(a)+i Core_real(b).

This is a useful closure of the **same real operator** on its two scalar channels. It is already what the source executes. Packing two independent real streams into one complex packet does not remove either scalar channel's required solve. Both are returned once.

In moment notation, if a complex supplier has W width-m roles and n_r rank-r child roles, its complex roles carry2mW independent real dimensions. Splitting the same computation into real roles gives2W roles and2n_r child roles. The normalized coefficient stays

    (1/(2W)) sum_r 2 n_r (r/m)^(1-a)
      = (1/W) sum_r n_r (r/m)^(1-a).

One must not retain the doubled real reward while retaining only one half of the child's paid work. The physical Core census supplies no factor improving this expression. It can support ordinary constant-factor engineering or avoiding work on known-zero channels in a new restricted ABI; it does not supply a better complex supplier exponent.

A genuinely different recursive real/Hermitian supplier would require, at **every** scale, an explicit involution tau on the actual child-call descriptors and paired data satisfying

    x_tau(c)=J_c conj(x_c),
    A_tau(c) J_c = J'_c conj(A_c),

with equal input radii, grids, shifts, kernel/twiddle parameters, full outgoing references and rounding error contracts. Fixed points need a real-subspace implementation and its own bill. Dirty borrowed helpers need the same pairing or independent restoration; they cannot become discarded redundant fields. Even when two main child inputs are conjugate, two independently dirty helper inventories need not be. A shared execution must serve both complete helper inventories and pay its bill, or lose the second helper target reward. A useful saving must therefore remove paid work without deleting an equal amount of eligible independent real target work. Every eliminated child must be matched to a legitimate returned independent real job, and its actual paid rank census must change after real-dimension normalization.

No such tau is defined by Tensor's opposite flag. Its chirp stage generally creates complex intermediate arrays; Gaussian cells and selected windows have their own origins, halos, coefficient pages and core offsets. The source does not assert that different cells/lines come in matching conjugate pairs, nor does its ordinary reversal define the required global frequency involution. The actual Core branch above pairs equal **operators on independent components**, not redundant conjugate-dependent children. The later FftWord/RingProduct boundary has not been rebound to a Hermitian recursive supplier, and no RawGaussian/Gaussian/Full runtime adapter is provided.

## Decision, unpaid obligations and credit

**Stop the recursive κ claim.** The literal source census has not changed a normalized rank moment. The original top-level two-forward/one-opposite Tensor structure makes a classical finite3→2 packing proposal intelligible, but this packet does not implement it, price its scalar products/routing/rounding, or claim production recovery. Its source error guard must be rederived, including correlated errors from H and H#, inward rounding, possible division by4i, opposite transform and final integer recovery.

Remaining obligations before any recursive claim are a changed paid child family with nontrivial normalized moment improvement, complete conjugate-child descriptor closure, independent real-domain dimensions, actual native/dirty-helper ABI and ranks, physical routing and owned-output lifecycle, an all-scale rounding/precision proof, compiler reserve and outer transfer. These costs are unknown here, not zero. No public write, fixture, emitter, allocation change, native execution, large replay or κ calculation was performed.

Credit JoyboyBrian's PR5095 physical sandwich and separate allocator work; Jose Manuel / jmbarrancoml's PR3935 Tensor; Tekalign / tekuuu's CRT; the physical Gaussian expansion/Core, FFT-word and ring-product authors; Chafik Boukhalfa's branchfree two-convolution inverse; Cinna Davis/Cao Yifan and all retained native, routing, arithmetic and analytic contributors. The conventional real-FFT packing identity is predecessor mathematics, not a new discovery. Astra's literature worker owns precise published attribution. This bounded source inventory used substantial OpenAI Codex assistance.
