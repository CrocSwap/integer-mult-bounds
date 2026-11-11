"""One reviewed inert full preparation per mode; imports NEW constructor only."""
import json
import os
from pathlib import Path
import sys

SOURCE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SOURCE / 'constructor'))
import fresh_sc as new


def load_source():
    request = json.loads((SOURCE / 'payload/REQUEST-v2.json').read_bytes())['constructor_request']
    compatibility = (SOURCE / 'caller/CALLER-COMPATIBILITY-v2.json').read_bytes()
    selection = (SOURCE / 'payload/SELECTION-v2.json').read_bytes()
    pool = {p.stem: p.read_bytes() for p in (SOURCE / 'payload/body-pool').iterdir()}
    return request, pool, compatibility, selection


def main():
    new.need(len(sys.argv) == 2 and sys.argv[1] in ('normal', 'optimized'), 'one preparation mode')
    mode = sys.argv[1]
    new.need(bool(sys.flags.optimize) == (mode == 'optimized'), 'actual child mode')
    request, pool, compatibility, selection = load_source()
    parent = json.loads(selection)['approved_preparation']['parents'][mode]
    owner = new.PreparationOwner(os.open(parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC))
    result, primary = None, None
    try:
        new.bind_full_preparation(owner, request, compatibility, selection, mode)
        result = new.prepare_full_stage(request, pool, owner)
    except BaseException as error:
        primary = error
    try:
        new.finish_preparation(owner)
    except BaseException as error:
        if primary is None:
            primary = error
    if primary is not None:
        raise primary
    new.need(owner.closed[0] and all(fd is None for fd in owner.fds)
             and all(owner.close_confirmed[i] for i in range(owner.next_slot[0])
                     if owner.close_attempted[i]), 'confirmed full final closure')
    new.need(result['installed_occurrences'] == 259 and result['claims'] == new.CLAIMS,
             'full prepared-only result')
    # External inventory/ledger acceptance still belongs to the serial parent.
    print(json.dumps({'status': 'CHILD_FINISHED_INERT_PREPARATION_ONLY', 'mode': mode,
                      'installed_occurrences': 259, 'finish_succeeded': True,
                      'manifest_sha256': request['manifest_sha256'], 'claims': new.CLAIMS,
                      'original_definitions_executed': False}, sort_keys=True))


if __name__ == '__main__':
    main()
