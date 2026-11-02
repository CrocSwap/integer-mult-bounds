#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Run only the new static archive checker; archived code is never loaded."""
from pathlib import Path
import importlib.util

path = Path(__file__).resolve().with_name('verify.py')
spec = importlib.util.spec_from_file_location('finite_cover_archive_check', path)
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)
checker.main()
