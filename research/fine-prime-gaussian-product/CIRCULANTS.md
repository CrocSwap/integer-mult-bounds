# Rounded circulant blocks in original padded coordinates

Each row index is a padded output coordinate. Each column index is a padded input coordinate. At output k and selected column q_j, put ρ=t/s, λ=s/t, θ=ρ−1, β_j=ρj−q_j. For all signed lifts h=q_j−k+mt, the broad coefficient is
```
α⁻¹ sum exp(−πλ²(h+β_j)²/α²).
```
For k=q_i the narrow coefficient, *before inverse or D*, is
```
sum exp(−πα²((h+β_j)²−β_j²)).
```
For the first identity, j−λk=λ(q_j−k+β_j). For the second, ρ(j−i)+β_i=q_j−q_i+β_j. Adding one source period shifts h by t in both. The global augmented broad map has an identity column on each hole. The narrow map has the identity on the holes as a direct summand. D on the holes is one. Access to each source uses its original q_j.

For a fixed output row, a selected input and a periodic lift determine a unique integer h. Summing over |h|>W gives a tail of at most `2A exp(−πg(W+1/2)²) (1+1/u)`, where `u=3g(2W+2)`. Here `(g,A)=(λ²/α²,1/α)` for broad and `(g,A)=(α²,max_j D_j)` for narrow. Indeed the ratio for successive radii is at most `exp(−πg(2W+2))≤1/(1+u)`. The initial Gaussian uses the fact that `|h+β_j|≥|h|−1/2`. The implementation rounds the first omitted Gaussian outward and includes the two tails once per row. It rounds each retained coefficient by outward fixed-point arithmetic and sums every integer h in the truncated window, including repeated residues when 2W≥t. This gives `RawAxis.broad_error` and `RawAxis.narrow_error` in induced infinity norm. The code also bounds the diagonal error and residuals independently of any Fourier transform.

## Pure blocks

Consider one aligned padded block of length B, centered at its integer position `m=first+B//2`. Purity means that every block coordinate is selected by q. Since q is strictly increasing by steps at least 1, checking the first and last positions of B consecutive source coordinates is sufficient. Thus `q_j=j+c₀` for a constant c₀ on that interval. Put x=q_j−m, y=k−m, h=x−y, δ=(1−λ)m−c₀ and β*=ρδ. The number β* is the true centered phase at the selected anchor. Set σ=−δ(1−θ). The broad unperiodized term factors into a row weight, Toeplitz weight and column weight:
```
row(y)   = α⁻¹ exp(π [λ(1−λ)y²+2λ(δ+σ)y−δ²+λσ²]/α²)
kernel(h)= exp(−πλ(h−σ)²/α²)
col(x)   = exp(−π [(1−λ)x²+2(δ+λσ)x]/α²).
```
Their exponents sum to `−π (x−λy+δ)²/α²`, as required. The narrow factors are
```
row(y)   = exp(πα²θy²)
kernel(h)= exp(−πα²(ρh²+2β*h))
col(x)   = exp(−πα²θx²).
```
To check the narrow identity, substitute `β_i=β*+θy`, `β_j=β*+θx`, and `x=y+h` in the unperiodized original exponent. The gauge-free shifted Toeplitz identities come from the vendored GAUGEFREE-INTERIORS proof and its cited predecessors.

Construct the local cyclic J by periodizing over B the signed kernel restricted to |h|≤W. If multiple h have the same residue mod B, sum all their coefficients. The kernel is indexed by **column minus row**. A routine for conventional convolution indexed by output minus input must reverse its kernel. Round the complete folded coefficient once after summation. For suprema U,C,V of the positive ideal factors and entrywise errors du,dc,dv, the computed matrix differs from the ideal truncated circulant by at most
```
min(2W+1,B) [du C V + (U+du) dc V + (U+du)(C+dc)dv].
```
This bound includes data coefficient rounding and finite setup error. The generator verifies that the two diagonal gauges have no zero. Only compression takes the inverse of the circulant. For narrow blocks the generator computes that inverse in exact rational arithmetic and verifies its cyclic convolution with the delivered kernel. The rational inverse stays in private setup. The generator serializes its dyadic spectral table. The arithmetic bound includes that quantization.

Suppose 2W<B. Mark the first and last W positions of every pure block as boundaries and mark all positions of all impure blocks. For h with |h|≤W, any pair crossing a block boundary consists of two boundary positions. The same is true of a cyclic B-wrap inside a pure block. Outside E×E the global signed truncation therefore agrees with the ideal unwrapped local term, and there is exactly one relevant periodic B representative. Define those entries of the reference by the *same exact product* of the delivered rational local factors, rather than independently rounded direct weights. On E×E use the global coefficients computed at true period t. The new Q−J then vanishes **exactly** outside E×E. This argument includes the periodic wrap at t. If 2W≥B, mark every position of that block as a boundary, use original-period Q for all entries, and do not confuse B-period with t-period. The global induced error is at most the global raw bound plus the worst applicable local row bound. Normalized operator and inverse perturbation must use this chosen Q, not a different global rounding.

At `B=O(p₀^(9/8))` the largest logarithmic gauge or inverse-gauge size is `O(α² θ B² + polylog p₀)=O(p₀^(1/4) log p₀)`. The implementation executes one axis at a time. The expansion never inverts its broad kernel. No lower bound on its eigenvalues is required. For the narrow kernel put a=πα². At its selected anchor |β*|≤1/2. The exact coefficient at h=0 equals one. The two terms h=±1 have total at most exp(−aθ)(1+exp(−2a)), since cosh is increasing for nonnegative arguments. For |h|≥2 the exponent is at most −a(h²−|h|). Summing the resulting geometric bound gives a total below 3exp(−2a). Thus the full nonzero mass is at most exp(−aθ)+4exp(−2a). Truncating terms cannot increase that mass. Positive terms folded on the diagonal only increase the row gap. In the fine family a=Θ(log p₀), a≥4log(16p₀) and θ≥1/(4p₀²). The gap 1−exp(−aθ)−4exp(−2a) exceeds 1/(8p₀²) eventually. All B folded entries together acquire at most B·2^(−2q+o(q)) error from the actual setup and coefficient grids. Thus the delivered narrow circulant has strict row margin at least 1/(16p₀²) and inverse row norm at most 16p₀² eventually. Its exact rational inverse exists. The delivered diagonal gauges have absolute logarithms O(p₀^(1/4) log p₀). The small finite configurations use the computed inverse and the complete page bound. Exact rational setup including a cubic local solve is `2^O(ell)poly(p₀)` across all axis blocks because B is polynomial in p₀ and local rational minor lengths are polynomial.
