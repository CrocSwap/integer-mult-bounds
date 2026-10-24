# Local finding: free completion of the retained 4856 word is obstructed

Status: DONE, outputs-only; no public claim, commit, push or PR. No kappa gain.

Source producer: PR4856, 0970de4ec97fc942e6202403ffd7586d19559391.
Source algebra/faithfulness: PR4920, 7eb4ef5251f7ba96c7e5d78c42fc98e66b7be4ba.
All retained inputs have SHA256 and full Git blob pins in SOURCES.json.

The exact 25-block GROUP-ALGEBRA expansion matches both literal native raw
and fused schedules, retaining absolute phases and outside-tensor scalars.
M00 contains a unique projective X0 class with coefficient 1 and grade0;
FB^4 cannot cancel it within that class. PR4920's separating-tensor proof
makes grade projection faithful at all sufficiently large widths. The
pi3 projection has zero first row/column and a lower4-by-4 triangular
block with pure unit AD diagonals. Its image from B_f^5 into A_(3),f^5
therefore has dimension exactly4*d, versus5*d for five independent pure
rank3 targets. Rectangular free pre/post linear maps, clean/copy/drop/reset
buffers and saved-input identity bypass cannot increase that rank. No
invertibility or scratch-restoration premise is needed. The supporting
pi0 rank/nullity proof covers invertible controllers with restored dirty
identity scratch. Arbitrary cross-output ADD is included in both arguments.

The source invoice remains 2H1+4H3,24 monomial passes, 10 ADD passes. Paying
even one additional H1 makes the five-target optimistic moment nonpositive
throughout0<=C<1. More strongly, any five pure Gaussian targets of rank at
most3 have at most four rank3 jobs, hence reward<=4*3^t+2^t and moment
<=2^t-2<=0 for0<=t<=1. This is strict at every positive C=1-t.
The zero-extra completion question is closed only in the
declared fixed finite columnwise Clifford alphabet; changed words,
nonmonomial helper resources, arbitrary width-specific address operations
outside that alphabet remain outside the result. One complete invocation
of the fixed producer is in scope. Prefix taps, saving intermediate
producer states and free gates inserted within that word are excluded.

Reproduce from the worktree root:

    python3 -I -W error -B outputs/free-completion-4856-grade-gate-20261023/check_grade.py
    python3 -I -O -W error -B outputs/free-completion-4856-grade-gate-20261023/check_grade.py

Controls: opposite scalar phase shares a projective class but not an exact
group element; omitting A^2 removes its unique class; target K has grade3
while X0 has grade0. Mutating an actual ADD sign and omitting the actual
closing bank0 A each fail group-algebra endpoint binding. RESULT.json retains every exact group matrix,
coefficient, branch label and grade. Independent bounded read-only reviews
passed with no correctness findings, including final-byte confirmation by
sol_1337_contact_frontier. See AUDIT.md and the exact reviewed-file hashes
in AUDIT.json. RUNS.json records final normal/O runs in2.118/2.277 seconds.

Smallest next gate: demand an actual changed physical resource or paid
profile with complete ownership and bill. Further cyclic norm/precision
optimization or unchanged-word free-controller search cannot remove this
obstruction. Parent owns any later publication decision.
