# One-slot disjoint-mask fusion forces a common projector

Fix either signed specialization q = +1 or q = −1 and set all 17
independent body variables to one. An even IDLE_ONE with mask S and
role r is a factor of the form

$$
I+\left(\prod_{j\in S} z_j-1\right)E_{rr},
\qquad E_{rr}=e_r e_r^{\mathsf T}.
$$

At this specialization the factor is identity. Let F be the complete
specialized operator and let P be the invertible prefix immediately
before this factor. Its contribution to the left-normalized derivative
$F^{-1}\partial F/\partial z_j$ is $P^{-1}E_{rr}P$ when j is in S,
and zero otherwise.

Delete two retained even idles with nonempty disjoint masks and
insert one even idle with their union at an arbitrary clock and role.
All deleted and inserted factors evaluate to identity. Every unchanged
factor has the same specialized prefix and suffix, so its derivative
contribution cancels when comparing the two formal caller words.
Choose one body variable from each original mask. Equality of the
formal operators forces the single normalized projector of the new
idle to equal both old normalized projectors. Thus the two old
normalized projectors must agree, irrespective of the insertion
clock or role.

For earlier and later old coordinate projectors $E_{ss}$ and $E_{tt}$
with intervening product M, this condition is equivalent to
$E_{tt}M=ME_{ss}$. The primary gate checks the off-axis components
of $Me_s$ and $e_t^{\mathsf T}M$ after reduction modulo 65521.
It verifies that the modulus is prime and that the used rational
denominators and gates are units. A nonzero outside component
certifies an exact failure. The independent gate uses exact rational
prefixes and their inverses to compare the original conjugated
projectors directly. A coordinate swap is a positive transport
control. A shear changes the conjugate and is rejected.

The condition allows non-diagonal intermediate conjugates. It keeps
the other caller events fixed and assumes a single one-role idle
whose stage derivatives use the same projector. Repeated stages,
odd-idle replacements, multi-role children and other changed
operators require different arguments.
