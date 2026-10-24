# Validation

CPython 3.12.2 on macOS arm64, standard library only. Each registered command
was timed separately from the worktree root with the exact interpreter
`/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12` and with `-B`.
These are single-run wall times for timeout sizing, not performance claims.

- `-I -Werror -B research/qutrit-mub-stability/verify.py` passed in 0.257 seconds.
- `-I -O -Werror -B research/qutrit-mub-stability/verify.py` passed in 0.250 seconds.
- `-I -O -Werror -B research/qutrit-mub-stability/test_package.py` passed in 1.504 seconds.

The direct verifier reported rank 16, kernel/equivalence rank 20, normal
squared singular value 3 and 972 derivative comparisons. The controls reported
seven rejections, successful optimized Git-free relocation, and unchanged
exported bytes. The registered package runner also passed all three commands.

The seven rejecting cases are an altered Jacobian entry, an incomplete
nine-direction equivalence space, changed pinned atlas bytes, a Boolean rank
receipt, an actual differential-sign code mutation with its code hash updated,
changed proof bytes, and a missing receipt. The actual code mutation fails
the mathematical rank gate before receipt comparison. These diagnose this
package's acceptance boundary; they do not establish independent review.

The proof cites complete-family uniqueness rather than replaying a predecessor
classification. The finite differential certificate is checked exactly. The
smooth tubular-neighborhood and compactness argument is written mathematics.
No proof-kernel, Lean, Docker, global threshold computation, physical supplier
or selected-construction replay is claimed. Hosted CI is tracked separately
in the pull request; this file makes no hosted-success claim.
