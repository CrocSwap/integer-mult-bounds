"""Shim for adoption simulation and benchmarking only.

Preloading this module as `binary_frame_replay` routes `replay` (and the
retained `check_word`) to the optimized adapter, so the frozen historical
test module `tests/test_joint_reclaim.py` can run unmodified against the
adapter via its own `from binary_frame_replay import replay`. The frozen
test file and the historical implementation are not changed by this.
"""
from fast_replay import replay, check_word  # check_word is the frozen historical one

__all__ = ['replay', 'check_word']
