# Actual compression suffix: original coordinates and nonlinear defects

JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.
This audits an existing conditional claim in Jose Manuel/jmbarrancoml's
PR3935. It is an informal quantified source proof with bounded physical
corroboration, not independent human or formal-kernel acceptance.

## Statement and retained premises

Let a production-admitted Tensor catalogue have D resampled axes, C positive
complete rows, common p>=101 and all of PR3851/3935's production hypotheses.
The actual source has D=plan.axes+1>=2; the argument also works algebraically
for D=1. Use the exact original-axis normalized compression operator
B_i=2^(-j) D_norm N_i^(-1) C_i from PR3935, not a matrix reconstructed from
rounded LU pages. Retain the following separate premises:

1. Every core page comes from the matching original-axis producer, including
   its old-H matrix, selection, core/window origins, normalization and work
   grid. Header acceptance alone is insufficient.
2. For every complex unit-disk target line, the actual Core output on its
   declared source core differs from the corresponding restriction of B_i by
   at most delta_i. This is PR3851's uniform completed local result, including
   principal-window locality, old-H inverse approximation, resolvent error,
   normalized diagonal error and final p-grid rounding. For the common
   production policy, delta_i<2h, h=2^-p. Its internal exact arithmetic,
   factor/pivot and stored-width justification remain inherited.
3. ||B_i||_(infinity->infinity)<=1/8. The principal-window bound <=1/4 is
   different; it is not substituted for this global exact-operator bound.
4. The retained physical copy, field-move, complete gather, record, primitive
   numerical and ownership contracts hold. We inspect their caller indices
   and compare the actual finite program; we do not re-prove their machines.

For an arbitrary p-grid post-chirp target tensor z with ||z||<=r_0<=1,
and any ideal target tensor y with ||z-y||<=e_0, the actual compression
suffix before the final 2^gamma restoration returns z_D with

  ||z_D|| <= 8^(-D) r_0 + sum_(i=0..D-1) 8^(-(D-1-i)) delta_i,
  ||z_D - (B_(D-1)...B_0)y||
      <= 8^(-D) e_0 + sum_(i=0..D-1) 8^(-(D-1-i)) delta_i.

Each local invocation is in its unit-disk domain. In particular, for the
actual chirp-return bound r_0<601/1000 and common delta_i<2h,

  ||z_D - (B_(D-1)...B_0)y|| < 8^(-D)e_0 + (16/7)(1-8^(-D))h.

The strict expression uses the strict local defect bound, not a stronger
independent local theorem. The source's conservative e_0+2Dh follows.
We do not change the production precision, charge fewer operations, or claim
a new overall Fourier error theorem. Exact final restoration multiplies the
whole error by 2^gamma; it never erases these terms.

## The actual core partition and its zero-padded representation

For axis i let t_i=K_i L and define

  a_(i,k)=floor(k L s_i/t_i),
  ell_(i,k)=a_(i,k+1)-a_(i,k),  0<=k<K_i.

Binding.__init__ constructs these exact original source_index endpoints.
They telescope from a_(i,0)=0 to a_(i,K_i)=s_i, have positive lengths by
the admitted geometry, and satisfy ell_(i,k)<=L. Thus the source cores
partition [0,s_i) once in increasing order. This proof uses floor endpoints;
principal-window endpoints use a different half-shifted ceiling operation.
They must not be interchanged.

Let J_i embed a source vector into K_i slots of length L: slot k contains
coordinates [a_(i,k),a_(i,k+1)) followed by L-ell_(i,k) zero records.
J_i preserves the sup norm. Let A_i compact those first ell_(i,k) entries,
check that every slot tail is zero, and append t_i-s_i zeros. A_i is a
partial exact permutation/zero insertion on this admitted subspace and
preserves its sup norm. CoreAssembly.run implements exactly A_i: it checks
start==position, sums lengths up to s_i, checks all removed tail bits and
then emits global source padding. This is not an unrestricted projection
which could silently discard arbitrary data.

Let H_i copy the catalogue's target halos periodically from period t_i,
including their signed origins. All remaining coordinates are spectators.
PeriodicWindows.run checks complete extent, monotone overlaps and the
triple-lift interval, and copies each declared target record. An overlap
copies a value, never sums two copies. Hence ||H_i||<=1. Let Ctilde_i apply
one actual Core per halo and spectator line, concatenate its returned core,
and append the slot zeros. LineApply.run consumes every protected child
return and writes exactly these zeros. Define the deterministic assembled
computed line map Ftilde_i by J_i Ftilde_i = Ctilde_i H_i.

Premise2 then gives, for every unit-disk original target line v,

  ||Ftilde_i(v)-B_i v|| <= delta_i.

The maximum over disjoint cores yields delta_i, not K_i*delta_i. Every
component is covered once; no averaging or cancellation is assumed. The
finite p48 fixture has only boundary cells, but this definition and the
conditional proof cover all Core cells through premise2, not through that
finite simplification.

## All halos first, then every actual mixed-radix line

