"""Source-pin and historical-frontier regressions; standard library only.

@woklerx with substantial OpenAI Codex assistance. Apache-2.0.
"""
import copy
import importlib.util
from pathlib import Path
import shutil
import tempfile
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('bootstrap_depth', HERE/'verify.py')
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)


def rejected(label, action, text):
    try:
        action()
    except ValueError as error:
        check.need(text in str(error), 'wrong reason: '+label)
        return
    raise ValueError('negative control accepted: '+label)


def main():
    check.need(__debug__, 'run without -O')
    baseline = check.run()
    read = check.read
    damaged_pins = copy.deepcopy(read(HERE/'SOURCES.json'))
    del damaged_pins['files'][check.ASSEMBLER]
    with patch.object(check, 'read', side_effect=lambda path: damaged_pins if path.name == 'SOURCES.json' else read(path)):
        rejected('deleted required source pin', check.source_pins, 'exact consumed source inventory')
    snapshot = copy.deepcopy(read(HERE/'SELECTED-SNAPSHOT.json'))
    snapshot['kappa'] = '0'
    with patch.object(check, 'read', side_effect=lambda path: snapshot if path.name == 'SELECTED-SNAPSHOT.json' else read(path)):
        rejected('changed historical snapshot', check.run, 'selected snapshot grid binding')
    original_root = check.ROOT
    # The scratch root deliberately contains no certificates/selected-result.json.
    # It is created within this package and removed by TemporaryDirectory only.
    with tempfile.TemporaryDirectory(prefix='depth-audit-test-', dir=HERE) as temporary:
        root = Path(temporary)
        for name in check.REQUIRED_INPUTS:
            destination = root/name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(original_root/name, destination)
        check.ROOT = root
        try:
            check.need(check.canonical(check.run()) == check.canonical(baseline), 'historical replay without selected pointer')
            path = root/check.ASSEMBLER
            path.write_bytes(path.read_bytes()+b'\n# Semantic no-op; immutable source pin must still reject.\n')
            rejected('modified pinned source', check.run, 'source pin: '+check.ASSEMBLER)
        finally:
            check.ROOT = original_root
    print('PASS_T37_BOOTSTRAP_SOURCE_CONTROLS rejected=3 historical_replay_without_selected_pointer=PASS')


if __name__ == '__main__':
    main()
