#!/usr/bin/env bash
# Recorded regeneration control: recompile both axes through this candidate's
# compiler.py and assert the shipped words are byte-identical, then rerun every
# arithmetic check with compare mode.  Run: bash regen.sh
cd /mnt/d/gen/b82/research/envelope-scheduled
python3 verify.py --regenerate
