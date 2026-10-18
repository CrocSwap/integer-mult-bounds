# Directed integer Taylor enclosure

Let S be the positive integer grid denominator and let 0 <= l <= u < 1. Set A=floor(S*l), B=ceil(S*u). Start lower and upper Taylor terms and sums at S. For j=1,...,N-1, update the lower term by floor(t*A/(j*S)) and the upper term by ceil(t*B/(j*S)), adding each to its respective sum.

Induction proves lower_term/S <= l^j/j! and upper_term/S >= u^j/j!: all multipliers are nonnegative, A/S <= l <= u <= B/S, and rounding is directed outward. Summing preserves the inequalities. The exponential series has only nonnegative terms, so the finite lower sum is a lower bound for exp(l).

Write U=B/S, and let T be the last upper integer term. The first omitted term is bounded by (T/S)*U/N. All subsequent term ratios are at most U/(N+1), so the omitted tail is at most

    (T/S)*U/N / (1-U/(N+1)).

In grid units this is T*B*(N+1) / (N*(S*(N+1)-B)). Its denominator is checked positive. Rounding this quantity upward and adding it to the upper sum gives an upper bound for exp(u). This remains valid when B/S rounds to 1; N>=2 suffices. The current callers enforce stricter argument ranges.

The dyadic and decimal implementations independently express the same enclosure argument. They retain distinct logarithm algorithms. The reference audit compares these enclosures with the predecessor unrounded rational Taylor algorithms at sixteen cases, including a narrow input interval, zero, tiny positive inputs and values near the allowed boundaries. Five invalid arguments are rejected; omitting the upper tail fails a reference inequality. These finite controls supplement the general induction above; they are not the proof of validity for all arguments.

The two moment engines must still accept each nominated lower endpoint and reject its next grid point. The logarithm oracle, complete finite admission, outer inequalities and inherited theorem assumptions remain separate obligations. Directed rounding may widen intervals; it never licenses rounding a failed bound inward.
