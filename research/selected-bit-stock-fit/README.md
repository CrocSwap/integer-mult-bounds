# Sharp borrowing fit for the original selected BIT reserve

The conditional reserve defined by [Adam Gall's PR2084](https://github.com/CrocSwap/integer-mult-bounds/pull/2084)
and [Nick Petalas's PR2120](https://github.com/CrocSwap/integer-mult-bounds/pull/2120)
has least uniform integer stock-fit cutoff **311305**, over the domain below.
At width 311304, a certified prime makes the borrowed part exactly half the
width, so strict fit fails.

This is a new stock-fit theorem for that prescribed reserve. It does not
implement its packet/compiler or completed-leaf assumptions, replace the
selected bootstrap cutoffs, prove their other size conditions, or change kappa.
The selected exponent and every frozen predecessor remain unchanged.

## Object, domain and source boundary

Let `P=28425`, and let `q>2^80` be a prime. Define

```
D(e) = 0                         for 0 <= e < 64,
D(e) = 1 + D(42*floor(e/64))      otherwise,
W_q(w) = P * |GL_64(F_q)| * q^(4096*(w-1)),
S(e,w) = W_q(w)^D(e).
```

For integer `e>=1`, real `0<s<=1/500` and `w=ceil(e^s)`, put
`k=ceil(log_q S(e,w))`.

**Theorem.** For every such `q,s` and every integer `e>=311305`, `k<e/2`.
No smaller integer cutoff works uniformly over this domain.

PR2120 explicitly chooses stock from the **original width e**, before the
borrowed width or body is chosen. That is the reserve studied here. The
smaller post-borrow body does not enter D. The nine additional work roles remain
in P, all high matrix fibers remain in W, and the leaves' zero extra external
factor remains conditional on their completed ordinary interface.

The source-pinned PR1094 selected record and assembly cite the tuned PR589 BIT
receipt. They identify the ordinary producer as dimension 64, largest child
42, and 28425 physical roles. The separate complex dimension 73 only
constrains the atom exponent. The authenticated PR1087 assembler defines

```
s = min(bit_lower, (1-10^-24)*complex_lower) - 10^-27.
```

The verifier reconstructs both native and conservative versions and proves
`0<s<=1/500` for each. Their exact values are in [RESULT.json](RESULT.json).
It reads, but never executes, the archived assembler. Historical dimension 67
in the generic cover source supplies no numerical parameter to this theorem.

The arithmetic theorem ranges over **all primes above 2^80**. Physical use
also requires the recipe's prime exclusions and retained interfaces. Those
exclusions are not checked for the sharpness witness. Thus the stated
minimality is not a minimal cutoff for a narrower eligible-prime set, nor a
minimum reserve over alternative constructions.

## Proof

### The finite staircase

The invertible local-ring matrix count gives

```
W_q(w) = P * q^(4096*w) * product_(i=1)^64 (1-q^-i).
```

This formula and the stock construction are credited predecessor work.
Because `P<2^15` and `q>2^80`,

```
log_q W_q(w) < 4096*w + 3/16.
```

For `2<=e<2^20` and `0<s<=1/500`, `1<e^s<2`, so `w=2`.
At depth d, therefore,

```
k <= 8192*d + ceil(3*d/16).
```

The exact depth thresholds are `b_1=64` and
`b_(d+1)=64*ceil(b_d/42)`. Indeed
`42*floor(e/64)>=b_d` holds exactly when
`e>=64*ceil(b_d/42)`. Hence depth d occupies the integer interval
`[b_d,b_(d+1)-1]`. This inverse-threshold method follows Sricharan Vagvala's
PR2105 and PR2120; the new use is an exact strict borrowing-fit boundary.

Only four intervals intersect `[311305,2^20)`:

| Depth | First width in this domain | Last width | Upper bound on k |
|---:|---:|---:|---:|
| 19 | 311305 | 405311 | 155652 |
| 20 | 405312 | 617663 | 163844 |
| 21 | 617664 | 941247 | 172036 |
| 22 | 941248 | 1048575 | 180229 |

In every row the first width exceeds twice the bound on k. The inverse
threshold identity proves coverage of every integer in the finite domain;
this is not an inference from sampled widths.

### All later atom-width jumps

For `e>=2^20`, choose integer `t>=20` with `2^t<=e<2^(t+1)`.
The existing two-level contraction `2*42^2<64^2` gives
`D(e)<=2*ceil(log2 e)<=2(t+1)`. Also

```
w <= 2*e^(1/500) < 2*2^((t+1)/500),
k < A(t)+1,
A(t) = 2*8193*(t+1)*2^((t+1)/500).
```

The extra unit covers the ceiling in k. At t=20,
`21/500<1/20` and `9^20>2*8^20`, so

```
A(20)+1 < 2*8193*21*(9/8)+1 = 1548481/4 < 2^19.
```

For every integer `t>=20`,

```
A(t+1)/A(t) <= (22/21)*2^(1/500) < (22/21)*(9/8) = 33/28 < 2.
```

Induction gives `A(t)+1<2^(t-1)<=e/2`. This covers every later e and every
ceiling jump in w. No floating-point logarithm or finite tail extrapolation
is used.

### Sharpness and primality

Take `q*=15*2^78+1=4533471823554859405148161` and `e*=311304`.
The depth thresholds give `D(e*)=19`; throughout the stated s domain,
`w=2`. Write
`B=product_(i=1)^64 (1-q*^-i)`. Bernoulli's inequality gives

```
B^19 >= (1-1/q*)^1216 >= 1-1216/q* > 1/2.
```

The exact integer comparisons

```
2*q*^3 < P^19 < q*^4
```

therefore imply

```
q*^155651 < W_(q*)(2)^19 < q*^155652.
```

Thus `k=155652=e*/2`, violating strict fit. Combined with the upper proof,
this proves minimality of 311305 as a uniform integer cutoff.

The certificate proves primality, rather than using a probable-prime test.
For `a=11`, it checks

```
a^(q*-1) = 1 mod q*,
gcd(a^((q*-1)/2)-1, q*) = 1,
(2^78)^2 > q*.
```

For any prime divisor p of q*, the first two conditions force the order of a
modulo p to have 2-adic valuation 78. Hence `2^78 | p-1`, making every prime
divisor greater than `sqrt(q*)`. A composite q* cannot have that property.
Sagar Thakrar's PR2343 already used this prime for its body-dependent reserve.
Aakash's PR2324 supplied the modular prime-certificate method with a different
prime. Neither the prime nor that method is claimed as a new discovery.

## Relation to existing work

Scientific base is canonical main
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4.
This refines the `selected-stock-envelope` card after overlap found the
conditional coefficient and later-stage composition already covered.
[The coordination claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2114#discussioncomment-18951283)
records the precise object and bounded method.

- PR2084 at `8001a23b003bec5dff5e61edec907b652c475932` supplies the conditional
  complete-packet stock, depth/restoration implication and coefficient 8194.
- PR2120 at `378593574261e0b0915e7e8a83147aa640274fc8` refines that coefficient
  to 6748 and explicitly fixes the original-width stock used here.
- Aakash's PR2324 at `0ec8a26572069b6109decadd488b9770944a4296` proves a sharp
  cutoff of 311311 for Jose Manuel's **different PR2234 replacement reserve**.
  Its staircase/tail/prime method is the direct methodological predecessor.
  This package applies that method to a different prescribed stock; it adds no
  new abstract cutoff technique. The six-width difference is not a correction
  to that theorem.
- Sagar Thakrar's PR2343 studies a changed, body-dependent reserve and a
  fixed-point counterexample. No body-dependent stock is substituted here.
- PR2547 audits conditional later-stage completion. That separate implication
  is not discharged by a better fit bound.

Josie Elliston's PR1956/PR1965 and ToikY's PR1990 distinguish stock fit from
carried time constants and expose the original missing coefficient. The
selected PR589 word is DreamingOfClouds' work on eumemic's base and credited
compiler/hosting lineage. Rohan Arun's reviewed PR185/PR387 and selected
PR1094 assembly, on Jeremy Kothe's PR1087, supply the retained contracts.
The finite-cover source and their constructions remain credited predecessor
work. No predecessor Python checker is imported or run.

## Reproduction and evidence limits

Standard-library CPython 3.12, from the repository root:

```
python3.12 -Werror -B scripts/research_package.py --package research/selected-bit-stock-fit
```

Expected main marker:
`PASS_SELECTED_BIT_STOCK_FIT uniform_cutoff=311305 failure=311304 no_new_kappa`.
The registered commands run normal and optimized verification and tests.
The required receipt cannot be silently regenerated. An explicit
`--write-result NEW_PATH` writes a separate file and refuses overwrite.

The checker authenticates the five live inputs, the selected citation and the
archive member before semantic use. It certifies the staircase, dyadic-tail
inequalities and modular primality witness using integers and fractions.
Ten test groups include an independent bottom-up all-child depth oracle on
all 1048577 widths through 2^20, a separate full exact 64-factor GL product
check of the sharpness witness without the Bernoulli relaxation, exact
strict-half failure, a composite-prime control, rebound missing-work and
invalid-exponent models, every live input's corruption through the optimized
public CLI, receipt corruption/type drift, and non-overwriting regeneration.
These support the written all-width proof; they do not implement a full
q-adic tape caller.

No full selected cold replay, physical/native admission, complete H2 estimate,
formal-kernel proof, hosted CI pass or independent human review is claimed.
The theorem settles only fit for this prescribed conditional stock. Other
primitive thresholds can still prevent using 311305 as an algorithm cutoff.

Implementation bounds are explicit: five live sources at most 8 MiB each,
a 32 KiB manifest/receipt, at most 1024 archive headers and a 64 KiB consumed
member, 41 inverse-threshold steps, and 2049 forward steps for inputs below
2^1024. Tests allocate one 1048577-byte depth array, bound the exact GL-product
integers below 3.3 million bits, and use 30-second CLI timeouts with scoped
temporary-directory cleanup. Python managed allocation and fixed
unittest/import dispatch are deviations from Power-of-Ten rules 3
and 9. They are confined to these bounds; an allocation-free implementation
or static test runner would require a different runtime. Reassess capacities
before extending the domain. Warnings-as-errors, syntax compilation and
normal/optimized replays pass on Linux x86_64 / CPython 3.12.15. No separate
static analyzer was run; Ruff is unavailable in this environment.

## Open next questions

1. Which other size conditions of the actual selected stopped producer exceed
   this stock-fit threshold? Begin with PR1965's H2 quantifier and one emitted
   routing/leaf contract. This matters before substituting a fit-only cutoff
   into an algorithm. The complete physical implementation and its uniform
   constants remain the blocker.
2. Can a smaller, body-dependent reserve be used for the original selected
   packet contract? Start with a divisibility/restoration proof before solving
   the borrowing inequality, following PR2343's warning about equality cycles.
   A smaller numerical stock alone does not establish that contract.

Nick Petalas. Apache-2.0, following the repository license.
