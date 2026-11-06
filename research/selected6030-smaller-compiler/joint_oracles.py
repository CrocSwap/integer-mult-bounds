#!/usr/bin/env python3
"""Run both independent optional-example checks within one registered command.
@CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
"""
from pathlib import Path
import runpy

here = Path(__file__).resolve().parent
for name in ('joint_independent_oracle.py', 'joint_coefficient_oracle.py'):
    runpy.run_path(str(here/name), run_name='__main__')
