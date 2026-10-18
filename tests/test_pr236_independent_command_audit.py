"""Corrupt evidence while repairing outer hashes to exercise semantic bindings.

These are small synthetic receipt fixtures, not Lean compilation tests.
Prepared with substantial OpenAI Codex assistance; Apache-2.0.
"""
import importlib.util
import io
import json
from pathlib import Path
import tarfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    'pr236_reconciliation', ROOT / 'research/pr236-independent-command-audit/verify.py')
VERIFY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFY)


def fixture():
    sources = {'src/A.lean': b'import Init\n#print axioms A.claim\n',
               'src/B.lean': b'import A\n#print axioms B.claim\n',
               'scientific/input.json': b'{"historical":true}\n'}
    modules = [dict(module=n, source='src/' + n + '.lean',
                    source_sha256=VERIFY.sha(sources['src/' + n + '.lean']),
                    declarations=1, expected_axiom_commands=[n + '.claim'],
                    imports=imports, timeout_seconds=60)
               for n, imports in [('A', ['Init']), ('B', ['A'])]]
    plan = dict(target_commit=VERIFY.TARGET, axiom_policy=VERIFY.ALLOWED,
                modules=modules, accepted_module_count=2, accepted_declarations=2,
                scientific_inputs=[dict(path='scientific/input.json',
                                        sha256=VERIFY.sha(sources['scientific/input.json']))],
                external_imports=['Init'], ordered_modules=['A', 'B'])
    map_bytes = VERIFY.encode(plan)
    compiler = {'version': 'synthetic fixture, not an executed compiler'}
    summary = dict(status='FULL_ACCEPTED_SET_COMPILED', full_accepted_set=True,
                   kernel_compiled=True, map_sha256=VERIFY.sha(map_bytes),
                   source_commit=VERIFY.TARGET, accepted_modules=2, selected_modules=2,
                   selected_declarations=2, rebuilt=['B'], reused=['A'], receipts={}, compiler=compiler)
    evidence = {'INPUT_MAP.json': map_bytes, 'darwin-driver.py': b'not executed'}
    for m in modules:
        name = m['module']
        log = ("'" + name + ".claim' does not depend on any axioms\n").encode()
        key = dict(policy=VERIFY.POLICY, compiler=compiler, source_sha256=m['source_sha256'],
                   imports=m['imports'], expected_axiom_commands=m['expected_axiom_commands'],
                   dependencies={} if name == 'A' else {'A': VERIFY.sha(b'object A')},
                   timeout_seconds=60, address_space_bytes=None, lean_jobs=1,
                   lean_stack_kib=65536, allowed_axioms=VERIFY.ALLOWED)
        receipt = dict(module=name, status='PASS', compiler_exit=0,
                       map_sha256_when_built=VERIFY.sha(map_bytes), build_key=key,
                       object_sha256=VERIFY.sha(('object ' + name).encode()),
                       log_sha256=VERIFY.sha(log),
                       audit=dict(declarations=1, axiom_free=1, axioms=[]))
        evidence['receipts/' + name + '.json'] = VERIFY.encode(receipt)
        evidence['logs/' + name + '.log'] = log
        summary['receipts'][name] = VERIFY.receipt_hash(receipt)
    evidence['SUMMARY.json'] = VERIFY.encode(summary)
    return map_bytes, sources, evidence


def change_receipt(evidence, name, change):
    path = 'receipts/' + name + '.json'
    receipt = json.loads(evidence[path])
    change(receipt)
    evidence[path] = VERIFY.encode(receipt)
    summary = json.loads(evidence['SUMMARY.json'])
    summary['receipts'][name] = VERIFY.receipt_hash(receipt)
    evidence['SUMMARY.json'] = VERIFY.encode(summary)


