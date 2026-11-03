"""NEW constructor fixtures only; never imports or executes original sources.

Only the parent may run this after exact source/plan/inventory review. Every
fixture/partial remains retained. No deletion, retry or original control rerun.
"""
import copy
import json
import os
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'constructor'))
import fresh_sc as new

IDS = ('corrected_owned_fixture', 'positive_short_write', 'missing_body',
       'wrong_body_pin', 'duplicate_destination', 'path_traversal', 'bool_bytes',
       'existing_stage', 'write_fault', 'readback_fault', 'primary_close_fault',
       'pending_open', 'prior_failed_owner', 'wrong_mode', 'scope_elevation',
       'runtime_name_override', 'unbound_full_proposal')
EXPECTED = ('PREPARED', 'PREPARED', 'REFUSED_BEFORE_STAGE', 'REFUSED_BEFORE_STAGE',
            'REFUSED_BEFORE_STAGE', 'REFUSED_BEFORE_STAGE', 'REFUSED_BEFORE_STAGE',
            'REFUSED_EXISTING', 'PRIMARY_PRESERVED', 'PRIMARY_PRESERVED',
            'PRIMARY_SECONDARY_AND_CLEANUP', 'PENDING_QUARANTINE',
            'PRIOR_PRIMARY_NO_IO', 'MODE_REFUSED', 'REFUSED_BEFORE_STAGE',
            'REFUSED_BEFORE_STAGE', 'REFUSED_BEFORE_STAGE')


class Marker(RuntimeError):
    pass


class FixtureOps:
    def __init__(self, kind):
        self.kind = kind
        self.calls = 0
        self.close_calls = 0
        self.body_error = Marker('owned fixture body marker')
        self.close_error = Marker('owned fixture close marker')
    def __getattr__(self, name):
        def call(*args, **kwargs):
            self.calls += 1
            if name == 'open' and self.kind == 'pending_open':
                raise self.body_error
            if name == 'write' and self.kind in ('write_fault', 'primary_close_fault'):
                raise self.body_error
            if name == 'read' and self.kind == 'readback_fault':
                raise self.body_error
            if name == 'fchmod' and self.kind == 'wrong_mode':
                return None
            if name == 'write' and self.kind == 'positive_short_write':
                args = (args[0], args[1][:2])
            if name == 'close':
                self.close_calls += 1
                result = os.close(*args, **kwargs)
                if self.kind == 'primary_close_fault' and self.close_calls == 1:
                    raise self.close_error
                return result
            return getattr(os, name)(*args, **kwargs)
        return call


def fixture_request():
    raw = b'owned fixture bytes\n'
    sha = new.digest(raw)
    rows = [{'occurrence_id': 'fixture01', 'logical_name': 'fixture',
             'recovered_path': None, 'installed_relative_path': 'payload/body.txt',
             'sha256': sha, 'bytes': len(raw), 'mode': 0o444,
             'producer_role': 'OWNED_FIXTURE', 'pin_provenance': 'literal owned fixture bytes',
             'availability': 'OWNED_FIXTURE_BYTES', 'required': True}]
    request = {'schema': 'fresh-sc-request-v1', 'subject_kind': 'OWNED_FIXTURE',
               'stage_name': 'fixture-stage', 'manifest': rows,
               'manifest_sha256': new.digest(new.canonical(rows)),
               'compatibility_sha256': '0' * 64, 'selection_sha256': '1' * 64,
               'forbidden_runtime_names': list(new.RUNTIME_NAMES), 'claims': dict(new.CLAIMS)}
    return request, {sha: raw}


