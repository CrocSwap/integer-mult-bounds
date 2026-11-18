# Residual certificates for the three interleaved helper bases

This audit reproduces the three requested restriction/split comparisons in
PR #7726. The chosen equations pass. The three alternate equations fail at
the stated coordinates. A separate count and rational price enclosure agree
with the complete invoice and the reported raw crossing bracket. No new
kappa is claimed. The selected frontier is unchanged.

The source constructor is retained. The new checker does not use the source
witness evaluator, graph propagation routine or price engine to accept these
equations or prices. It checks explicit formal residual identities and full
response solutions. This is a separate implementation of one mathematical
check, with a shared constructor. It is not a blind review, an independently
implemented construction, independent human acceptance or a full admission.

## Sources and exact scope

The scientific source is commit 3ba9094c54b61f424d2f98cd2c6ca64c01baf9d3.
Its deposited PR7713 graph has SHA-256
`16e99893a2c669467ce74f214e8eb5150402f0267aaa8d67aad5d870aa4d5c18`.
The source restores stable labels, then applies its rational edit journal.
All 55 package files are retained without change and have exact byte pins.
The copied source manifest describes the original package. Its full replay
also requires external main-branch inputs; that full suite is not run here.
The constructor used here needs only the retained files.

The restriction indices are zero-based 169, 137 and 91 for roles 1400, 1401
and 1409. The associated split indices are 252, 253 and 254. Each test starts
at the exact prefix, with the chosen restriction or its deposited alternate.
No test substitutes a later graph or treats a retired helper as zero scratch.
The split prefixes have 1510, 1511 and 1512 independent formal input symbols.
These stable namespaces include the source's isolated retired identity roles.
They are not the compact final public-owner count.

The local source/receiver equations are checked in their own orientations.
The first split is forward at chart 288. The other splits are transposed at
charts 288 and 306. The new checker forms the transposed scalar equations
directly and checks all source, receiver, pulse and output charts. A separate
heap-based topological sort checks every prefix for locality and cycles.

## Formal coefficient certificates

For each internal or terminal bank k, write its defining equation as
`E_k=z_k-sum_j a_kj*z_j`. Negative bank labels name independent entrance
symbols. All coefficients are exact rationals. A linear observation o has
entrance expansion s if the following formal identity holds:

`sum_k lambda_k*E_k = o-sum_i s_i*x_i`.

The certificate stores every nonzero multiplier lambda and every nonzero
entrance coefficient. The checker directly adds the defining equation rows
with these multipliers. It compares every resulting formal coefficient with
the right side. It does not propagate o backwards to decide acceptance.
Since every defining equation is zero during execution, the identity proves
the observation for all independent inputs. A missing nonzero coefficient
cannot be hidden by testing only selected inputs.

The generator uses reverse substitution to propose multipliers. It is not
trusted for acceptance. The checker uses the direct residual identity above.
It applies this check to the source-minus-receiver restriction, the readout,
the calibration-minus-return-decoder relation, and the two helper output rows.
There are 30 such identities with 10484 nonzero multipliers in total.

For a pulse b and entrance direction w, a response certificate gives a value
v for every nonzero bank. The checker substitutes it in every equation:
`v_k=b_k+sum_internal a_kj*v_j+sum_input a_ki*w_i`.
It does this in arbitrary bank-key order. The independently checked acyclic
graph makes the solution unique. The pulse check uses w=0. The steering check
uses b=0. Each is compared with the complete specified terminal direction,
including every zero terminal. The local readout and calibration must both
have zero pulse response for the chosen split.

The audit also proves that each restricted and split helper is an isolated
identity summand at its actual prefix. Its output row equals its own input.
Its unit input produces one at that output and zero at every other output.
These row and column facts are required for surrendering that helper in the
source's restriction and split proofs. They are checked here rather than
inferred from the final compact graph.

There are 24 response solutions, checked against 176320 defining equations.
The direct identity and response checks perform 4303065 exact coefficient
products. This count describes the finite check, not a tape or runtime bill.

## Reproduced comparisons

Both the chosen and alternate restriction equations are valid at their own
restriction prefixes. The alternate is not rejected merely because its
equation differs from the chosen certificate. The difference appears in the
later fixed split contract after the full intervening prefix is rebuilt.

| Restriction | Split and orientation | Alternate failure | First coordinate | Actual minus required |
| --- | --- | --- | ---: | ---: |
| 1400 | 294, forward, chart 288 | 16 readout coefficients | input 10 | 1 |
| 1401 | 288, transpose, chart 288 | 16 response coefficients | output 11 | -2 |
| 1409 | 302, transpose, chart 306 | 27 response coefficients | output 25 | 1 |