class SourceReceiptReconciliation(unittest.TestCase):
    def setUp(self):
        self.map_bytes, self.sources, self.evidence = fixture()

    def check(self):
        return VERIFY.reconcile(self.map_bytes, self.sources, self.evidence)

    def reject(self, reason):
        with self.assertRaisesRegex(VERIFY.ReconciliationError, reason):
            self.check()

    def test_complete_fixture_and_explicit_trust_boundary(self):
        result = self.check()
        self.assertEqual(result['accepted_modules'], 2)
        self.assertEqual(result['internal_dependency_edges'], 1)
        self.assertEqual(result['audited_declarations'], 2)
        self.assertFalse(result['fresh_kernel_compilation'])
        self.assertFalse(result['object_and_compiler_hashes_independently_revalidated'])

    def test_changed_accepted_source(self):
        self.sources['src/A.lean'] += b'-- changed\n'
        self.reject('Accepted source digest')

    def test_missing_and_extra_sources(self):
        for missing in [True, False]:
            with self.subTest(missing=missing):
                self.setUp()
                if missing:
                    del self.sources['src/A.lean']
                else:
                    self.sources['src/Extra.lean'] = b'not accepted'
                self.reject('Exact source archive inventory')

    def test_changed_scientific_input(self):
        self.sources['scientific/input.json'] = b'{}'
        self.reject('Scientific input digest')

    def test_duplicate_module_and_dependency_cycle(self):
        for mode in ['duplicate', 'cycle']:
            with self.subTest(mode=mode):
                self.setUp()
                plan = json.loads(self.map_bytes)
                if mode == 'duplicate':
                    plan['modules'][1]['module'] = 'A'
                else:
                    plan['modules'][0]['imports'] = ['B']
                    self.sources['src/A.lean'] = self.sources['src/A.lean'].replace(b'import Init', b'import B')
                    plan['modules'][0]['source_sha256'] = VERIFY.sha(self.sources['src/A.lean'])
                self.map_bytes = VERIFY.encode(plan)
                self.reject('Module identity coverage|Dependency order/closure')

    def test_missing_or_extra_evidence_member(self):
        for missing in [True, False]:
            with self.subTest(missing=missing):
                self.setUp()
                if missing:
                    del self.evidence['receipts/A.json']
                else:
                    self.evidence['receipts/Extra.json'] = b'{}'
                self.reject('Exact historical evidence inventory')

    def test_changed_map_copy(self):
        self.evidence['INPUT_MAP.json'] += b'\n'
        self.reject('Submitted/retained map equality')

    def test_source_dependency_and_policy_tampering_with_resealed_summary(self):
        changes = [lambda r: r['build_key'].update(source_sha256='0' * 64),
                   lambda r: r['build_key']['dependencies'].update(A='0' * 64),
                   lambda r: r['build_key'].update(address_space_bytes=4 * 1024**3),
                   lambda r: r['build_key'].update(expected_axiom_commands=[])]
        for index, change in enumerate(changes):
            with self.subTest(index=index):
                self.setUp()
                change_receipt(self.evidence, 'B', change)
                self.reject('Receipt source/dependency/policy binding')

    def test_missing_and_duplicate_declarations_with_resealed_log_and_summary(self):
        for log in [b'', self.evidence['logs/A.log'] * 2]:
            with self.subTest(log=log):
                self.setUp()
                self.evidence['logs/A.log'] = log
                change_receipt(self.evidence, 'A', lambda r: r.update(log_sha256=VERIFY.sha(log)))
                self.reject('Axiom declaration coverage|Duplicate axiom report')

    def test_disallowed_axiom_with_resealed_log_and_summary(self):
        log = b"'A.claim' depends on axioms: [sorryAx]\n"
        self.evidence['logs/A.log'] = log
        change_receipt(self.evidence, 'A', lambda r: r.update(log_sha256=VERIFY.sha(log)))
        self.reject('Disallowed recorded axiom')

    def test_recount_is_compared_to_receipt(self):
        change_receipt(self.evidence, 'A', lambda r: r['audit'].update(axiom_free=0))
        self.reject('Receipt axiom recount')

    def test_changed_log_without_resealing(self):
        self.evidence['logs/A.log'] += b'warning: changed bytes\n'
        self.reject('Receipt log digest')

    def test_incomplete_build_partition(self):
        summary = json.loads(self.evidence['SUMMARY.json'])
        summary['rebuilt'] = []
        self.evidence['SUMMARY.json'] = VERIFY.encode(summary)
        self.reject('Historical build partition')

    def test_failed_compiler_receipt(self):
        change_receipt(self.evidence, 'A', lambda r: r.update(compiler_exit=1))
        self.reject('Historical receipt status')

    def test_boolean_cannot_replace_integer_evidence(self):
        changes = [lambda r: r.update(compiler_exit=False),
                   lambda r: r['build_key'].update(lean_jobs=True),
                   lambda r: r['audit'].update(declarations=True)]
        for change in changes:
            self.setUp()
            change_receipt(self.evidence, 'A', change)
            self.reject('Historical receipt status|policy binding|Receipt axiom recount')

    def test_duplicate_json_keys_are_rejected(self):
        with self.assertRaisesRegex(VERIFY.ReconciliationError, 'Duplicate JSON key'):
            VERIFY.decode(b'{"compiler_exit":1,"compiler_exit":0}')

    def test_self_consistent_object_hashes_are_not_object_verification(self):
        # Positive boundary control: without .olean bytes a consistently rebound
        # graph can pass the structural layer. Production pins authentic Git
        # archives first; neither layer claims to revalidate absent binaries.
        replacement = VERIFY.sha(b'no corresponding compiled object supplied')
        change_receipt(self.evidence, 'A', lambda r: r.update(object_sha256=replacement))
        change_receipt(self.evidence, 'B', lambda r: r['build_key']['dependencies'].update(A=replacement))
        result = self.check()
        self.assertFalse(result['object_and_compiler_hashes_independently_revalidated'])

    def test_multiline_axioms_and_linter_output(self):
        log = (b"warning: a harmless linter message\n"
               b"'A.claim' depends on axioms: [propext,\n Classical.choice,\n Quot.sound]\n")
        result = VERIFY.audit_log(log, ['A.claim'])
        self.assertEqual(result, dict(declarations=1, axiom_free=0, axioms=VERIFY.ALLOWED))
        with self.assertRaisesRegex(VERIFY.ReconciliationError, 'Unterminated'):
            VERIFY.audit_log(b"'A.claim' depends on axioms: [propext,\n", ['A.claim'])

    def test_source_scanner_masks_nested_comments_and_multiline_strings(self):
        source = b'''/- import Hidden /- #print axioms Hidden.a -/ -/
import Init -- import Hidden
def message := "text with escaped quote \\" and nested comment marker /-
import Hidden
#print axioms Hidden.b
"
#print /- separator -/ axioms A.claim
'''
        self.assertEqual(VERIFY.source_commands(source), (['Init'], ['A.claim']))

    def test_rehashed_source_import_and_audit_mismatches(self):
        for extra, reason in [(b'import Lean\n', 'Source import commands'),
                              (b'#print axioms Extra.claim\n', 'Source axiom commands')]:
            with self.subTest(extra=extra):
                self.setUp()
                self.sources['src/A.lean'] += extra
                plan = json.loads(self.map_bytes)
                plan['modules'][0]['source_sha256'] = VERIFY.sha(self.sources['src/A.lean'])
                self.map_bytes = VERIFY.encode(plan)
                self.reject(reason)

    def test_source_scanner_rejects_unterminated_or_unsupported_commands(self):
        for source in [b'/- open', b'def s := "open', b'import Foo; import Bar',
                       b'#print axioms A.claim extra']:
            with self.subTest(source=source), self.assertRaises(VERIFY.ReconciliationError):
                VERIFY.source_commands(source)

    def test_archive_rejects_duplicates_links_and_traversal(self):
        for mode in ['duplicate', 'link', 'traversal']:
            with self.subTest(mode=mode):
                output = io.BytesIO()
                with tarfile.open(fileobj=output, mode='w:gz') as stream:
                    member = tarfile.TarInfo('../escape' if mode == 'traversal' else 'src/A.lean')
                    if mode == 'link':
                        member.type = tarfile.SYMTYPE
                        member.linkname = '/outside'
                    stream.addfile(member, io.BytesIO())
                    if mode == 'duplicate':
                        stream.addfile(member, io.BytesIO())
                with self.assertRaisesRegex(VERIFY.ReconciliationError, 'archive member'):
                    VERIFY.archive(output.getvalue())


if __name__ == '__main__':
    unittest.main()
