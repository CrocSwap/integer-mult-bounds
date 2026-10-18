# Packing scope for the twelve-call dispatch

Fix the three admitted suppliers, the selected 59 JP8 / 12 J249 / 1 CK calls,
all required helper roles, existing geometry and finite moment formula.
There are 16,128 owner segments, of total capacity 387,072 and maximum capacity
48. Required helper widths total 280,032, so every complete legal assignment
leaves 107,040 = 2230·48 unused units.

For 0 < q < 1 the variable idle contribution to the moment is proportional to
Σ g^(1−q), with 0 ≤ g ≤ 48. Strict concavity shows that transferring mass from
a smaller positive gap into a larger gap below 48 decreases this sum. Repetition
leaves only full gaps of 48, since total unused capacity is divisible by 48.
This is a relaxation of the physical and timing constraints. The verified
literal map realizes 2230 gaps of 48 and therefore attains the relaxed lower
bound, minimizing the moment among all assignments with these fixed inputs.

The positive moment root is below 1: the fixed supplier atom count alone
already exceeds the normalization denominator 7168 at q=1. All paid ranks are
below 73, so the moment is strictly increasing in q. Thus this assignment
maximizes the moment-limited exponent ceiling for the fixed inputs, while the
reported decimal remains an exactly verified lower bound on the root conversion.
Other admission and inherited outer assumptions remain separate.

This proof does not compare other dispatch counts, other suppliers, schedules,
geometries, or different mathematical constructions. The count12 was nominated
by a numerical search, then its concrete assignment was certified exactly.
