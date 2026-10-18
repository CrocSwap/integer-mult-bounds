# Exact arithmetic identity

For x=p/q, q>0, let c_j=24!/j!. The retained polynomial is S24(x)=sum(x^j/j!, j=0..24). Its exact integer numerator over D=q^24*24! is A=sum(c_j p^j q^(24-j)). Starting A24=1 and descending j=23..0, the update A_j=p*A_(j+1)+c_j*q^(24-j) gives that numerator. The code simultaneously accumulates q powers and c_j; no intermediate Fraction normalization is needed.

The retained upper tail is (x^25/25!)/(1-x/26). With R=26q-p>0, S24 plus that tail equals

`(25*A*R + 26*p^25) / (25*D*R)`.

The new lower result is floor(DYAD*A/D)/DYAD; the new upper result is ceil(DYAD*(25*A*R+26*p^25)/(25*D*R))/DYAD. These are exactly the original final floor/ceil operations on exactly the same rational expressions. There is no new enclosure, lower precision, truncated degree or smaller tail. The identity applies to every exact rational 0<=lower<=upper<1/10, not only the fixtures.

The whole-moment adapter retains the original logarithm, rank weights, optional inherited surcharge and final rounding. Replacing each exponential by its identical returned pair leaves every accumulated rational and the resulting moment pair identical. Frozen source code is unchanged; this is an opt-in arithmetic adapter, not supplier admission or a new multiplication theorem.
