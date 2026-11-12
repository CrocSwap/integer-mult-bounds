# Fixed-clock owned zero-rebirth observability

At each exact owned MOVE let Pᵢ be the moved row as a linear form on
the original public inputs. Let Sᵢ be the response to a unit defect
in that owned slot just after the original MOVE. Its observations
are the final public rows and the pre-write destinations of every
later COPY. Earlier guard coordinates in Sᵢ are zero by convention.
The exact normalized MOVE is the identity on its role value.
INIT and CLEAR reset a slot to zero. ADD, COPY and SCALE act with
the original signed rational coefficients. Evaluate COPY as a
linear assignment after recording its pre-write guard. This
relaxation is defined even when a candidate violates the guard.
A legal candidate must preserve both the observations and the
guard preconditions.

Replacing one MOVE by a CLEAR and zero INIT at the original clock
injects defect −Pᵢ in that slot. The full observation difference is
−SᵢPᵢ. Exact reverse covectors verify a nonzero coordinate of every
Pᵢ. A grouped forward sweep and separate per-site exact sweeps find
a nonzero final public coefficient of every Sᵢ. The independent
engine also pulls each first coefficient back from the final
public output. They agree on the first coefficient and number of
nonzero observations at each site. The sole original COPY is at
clock 33805. All 11 unit defects injected before that clock are
zero at its destination just before the write. No unvisited site
or single-site survivor remains.

## Two fixed-clock replacements

Let i < j and let g be the scalar response of the first unit
defect in the second owned slot just after the original MOVE j.
At that point the second slot would hold Pⱼ − gPᵢ after applying
the first edit alone. The second zeroing adds −Pⱼ + gPᵢ in its
slot. The resulting observation difference is

```text
−Sᵢ Pᵢ − Sⱼ Pⱼ + g Sⱼ Pᵢ.
```

If Pᵢ and Pⱼ are linearly independent, choose an input on which
Pᵢ vanishes and Pⱼ does not. The difference is nonzero because
Sⱼ is nonzero. If Sᵢ and Sⱼ are linearly independent, a linear
functional that vanishes on Sⱼ and is nonzero on Sᵢ leaves a
nonzero multiple of Pᵢ. Thus cancellation requires both pairs to
be proportional for any g.

Exact 2×2 prefix minors exclude 1,073 of 1,081 pairs. Each of the
other eight has a public observation that is zero in exactly
one full suffix column, proving suffix independence. The lead
screen's suffix support counts or first coordinates differ on
these same eight. The independent checks list exact differing
coordinates and coefficients. All pairs close before any
cross-transport or candidate computation.

This proof grants the normalized replacement even if the two
same-clock lifecycle changes would carry additional costs. A
successful normalized test would still require signed arbitrary-input
and adjoint equality, ownership, restoration, all-width physical and
compiler validity, and charged precision and tape checks.

## Directed price

A rank-r deletion saves 17 paid rank-r positions across the
signed caller. A single edit changes the paid count from 110,519
to 110,502. A pair changes it to 110,485. Productive count stays
22,461 and the rank surplus increases by 17 times the sum of
deleted ranks. No additional paid call is granted in the quote.

The strongest pair in the literal rank stock has ranks 6 and 5.
Its directed gross upper at the old crossing is 185.838303398540
raw and its complete margin upper at the fixed moonshot target is
45.956805594899 raw, both rounded upward. The predecode
all-site relaxation bounds gross credit by 1,896.702946936210 raw
at the old crossing and grants all 47 anchors independently.
The exclusions above certify zero realized saving in the tested
single and pair families. The all-site quote is a relaxation;
the pair theorem gives no conclusion for larger simultaneous sets.