def main():
    new.need(len(sys.argv) == 2, 'fresh owned fixture destination required')
    base = Path(sys.argv[1])
    base.mkdir(mode=0o700, parents=False, exist_ok=False)
    outcomes = []
    pre_io = {'missing_body', 'wrong_body_pin', 'duplicate_destination',
              'path_traversal', 'bool_bytes', 'scope_elevation',
              'runtime_name_override', 'unbound_full_proposal'}
    for key, expected in zip(IDS, EXPECTED):
        root = base / key
        root.mkdir(mode=0o700)
        request, pool = fixture_request()
        ops = FixtureOps(key)
        owner = new.PreparationOwner(os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW), ops)
        if key == 'missing_body':
            pool.clear()
        elif key == 'wrong_body_pin':
            pool[next(iter(pool))] = b'wrong'
        elif key == 'duplicate_destination':
            other = copy.deepcopy(request['manifest'][0])
            other['occurrence_id'] = 'fixture02'
            request['manifest'].append(other)
        elif key == 'path_traversal':
            request['manifest'][0]['installed_relative_path'] = '../escape'
        elif key == 'bool_bytes':
            request['manifest'][0]['bytes'] = True
        elif key == 'scope_elevation':
            request['claims']['runtime_admission'] = True
        elif key == 'runtime_name_override':
            request['forbidden_runtime_names'] = ['one', 'two', 'three', 'four']
        elif key == 'unbound_full_proposal':
            request['subject_kind'] = 'FULL_ORIGINAL_PROPOSAL'
        elif key == 'existing_stage':
            (root / request['stage_name']).mkdir(mode=0o700)
        elif key == 'prior_failed_owner':
            owner.primary[0] = ops.body_error
            owner.quarantine[0] = True
        request['manifest_sha256'] = new.digest(new.canonical(request['manifest']))
        caught = None
        try:
            result = new.prepare_full_stage(request, pool, owner)
        except BaseException as error:
            caught = error
        if key in pre_io:
            new.need(caught is owner.primary[0] and caught is not None and ops.calls == 0
                     and not (root / request['stage_name']).exists(), 'before-stage refusal oracle')
            outcome = 'REFUSED_BEFORE_STAGE'
        elif key == 'prior_failed_owner':
            new.need(caught is ops.body_error and ops.calls == 0, 'prior owner oracle')
            outcome = 'PRIOR_PRIMARY_NO_IO'
        elif key == 'existing_stage':
            new.need(type(caught) is FileExistsError and (root / request['stage_name']).is_dir(), 'existing-stage oracle')
            outcome = 'REFUSED_EXISTING'
        elif key == 'pending_open':
            new.need(caught is ops.body_error and owner.pending[0] and owner.quarantine[0], 'pending acquisition oracle')
            outcome = 'PENDING_QUARANTINE'
        elif key in ('write_fault', 'readback_fault', 'primary_close_fault'):
            new.need(caught is ops.body_error and owner.primary[0] is ops.body_error, 'direct primary oracle')
            before = ops.calls
            try:
                new.prepare_full_stage(request, pool, owner)
            except BaseException as repeated:
                new.need(repeated is ops.body_error and ops.calls == before, 'no successor after failure')
            else:
                raise RuntimeError('failed owner reused')
            outcome = 'PRIMARY_SECONDARY_AND_CLEANUP' if key == 'primary_close_fault' else 'PRIMARY_PRESERVED'
        elif key == 'wrong_mode':
            new.need(caught is not None and owner.primary[0] is caught, 'exact mode refusal')
            outcome = 'MODE_REFUSED'
        else:
            new.need(caught is None and result['status'] == 'INERT_FRESH_STAGE_PREPARED_ONLY'
                     and result['claims'] == new.CLAIMS and result['C07_lease'] is False, 'source-only result')
            new.need((root / 'fixture-stage/payload/body.txt').read_bytes() == b'owned fixture bytes\n', 'independent literal fixture readback')
            new.need(owner.lineage[0]['written'] == 20, 'positive short-write byte bill')
            outcome = 'PREPARED'
        try:
            new.finish_preparation(owner)
        except BaseException as terminal:
            new.need(terminal is owner.primary[0], 'finish retains primary')
        new.need(all(fd is None for fd in owner.fds), 'all independent known closes attempted')
        if key == 'primary_close_fault':
            new.need(owner.secondary_count[0] == 1 and owner.secondary[0] is ops.close_error
                     and ops.close_calls >= 3, 'raw secondary and cleanup continuation')
        new.need(outcome == expected, 'independent literal ordered oracle')
        outcomes.append({'id': key, 'outcome': outcome})
    print(json.dumps({'status': 'PASS_NEW_OWNED_FIXTURE_CONSTRUCTOR_ONLY',
                      'controls': outcomes, 'claims': new.CLAIMS,
                      'original_definitions_executed': False}, sort_keys=True))


if __name__ == '__main__':
    main()
