The default replay verifies three finite certificates:

* encoder_receipt.py: exact dyadic encoder, old-helper compensation and
  restoration for the narrow Pauli factor. This is a partial word. It does
  not implement I-K or certify a complete supplier.
* compensation_rank.py: exact moments and the full rank of I-K on the E8
  squared norm-four shell. The rank-one rectangle consequence does not
  apply to arbitrary reusable arithmetic circuits.
* mobius_frames.py: physical frame growth in the direct, unfused D16
  spinor Mobius schedule. Its obstruction does not exclude other schedules.

Run replay.py with a fresh output directory outside the checkout. It
requires NumPy, propagates -I and -O to the child checks, and compares
parsed JSON with all three frozen receipts. The source checkout is not
modified. pure_blocks.py is retained as optional exploratory history;
its printed diagnostic is not a claimed certificate or a default check.

Prepared by DominikScholz with OpenAI Codex assistance. The inherited E8
geometry, frame interfaces and community provenance remain those cited
by the enclosing package. No new multiplication exponent is claimed.

Verification from the repository root (Python 3.11+ with NumPy):

  python3 -B research/niemeier-lattices/workbench/helper-routes/replay.py /tmp/niemeier-helper-normal
  python3 -B -I -O research/niemeier-lattices/workbench/helper-routes/replay.py /tmp/niemeier-helper-optimized

Both output directories must be new and outside the checkout. The -I -O
invocation propagates isolation and disabled assertions to every child.
The three-certificate replay takes approximately one second on the
packaging machine.
