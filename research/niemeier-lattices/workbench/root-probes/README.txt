Root-pair rectangle experiment
==============================

Run from the repository root:
    python3 -B -I -O research/niemeier-lattices/workbench/root-probes/rectangles.py

NumPy is required. The script deterministically regenerates the seeded
search's best partition and exactly replays all five small partitions,
then compares the full receipt with RECTANGLES.json. Optional --output
writes a copy outside the package. This is one costly construction for
mixed E8^2 ports, not a bound on all partitions or shared-role circuits.
