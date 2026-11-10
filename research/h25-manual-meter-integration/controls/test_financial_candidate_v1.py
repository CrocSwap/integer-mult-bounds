"""New pure-code controls; never import or execute original C2/F4/A4 modules.

The small source-owned fixture below is an arithmetic/transition oracle only.
It cannot authenticate a native owner, existing F4 schema, census or source pin.
Native IO/EX publication and original normal/O qualification remain unrun.
"""
import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
from types import ModuleType
import unittest


ROOT = Path(__file__).resolve().parents[1]


def load_new(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'implementation' / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CANDIDATE = load_new('financial_candidate_v1')
SETTLEMENT = load_new('manual_settlement_v1')


FIXTURE = '''
import json
from pathlib import Path
FIN_ROOT = Path('/fixture/financial')
FIN_ENTRIES = FIN_ROOT / 'entries'
FIN_HEAD = FIN_ROOT / 'HEAD.json'
ADMIN_NS = 7
META_CAP = 131072
FIN_MAX_FILES = 2048
FIN_MAX_BYTES = 8388608
FRAME_RECORDS = {}
def financial_plain(value):
    if type(value) is dict:
        if not all(type(k) is str for k in value): raise ValueError('keys')
        for x in value.values(): financial_plain(x)
    elif type(value) is list:
        for x in value: financial_plain(x)
    elif value is not None and type(value) not in (str,int,bool): raise ValueError('DATA')
def financial_decode(raw): return json.loads(raw)
def canonical_financial(value): return (json.dumps(value,sort_keys=True,separators=(',',':'))+'\\n').encode()
def fp(value,raw=False):
    if type(value) is not dict or set(value)!={'path','bytes','sha256','mode'}: raise ValueError('pin')
def flabel(value):
    if type(value) is not str or not value or '/' in value: raise ValueError('label')
def validate_original_record(kind,value):
    if type(value) is not dict: raise ValueError('record')
    return value
def _manifest_successor(a,b):
    if a['attempt_id']!=b['attempt_id']: raise ValueError('APPEND')
    for k in ('command_pin','reservation_pin','pre_entry_pin','meter_start_pin'):
        if a[k] is not None and a[k]!=b[k]: raise ValueError('APPEND')
def _opening_evidence_f3(value): return dict(parent_body_ns=100,parent_admin_ns=30)
def _entry_financial_view(pin,manifest,take,legacy):
    name=manifest['attempt_id']; terminal=manifest['phase']=='CLOSED_KNOWN'
    body=20 if name=='old' else (5 if terminal else None)
    return dict(entry_id=name,phase=manifest['phase'],body_ns=body,
        settlement_route=manifest['settlement_route'],manifest_pin=pin,
        terminal_known=terminal,known_charge_ns=None if body is None else body+7,
        _unknown=[] if terminal else ['REVIEW_MISSING'])
def financial_evidence(snapshot):
    wires=snapshot['wires']; head=json.loads(snapshot['head_wire'])
    state=json.loads(wires[head['state_pin']['path']]); opening=json.loads(snapshot['opening_wire'])
    entries={}
    for pin in state['ordered_entries']:
        m=json.loads(wires[pin['path']]); entries[m['attempt_id']]=_entry_financial_view(pin,m,None,None)
    return dict(entries=entries,descriptor=opening,state_pin=head['state_pin'],
        opening_pin=snapshot['opening_pin'],head_pin=snapshot['head_pin'],
        encumbered_policy_ns=500,pending=[n for n,v in entries.items() if v['phase']!='CLOSED_KNOWN'])
def require_opening_append(previous,current):
    a=financial_evidence(previous); b=financial_evidence(current)
    if list(b['entries'])[:len(a['entries'])]!=list(a['entries']): raise ValueError('APPEND')
    if b['descriptor']['previous_opening_sha256']!=a['opening_pin']['sha256']: raise ValueError('APPEND')
    return True
'''


def fixture():
    module = ModuleType('new_pure_funding_fixture')
    exec(FIXTURE, module.__dict__)
    return module


def record(name, phase, command=None, reservation=None, start=None):
    return dict(schema='fixture-entry', attempt_id=name, phase=phase,
                command_pin=command, reservation_pin=reservation, pre_entry_pin=None,
                meter_start_pin=start, meter_body_pin=None, native_chain_pin=None,
                financial_adjudication_pin=None, formal_start_pin=None, formal_receipt_pin=None,
                settlement_route='MANUAL_ONLY')


class CandidateControls(unittest.TestCase):
    def setUp(self):
        self.F = fixture(); self.wires = {}
        def put(path, value, mode=0o444):
            wire = self.F.canonical_financial(value).decode()
            self.wires[str(path)] = wire
            return CANDIDATE.wire_pin(path, wire, mode)
        self.put = put
        root = self.F.FIN_ROOT; entries = self.F.FIN_ENTRIES
        old = put(entries / 'old/ENTRY-000000.json', record('old', 'CLOSED_KNOWN'))
        pending = put(entries / 'debt/ENTRY-000000.json', record('debt', 'STARTED'))
        state = dict(schema='fixture-state', generation=0, previous_state_sha256=None,
                     ordered_entries=[old,pending], known_body_ns=120, admin_policy_ns=44,
                     known_policy_ns=164, unsettled_entries=['debt'], metadata_close_events=[],
                     physical_total_ns=None, old_complete_total_ns=None, physical_boundary='OPEN_NOT_ZERO')
        self.state_pin = put(root / 'STATE-000000.json', state)
        opening = dict(schema='fixture-opening', suffix_state_pin=self.state_pin,
                       previous_opening_sha256=None, expected_totals=dict(body_ns=120,
                       admin_policy_ns=44,known_policy_ns=164,operations=5))
        op = put(root / 'OPENING-000000.json', opening)
        head = dict(schema='fresh-financial-head-v1', generation=0,state_pin=self.state_pin,
                    opening_pin=op,previous_head_sha256=None)
        put(root / 'HEAD-000000.json', head,0o600); hp=put(self.F.FIN_HEAD,head,0o600)
        self.previous=dict(schema='fresh-financial-snapshot-v1',opening_pin=op,
            opening_wire=self.wires[op['path']],legacy_snapshot={'fixture':True},
            wires=copy.deepcopy(self.wires),head_pin=hp,head_wire=self.wires[hp['path']],
            census={str(root):['HEAD-000000.json','HEAD.json','OPENING-000000.json','STATE-000000.json','entries'],
                    str(entries):['debt','old'],str(entries/'old'):['ENTRY-000000.json'],
                    str(entries/'debt'):['ENTRY-000000.json']})
        folder = entries / 'own'
        command=put(folder/'COMMAND.json',dict(operation_class='METADATA_INITIALIZER',settlement_route='MANUAL_ONLY'))
        reservation=put(folder/'RESERVATION.json',dict(before_closed_state_pin=self.state_pin,
            policy_reserved_before_ns=500,body_reservation_ns=100))
        self.reserved=put(folder/'ENTRY-000000.json',record('own','RESERVED',command,reservation))
        self.start=put(folder/'METER_START.json',dict(attempt_id='own',command_pin=command,
            reservation_pin=reservation,body_begin_ns=123456789))
        self.wires[str(folder/'METER_BODY.json')]=''
        self.extra={p:w for p,w in self.wires.items() if p not in self.previous['wires']}
        self.pending=str(folder/'PENDING.json')
        self.builder=CANDIDATE.bind_funding(self.F)

    def started(self):
        return self.builder.build_started(self.previous,self.reserved,self.start,self.extra,self.pending)

    def change_reservation(self, **changes):
        manifest=json.loads(self.extra[self.reserved['path']]); rp=manifest['reservation_pin']
        obj=json.loads(self.extra[rp['path']]); obj.update(changes)
        wire=self.F.canonical_financial(obj).decode(); self.extra[rp['path']]=wire
        manifest['reservation_pin']=CANDIDATE.wire_pin(rp['path'],wire)
        wire=self.F.canonical_financial(manifest).decode(); self.extra[self.reserved['path']]=wire
        self.reserved=CANDIDATE.wire_pin(self.reserved['path'],wire)
        start=json.loads(self.extra[self.start['path']]);start['reservation_pin']=manifest['reservation_pin']
        wire=self.F.canonical_financial(start).decode(); self.extra[self.start['path']]=wire
        self.start=CANDIDATE.wire_pin(self.start['path'],wire)

    def test_started_is_exact_two_field_change_and_preserves_start_clock(self):
        result=self.started(); c=result['candidate']
        reserved=json.loads(self.extra[self.reserved['path']])
        expected=dict(reserved,meter_start_pin=self.start,phase='STARTED')
        self.assertEqual(json.loads(c['wires'][result['started_manifest_pin']['path']]),expected)
        self.assertEqual(json.loads(c['wires'][self.start['path']])['body_begin_ns'],123456789)
        self.assertEqual(json.loads(c['wires'][self.pending])['closed_state_sha256'],self.state_pin['sha256'])
        self.assertEqual(self.previous['opening_pin']['sha256'],json.loads(c['opening_wire'])['previous_opening_sha256'])

    def test_literal_full_totals_keep_existing_debt_and_history(self):
        c=self.started()['candidate']; state=json.loads(c['wires'][json.loads(c['head_wire'])['state_pin']['path']])
        self.assertEqual((state['known_body_ns'],state['admin_policy_ns'],state['known_policy_ns']),(120,51,171))
        self.assertEqual(state['unsettled_entries'],['debt','own'])
        self.assertEqual(json.loads(c['opening_wire'])['expected_totals'],dict(body_ns=120,admin_policy_ns=51,known_policy_ns=171,operations=6))
        for path,wire in self.previous['wires'].items():
            if path!=str(self.F.FIN_HEAD): self.assertEqual(c['wires'][path],wire)
        self.assertEqual(c['census'][str(self.F.FIN_ENTRIES)],['debt','old','own'])
        self.assertEqual(c['wires'][str(self.F.FIN_ENTRIES/'own/METER_BODY.json')],'')

    def test_stale_predecessor_reservation_rejected(self):
        self.change_reservation(before_closed_state_pin=dict(self.state_pin,sha256='a'*64))
        with self.assertRaisesRegex(CANDIDATE.CandidateError,'reservation names exact predecessor'):self.started()

    def test_hidden_reservation_debt_rejected(self):
        # The record pin remains authentic for this changed fixture record;
        # rejection must be the before-encumbrance relationship, not a bad hash.
        self.change_reservation(policy_reserved_before_ns=0)
        with self.assertRaisesRegex(CANDIDATE.CandidateError,'reservation names exact predecessor'):self.started()

    def test_old_wire_mutation_rejected(self):
        self.extra[self.state_pin['path']]='{}'
        with self.assertRaises(CANDIDATE.CandidateError):self.started()

    def test_wrong_operation_rejected_at_authenticated_command(self):
        manifest=json.loads(self.extra[self.reserved['path']]); cp=manifest['command_pin']
        command=dict(operation_class='DATA_CONTROLLER',settlement_route='MANUAL_ONLY')
        wire=self.F.canonical_financial(command).decode(); self.extra[cp['path']]=wire
        manifest['command_pin']=CANDIDATE.wire_pin(cp['path'],wire)
        wire=self.F.canonical_financial(manifest).decode();self.extra[self.reserved['path']]=wire
        self.reserved=CANDIDATE.wire_pin(self.reserved['path'],wire)
        start=json.loads(self.extra[self.start['path']]);start['command_pin']=manifest['command_pin']
        wire=self.F.canonical_financial(start).decode();self.extra[self.start['path']]=wire
        self.start=CANDIDATE.wire_pin(self.start['path'],wire)
        with self.assertRaises(CANDIDATE.CandidateError):self.started()

    def test_census_accounts_for_every_new_entry_file(self):
        c=self.started()['candidate']; folder=self.F.FIN_ENTRIES/'own'
        self.assertEqual(c['census'][str(folder)],sorted(Path(p).name for p in c['wires'] if Path(p).parent==folder))

    def test_replayed_started_entry_rejected(self):
        result=self.started()
        with self.assertRaises(CANDIDATE.CandidateError):
            self.builder.build_started(result['candidate'],self.reserved,self.start,self.extra,self.pending)

    def test_exact_function_code_and_source_identity(self):
        other=fixture()
        self.F.financial_decode.__code__=other.financial_decode.__code__
        with self.assertRaises(CANDIDATE.CandidateError):self.started()

    def test_path_hook_is_rejected_without_calling_it(self):
        calls=[]
        class Hostile:
            def __str__(self):calls.append(True);raise AssertionError('hook')
        with self.assertRaises(CANDIDATE.CandidateError):CANDIDATE.wire_pin(Hostile(),'{}')
        self.assertEqual(calls,[])

    def test_settlement_literal_charge_once_and_preserves_other_debt(self):
        c=self.started()['candidate']; oldpin=c['opening_pin']; folder=self.F.FIN_ENTRIES/'own'
        manifest=json.loads(c['wires'][str(folder/'ENTRY-000001.json')]);manifest['phase']='CLOSED_KNOWN'
        wire=self.F.canonical_financial(manifest).decode();pin=CANDIDATE.wire_pin(folder/'ENTRY-000002.json',wire)
        additions={pin['path']:wire,str(folder/'METER_BODY.json'):'{"fixture":"actual-body"}\n'}
        result=self.builder.build_settlement(c,'own',pin,additions)
        state=json.loads(result['wires'][json.loads(result['head_wire'])['state_pin']['path']])
        self.assertEqual((state['known_body_ns'],state['admin_policy_ns'],state['known_policy_ns']),(125,51,176))
        self.assertEqual(state['unsettled_entries'],['debt'])
        self.assertEqual(json.loads(result['opening_wire'])['previous_opening_sha256'],oldpin['sha256'])
        with self.assertRaises(CANDIDATE.CandidateError):self.builder.build_settlement(result,'own',pin,additions)


class ErrorAndPublicationSourceControls(unittest.TestCase):
    def test_first_error_survives_cleanup_and_partial_retains_reservation(self):
        f=SETTLEMENT.FailureState(); first=OSError('write'); cleanup=OSError('close')
        f.publication_entered();self.assertIs(f.remember(first,True),first)
        self.assertIs(f.remember(cleanup,True),first)
        self.assertEqual(f.secondary,[cleanup]);self.assertTrue(f.reservation_retained)
        with self.assertRaises(SETTLEMENT.SettlementError):f.verified()

    def test_known_readback_is_only_reservation_release_transition(self):
        f=SETTLEMENT.FailureState();self.assertTrue(f.reservation_retained)
        with self.assertRaises(SETTLEMENT.SettlementError):f.verified()
        f.publication_entered();f.verified();self.assertFalse(f.reservation_retained)
        with self.assertRaises(SETTLEMENT.SettlementError):f.publication_entered()

    def test_actual_publisher_uses_candidate_verifier_before_any_publication(self):
        tree=ast.parse((ROOT/'implementation/manual_settlement_v1.py').read_text())
        fn=next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name=='settle')
        text=ast.get_source_segment((ROOT/'implementation/manual_settlement_v1.py').read_text(),fn)
        self.assertLess(text.index("fns['verify_financial_candidate']"),text.index("publication_entered()"))
        self.assertLess(text.index("fns['read_financial_opening']"),text.index("r['failure'].verified()"))
        self.assertIn("before['head_pin']",text)
        self.assertNotIn('financial_commit_candidate',text)
        self.assertIn("if name != own_id",text)

    def test_stale_head_and_missing_census_are_not_downgraded_to_partial_success(self):
        # This is a source-routing oracle, not execution of old F4/native IO.
        text=(ROOT/'implementation/manual_settlement_v1.py').read_text()
        self.assertIn("fns['verify_financial_candidate'](io, candidate, os.getuid(), before['head_pin'])",text)
        self.assertIn("need(actual == candidate",text)
        self.assertIn("raise fail(r, error, uncertain)",text)
        self.assertNotIn('except Exception: pass',text)


if __name__=='__main__':
    unittest.main()
