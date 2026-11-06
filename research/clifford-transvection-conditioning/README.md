# Three-qubit Clifford Gram condition bound 807

Scoped written proof with exact finite corroboration, produced by Nick Petalas.
For the full projective three-qubit Clifford alphabet and every integer `f >= 10`,

\[
 \frac{2835}{131072} I\preceq H_f\preceq\frac{2287845}{131072} I,
 \qquad H_f(a,b)=\left(\operatorname{tr}(U_a^*U_b)/8\right)^f.
\]

The sufficient uniform spectral condition bound is **807**. This improves the
6,456 bound of [alephnan's PR6714](https://github.com/CrocSwap/integer-mult-bounds/pull/6714):
the lower endpoint increases sixfold and the upper endpoint decreases by a quarter.
It is a sufficient interval; the exact spectrum and its sharp endpoints remain open.

The new step is two affine inequalities on its thirty quotient-character types.
Summing them against an actual irreducible's nonnegative multiplicities and using
the predecessor's transvection trace bound proves the improved interval at width
ten. Its Schur-product argument propagates that same interval to every larger width.
[PROOF.md](PROOF.md) gives all hypotheses, the exact rational certificate, and
attaining mixtures for the relaxation. This contribution does not improve the
already proved threshold ten or the selected multiplication exponent.

## Reproduce

From the repository root with CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/clifford-transvection-conditioning/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/clifford-transvection-conditioning/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/clifford-transvection-conditioning
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/clifford-transvection-conditioning --check-source-history
```

Another CPython 3.12 path can replace the absolute interpreter path. The direct
verifier prints `PASS_CLIFFORD_TRANSVECTION_CONDITIONING` inside a generated JSON
receipt with all thirty pairs of affine residuals, both orbit-specific bounds,
the complete relaxed-vertex results, seven rejection controls, and every package
file's SHA256. It writes no files. The registered runner executes both normal and
optimized commands; all checks remain active under optimization.

The finite arithmetic certifies the **new supporting inequalities and optimization**.
It does not rerun the predecessor's character extraction, width-nine decomposition,
threshold proof or native program. Exact source data are retained unchanged under
`source/`, with hashes and public commit links in [ORIGIN.json](ORIGIN.json).
[VALIDATION.md](VALIDATION.md) records executed checks and replay limits.

## Claims and limitations

The uniform implication rests on the written proof and the cited mathematical
inputs of PR6714, including its identification of the published character table.
The upper and lower relaxed optima are attained by convex mixtures, which need
not correspond to actual irreducibles. No actual spectral endpoint or exact
condition number is claimed. The 92,897,280-square Gram matrix is not constructed.

This is a native-algebra side result. No physical caller, coefficient preparation,
dirty restoration, precision/tape bill, complete recursive invoice, selected
supplier admission or complete multiplication theorem is supplied. All five
selected framework assumptions retain their status. No selected cold replay,
Lean or Docker run was needed. Independent human and formal proof-kernel review
are unclaimed.

The `formal-interface-lemma` card is explicitly changed to this written spectral
question. Its selected-source orientation passed; its proof-assistant acceptance
gate is not claimed. Source-bound numerical data and classical representation
and Schur-product facts remain credited premises.

## Open next questions

- Determine the actual width-ten spectral endpoints. Start with the two
  quadratic-form stabilizer representation decompositions. Their additional
  multiplicity constraints are the missing input; the relaxed witnesses do not
  establish actual attainment.
- Add one more phase-correct conjugacy-class trace constraint without computing
  the whole even-sector table. Start by counting its fixed quadratic forms.
  The single-transvection relaxation is solved exactly here, so a stronger
  bound needs additional representation information.

The same questions and blockers are structured in [TASK.json](TASK.json).

## Related open work and credit

[PR6714](https://github.com/CrocSwap/integer-mult-bounds/pull/6714) studies this
same alphabet and Gram matrix. It proves threshold ten and supplies the cited
multiplicities, trace bound and sufficient interval. This package answers part
of its second open question by improving the interval, without rechecking those
results. Its threshold and all exact source quantities are retained as inputs.

[PR6718](https://github.com/CrocSwap/integer-mult-bounds/pull/6718) gives a
written review of PR6714's even-sector argument and old constants. It is
separate review coverage and does not derive this improved certificate.

Credit alephnan for PR6714's theorem and representation-theoretic reduction;
Chin-Yen Lee, Wei-Hsuan Yu, Yung-Ning Peng and Ching-Jui Lai for the published
character table; Ali Romman for the Clifford trace/pointwise framework; MatShep
for the sharp one- and two-qubit results; and Nick Petalas for the earlier lower
bound and open question cited by PR6714. Affine linear programming, tensor
reciprocity, character bounds and Schur products are classical. The new result
is the improved source-specific certificate and its universal conditioning
consequence. New work is Apache-2.0.

[Advance CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19440708).
