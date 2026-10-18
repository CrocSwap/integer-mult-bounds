# Exact signed batch and restored recursive children

At any point let
`z=z_initial+sum_j q_j B_j x_j`. A B_j query updates only q_j. An A_i query
of sign s adds `s A_i z_initial+sum_j s q_j A_i B_j x_j` to y_i. Therefore
the literal word is correct for free noncommuting linear maps precisely when
the final q is zero, each output's signed readout count is zero, and its
signed sum of q vectors is row i of H. `verify.py` checks these integer
conditions directly from the word, separately from the path constructor.
They also prove restoration on arbitrary dirty inputs at every L.

The constructor finds two-difference representations for outputs 0,1,2 and
a one-difference representation for output 3. Both sides of every difference
are actual connector states along the same eight-step path. Inserting the
negative and positive readouts at those respective visits gives the desired
row, irrespective of which visit comes first. Readouts do not modify z or a
source; distinct output ports and restored child scratch permit them at the
same visit. All fourteen output calls are counted, including repeated taps.

For an ordered product F with first half B applied before second half A,
borrow an arbitrary distinct dirty row u. The positive product shear is

```text
u += B source; target += A u; u -= B source; target -= A u.
```

Linearity cancels the initial u contribution, leaves target increased by
A B source and restores u. Sources and all other arrays are unchanged.
This uses no inverse of A or B. Every negative product call is the literal
reverse of its positive primitive program, with each additive sign inverted.
Induction proves exact restoration and the recurrence
`C(F)=2C(B)+2C(A)+d_node`, with one fresh dirty row per active recursion level.
Pool rows never overlap the eight data rows or the batch connector.

`verify.py` lowers every query into literal single-factor additive shears.
Its separate formal replay gives each of the twelve initial dirty rows an
independent symbol and treats every matrix factor as a free noncommuting
letter. The full polynomial endpoint must have only the sixteen demanded
Hadamard product terms and the initial output symbols; all eight non-output
rows restore. Appending the literal inverse must restore all twelve rows.
This is an exact algebraic certificate for the finite emitted factor lists;
the induction above explains the general product-child interface.

The comparison words implement the identical H endpoint. Source stars hold
each B_j once while updating all outputs; output stars form each requested
signed source sum separately. All of their connector restores, output dirt
subtractions, product children and inverses are emitted and counted. The
unit-leaf lengths give complete totals 238, 364 and 526, with the same four
borrowed dirty arrays. Nonuniform child-price formulas and every further
adapter/dispatch/tape obligation are retained explicitly in README.md.

No query minimum is asserted. The support lower bound of sixteen queries
does not by itself characterize signed four-by-four matrices, and the failed
ten/twelve-source-step screenings do not prove that eighteen or twenty
queries are impossible. The new evidence is the literal 22-query construction
and its complete 238-call realization in the priced exact interface.