The required coefficient at each displayed coordinate is zero. Every other
coefficient is also compared. These failures match the deposited source
witness. They are counterexamples to these three alternate-prefix/fixed-split
combinations. They do not prove that the chosen relations are unique, optimal,
or necessary for every possible split.

The chosen splits have nonzero triples `(s*w,y*t,t_r)` equal to
`(2,1/2,3)`, `(-4,1,1)` and `(-2,1/2,1/2)`. Their readouts and calibrations
have zero pulse feedback. The full steering response equals the full pulse
response in each chosen case. Thus the local algebraic hypotheses checked
here support the source's stated split formula. The unchanged main operator
and the correctness of all other edits remain source premises.

## Complete invoice and independent price enclosure

The retained constructor rebuilds the complete graph with SHA-256
`ba59d5db17c40185c8608a734ced10135d8c041e432c3840e9034868781c31a2`.
The new count derives the 400 main roles from the deposited stable-label
map. The compact graph has 1260 public roles, hence 860 independent helpers.
It checks the binary chart bases and strict nesting of every paid route and
productive helper route, then counts their actual dimension differences.
It does not use the source's histogram function.

The native has 5810 paid transfers and 860 productive helpers. The literal
caller has 16 ordered native invocations. Direct event counting adds every
QUERY and signed or unit idle child at its port multiplicity. Direct counting
of all root diagonal declarations adds the root targets. This yields 96512
paid jobs, 17296 productive jobs and productive rank mass minus paid rank
mass 1328. All rank bins match the source receipt. This is a complete invoice
for the stated caller contract; its scalar endpoint and physical execution
remain inherited, rather than re-proved by counting declarations.

The independent price code uses only rational arithmetic. To bound log r,
write `r=2^k*y` with `1<=y<2`. For x=(y-1)/(y+1), use
`log(y)=2*sum_(j>=0) x^(2j+1)/(2j+1)`. The same series bounds log 2 with
x=1/3. After n=80 terms, the omitted tail is between zero and
`2*x^(2n+1)/((2n+1)*(1-x*x))`. All arguments lie in [0,1/3]. The code rounds
the resulting interval outwards to a rational grid of denominator 10^60.

For `a<=kappa*log(r)<=b<1`, the 17th-degree alternating partial sum for
exp(-b) is a lower bound; the 16th-degree sum for exp(-a) is an upper bound.
The terms decrease in magnitude. Multiply by r to enclose `r^(1-kappa)` and
round outwards to denominator 10^40. Add productive bounds and subtract paid
bounds with the correct interval endpoints. The final receipt rounds outwards
again to denominator 10^25. No floating-point result decides a sign.

The productive-minus-paid margin is strictly positive at .00378751509478
and .00378751509486, and strictly negative at .00378751509487. At the claimed
point it is about 3.0960942589e-8. RESULT.json contains the exact rational
enclosures. These signs confirm the source's claim-point margin and raw
bracket signs. The source's uniqueness, physical and compiler arguments are
not replaced by this finite price calculation. No extra root digits or new
construction are claimed.

## Controls and limits

Six changed certificates fail: a changed multiplier, a changed entrance
coefficient, a changed pulse value, a changed steering value, a changed helper
identity column, and omission of the role549 half-input term from the exact
role1409 source relation. The latter check concerns this relation at this
prefix; it is not a universal necessity claim about role549.

The price checker encloses the exact square-root control `4^(1-1/2)=2` and
returns exactly 1328 at kappa zero. Omitting all fixed root targets makes the
claim-point margin negative. Omitting fixed caller charges makes the upper
bracket margin positive. These controls show why neither side of the complete
caller bill can be omitted. They are changed invoices, not alternative valid
constructions.

All 55 source files, the certificate and the receipt are bound by exact
checks. Normal and optimized Python use explicit exceptions. No source file
is changed by replay. The generator is optional; it writes only the proposed
certificate and is not called by registered verification.

The source constructor, original parent graph, other journal edits, exact
caller operator, native Gaussian phases, all-column physical implementation,
stock/reset and compiler/analytic interfaces remain shared dependencies.
The complete original five-command source suite, selected cold replay, Lean
and Docker were not run. The selected .00363005817 and all five framework
assumptions remain unchanged. This contribution adds separately checkable
algebraic and price evidence. It does not promote the open source proposal.
