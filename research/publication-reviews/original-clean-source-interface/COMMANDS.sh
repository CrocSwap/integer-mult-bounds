#!/bin/sh
set -eu
env OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 NUMEXPR_NUM_THREADS=1 python3 -I -B /Users/aliromman/Projects/IntegerMultiplicationBounds/work/centre-encoding-campaign-20261014/publication-wrap-20261022/reviews/original-clean-source-interface/cold/package/replay.py --out /Users/aliromman/Projects/IntegerMultiplicationBounds/work/centre-encoding-campaign-20261014/publication-wrap-20261022/reviews/original-clean-source-interface/cold/replay
python3 -I -B /Users/aliromman/Projects/IntegerMultiplicationBounds/work/centre-encoding-campaign-20261014/publication-wrap-20261022/reviews/original-clean-source-interface/check_package.py
