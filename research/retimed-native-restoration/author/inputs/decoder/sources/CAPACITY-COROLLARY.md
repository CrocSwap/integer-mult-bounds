# Production binary owner capacity is less than twice the external bank

This separate corollary combines the binary raw-context census with the
independently accepted numerical mass enclosure published in PR #8091 at
`de02b59fa9a74d4958d0d114d25e9083ab91b022`. It does not alter the frozen census
proof or numerical proof. Implementation: Ali Romman's #8042 at
`dfd25d553a843a946ca0b94130a5ff8943e98fdd`.

## Exact dependencies and conclusion

`COROLLARY-BINDINGS.json` pins portable copies of the mass proof, its acceptance,
its production binding, installed constants and this package's census.
The accepted numerical proof has SHA256
`b92516aaa39192c6713654fa6f41b4c4f8367b1f71c7e374b95fd31687464c1b`;
its independent `CROSS-REVIEW.md` has SHA256
`281ad36f151c2e63620a2a08a9eaf099615de47e71e180fd24de32a4f9e236ad`.
Both refer to the identical `transport.py` SHA256
`98bdb540233794338b426d1b0d0e72cff7fcbbd08be702af0d81e237dbecaae9`.
The frozen census proof has SHA256
`672289a9a52ffdc710b4ff037c03c7149097fb99a9083ba9da62021edc77c97f`.

For every successfully executed production binary recipe at height h >= 3000,
with N=2^h and B=N^92, the fresh `OwnerBanks` instance in
`binary_receiver.Receiver.compiled` satisfies

\[
\boxed{\mathrm{capacity}<2B.}\tag{1}
\]

The arithmetic below holds already for h >= 1024, the source Recipe's allowed
height range; h >= 3000 is the binary receiver's actual dispatch boundary.
This proves the local binary beta=2 capacity premise at this pin. It does not
discharge complete selected storage, tape, source-correctness, analytic-recovery,
integer-recovery or supplier-admission obligations.

## Literal production bindings

`installations.py` defines `BINARY_C = 4484997569314581 / 2^60`.
`raw_binary_stage.binary_recipe` passes that value as `Recipe.trial`, so

\[
t=1-\mathrm{BINARY\_C}
=1148436507037532395/1152921504606846976>3/4.
\]

`Recipe.open` sets L=2^15=32768, U=2 floor(N/(2048*134))<N,
volume V=N^6, and width B=N^92. It passes the fixed binary q=104904 paid
labels and `delay_base = 2^max(19,(q-1).bit_length()) = 2^19`.
`Plan` uses scale step 6/5 and bins e=L,L+2,...,U-2. These are constructor
bindings, not approximations to a generated calendar. The binary target and
paid labels have maximum target 127 and minimum paid grade 1, as authenticated
in the accepted production binding and independently enumerated here.

The authenticated inherited `powered.py` defines `bit_word(targets,paid)` as
`PoweredWord(134,tuple(targets),tuple(paid),480,16,10,11)`. Thus the ambient 134
is a literal source constant. `BinaryWord` reads those unchanged target/paid
tuples directly; it does not invoke a powered native word. The full nested
archive provenance is retained in `dependencies/powered-origin.json`.

## Replica count from the accepted mass enclosure

The numerical proof applies to this exact dyadic t, V=N^6, actual grid
`g=2^max(256,64*N.bit_length())`, and all nonempty mass calls. Its accepted
production grade check covers every endpoint by X=2064N and gives the
one-sided error Delta<1/4. Each bin's actual
`count[e]=ceil(mass(e,e+2)[1])` is therefore less than its ideal mass plus 2.
The ideal bin masses telescope, and the number of bins is less than U:

\[
\sum_e\mathrm{count}[e]<\frac{N^6}{tL^t}+2U.
\]

Since t>3/4>1/2 and L>=16, tL^t>(1/2)sqrt(L)>=2>1.
Also U<N and 2N<=N^6 for N>=2. Therefore

\[
\boxed{\sum_e\mathrm{count}[e]<2N^6.}\tag{2}
\]

This is the only use of the imported numerical enclosure. Allocation funding
and source correctness remain separate contracts of a successful Plan.

## Delay bound from the exact source level loop

The Plan level loop starts with `level=0, limit=L` and, for increasing bins e,
multiplies limit by 6/5 while `limit*(6/5)<=e`. Thus the invariant at the end
of each bin's loop is

\[
L(6/5)^{\ell(e)}\le e,\qquad
\mathrm{delay}[e]=(2^{19})^{\ell(e)}.
\]

The exact integer inequality

\[
6^{76}>2^{19}5^{76}\tag{3}
\]

gives

\[
\mathrm{delay}[e]\le(6/5)^{76\ell(e)}
\le(e/L)^{76}<(N/L)^{76}.\tag{4}
\]

The first inequality is equality when level is zero. No logarithmic rounding
or floating-point estimate is used. For h>=1024, q+1=104905<N. Using L>=1,
N^76>=1 and (4),

\[
q\,\mathrm{delay}[e]+1<qN^{76}+1
\le(q+1)N^{76}<N^{77}.\tag{5}
\]

Combining (2) and (5) yields the inclusive context estimate

\[
C_* =\sum_e\mathrm{count}[e](q\,\mathrm{delay}[e]+1)<2N^{83}.\tag{6}
\]

## Source-bound owner capacity

The separate census gives capacity<=B+22339 C_* for a fresh allocator.
Since 22339<2^15 and N^9=2^(9h)>2^16 at every h>=1024,

\[
22339 C_*<2^{16}N^{83}<N^{92}=B.
\]

This proves (1). The census includes input zero owners, suspended inner owners,
outer query clones, opening/closing microsteps and cross-context loan custody.
The free-first allocator turns its live bound into historical owner capacity.

Physical byte reserve on a reused fixed head remains
`max(K0, V_field*capacity)` with K0 its initial reservation; zero-on-return does
not erase historical capacity. Other compiler banks, public cold slots,
work tapes, pinned headers and external input/output storage are accounted
in their respective composition and local-byte theorems, not in (1).

## Evidence and scope

`check_corollary.py` authenticates all dependencies, captures the actual
Recipe.open arguments at several heights without constructing a Plan, evaluates
the actual Plan level/count expressions against exact fixtures, and checks the
integer inequalities above. It rejects an insufficient delay exponent, a
reversed delay inequality and a tiny-height attempt to use the production slack.
The universal proof is (2)--(6); finite height checks establish source binding,
not extrapolation to arbitrarily large heights.

Credit for the fixed graph, caller and transport belongs to the retained source
authors; the mass enclosure and its independent reviewers retain their stated
credit. This census and corollary were prepared for Jerry Chen with substantial
OpenAI Codex assistance. No selected kappa or complete premise changes.