Tensor.run performs the following actual suffix: gather natural target
order; all D target halos; all D compression axes; all D core assemblies;
scatter to natural order; remove source padding. It does not interleave
compression with new halo extraction. The checker authenticates and extracts
those six existing statements from Tensor.run's AST, without replacing any
numerical owner, and executes them on an arbitrary admitted post-chirp input.
This is a source-extracted suffix execution, not a successful full Tensor.run.

In canonical order [C][all K fields][all I fields], at stage i Layout uses

  move_C=C product_(j<=i) K_j,
  move_A=product_(j>i) K_j product_(j<i) I_j,
  move_R=2(p+2) product_(j>i) I_j,
  halo_C=C product_(j<i) K_j, halo_R=move_A move_R,
  line_C=C product_j K_j product_(j<i) I_j,
  line_A=product_(j>i) I_j,
  line_outer=C product_(j<i) K_j,
  line_count=product_(j>i) K_j product_(j!=i) I_j.

For the halo loop, processed I fields have target_halo length and remaining
ones have L. For the compression loop these choices reverse: processed
fields have L and remaining ones target_halo. For assembly they are all L.
These are exactly the three Layout constructor calls in Tensor.run. The
move/line products therefore enumerate every complete spectator tuple,
including all coarse tile fields and zero-padded slots. They are not counts
of active support. Binding.compression_header checks p,P,target_halo,
source_length, core offset/length, bandwidth and actual producer work width.
The separate compression_sources stream binds the missing absolute origins;
source-generated page provenance is still premise1.

For i!=j, moving H_j past Ctilde_i is valid as a coordinate-selection
identity: each j-halo copy selects one complete i-input line, so applying the
same deterministic i-page to every copy yields identical i-results. A zero
spectator line stays zero because all actual Core scalar operations are
homogeneous before rounding and inward truncation maps zero to zero.
Thus extra zero slots also match. Core assembly on another axis commutes
for the same reason, checking only tails which the i-map leaves zero.

This does NOT claim two nonlinear numerical axis maps commute. Their order
0,1,...,D-1 is unchanged. It only moves copies, exact coordinate rearrangements
and zero embeddings across operations on a different coordinate. In
particular it never extracts a new i-halo from a restricted i-core.
Repeatedly applying this identity identifies the literal all-halos-first
schedule, after compaction, with Ftilde_(D-1)...Ftilde_0. Complete gathers
and final padding removal change representation but not the error norm.

## Domain and error induction without nonlinear Lipschitz continuity

Put z_(i+1)=Ftilde_i(z_i) and y_(i+1)=B_i y_i in natural coordinates,
using the current target/source axis dimensions. Suppose ||z_i||<=r_i<=1.
Every extracted local halo has norm<=r_i. Premise2 therefore applies to
every actual local call on z_i; its bound is uniform over all core pages,
all spectator lines and all positive C. Premise3 gives

  ||z_(i+1)|| <= ||B_i z_i|| + delta_i <= r_i/8+delta_i,
  ||z_(i+1)-y_(i+1)||
    <= ||Ftilde_i(z_i)-B_i z_i|| + ||B_i(z_i-y_i)||
    <= delta_i+e_i/8.

The comparison evaluates the local defect at the computed input z_i. It
never invokes a rounded Core on y_i or takes a difference of two rounded
Core calls. Since delta_i<2^-100<1/8 and r_i<=1, r_(i+1)<1/4<1; induction
is valid for every admitted D and arbitrary C. Solve these scalar recurrences
to obtain the stated sums. These elementary recurrences are only the final
step; the substantive obligation above binds their arguments to the actual
source-indexed physical suffix.

Even inward scalar rounding is not 1-Lipschitz on real inputs: truncation
to integers sends 99/100 to0 and1 to1. The input distance is1/100 and output
distance1. Likewise a smaller per-call approximation error cannot justify
interchanging two nonlinear axis operations. No such inference is used.

## Complete costs, evidence and limits

All source costs remain: catalogue/source and factor production, all halo
and overlap copies, triple lifts, each full-support gather, each scalar
product and rounding, both local passes/Schur solve, zero slot emission,
protected-return copying and final scratch/marker erasure. Our proof removes
no paid operation. PR3935's full conditional time/space invoice remains
inherited; isolated setup is not absorbed into a small packet.

The bounded checker starts with a signed complex8x8 target packet of norm
below.601, executes the actual extracted suffix and checks every Core return
against a separately written signed two-pass arithmetic model. It compares
all49 final complex records against a natural-coordinate axis model and
records halo/compression/assembly stage sizes, norms and source hashes.
The retained grammar parser is credited; the numerical checker does not
call its compress/full functions. Wrong-layout and restricted-axis reuse
controls discriminate the original-coordinate result. Reduced p48/P80
pages are NOT production pages: neither their measured norms nor the
successful staged comparison establishes premise2 or3 for production.

The proof is conditional on the original all-size local analytic result.
It does not independently verify Gaussian interval generation, old-H
resolvent/locality estimates, Schur conditioning, word/FFT correctness,
production native suppliers, chirp correctness or CRT/integer recovery.
It exposes precisely where each is needed. No selected result changes.
