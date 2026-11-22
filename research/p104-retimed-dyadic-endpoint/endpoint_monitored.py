#!/usr/bin/env python3
"""Measure fixed candidate setup; run operand-dependent guards separately."""
from importlib.util import module_from_spec,spec_from_file_location
from pathlib import Path
from unittest.mock import patch
import sys

source, machine, result = map(Path,sys.argv[1:4])
sys.path.insert(0,str(machine.resolve()))
sys.path.insert(1,str(source.resolve()))
from upstream import install
install()
from installations import DYADIC_ENDPOINT,PROFILES
import check_installation

# The source's <=4096-bit/zero-calendar measurement is for fixed setup only.
# Keep the named installed profile and monitor the exact prepare_native path.
assert PROFILES['dyadic-endpoint'] is DYADIC_ENDPOINT
with patch.object(check_installation,'PROFILES',{'dyadic-endpoint':DYADIC_ENDPOINT}):
    check_installation.main()
print('PASS_E264_CANDIDATE_MONITORED_FIXED_SETUP',flush=True)

# Entrance, placement and boundary arithmetic are operand-dependent controls;
# they are intentionally outside the source's fixed-setup monitor.
runtime=Path(__file__).with_name('endpoint_runtime.py')
spec=spec_from_file_location('endpoint_runtime',runtime)
module=module_from_spec(spec)
sys.argv=[str(runtime),str(source),str(machine),str(result)]
spec.loader.exec_module(module)
module.main()
print('PASS_E264_CANDIDATE_FINITE_RUNTIME_GUARDS',flush=True)
