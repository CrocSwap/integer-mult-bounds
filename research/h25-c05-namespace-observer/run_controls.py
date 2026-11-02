"""Isolated entry for the two new-code suites; never load an archived source."""
import hashlib
import json
from pathlib import Path
import runpy
import sys
import unittest


PACKAGE = Path(__file__).resolve().parent
PINS = {
    'c05_namespace_observer_v1.py':
        'd52913c0e0a25457aa1fac39459321134304a15ac7788bd0115ddf3c8a2ba882',
    'test_c05_namespace_observer_v1.py':
        'ed1ddeff64acf69900e55ac00a38bdf1b6d249a6fc4e5843cd372f9b95618dd7',
}
for filename, expected in PINS.items():
    if hashlib.sha256((PACKAGE / filename).read_bytes()).hexdigest() != expected:
        raise RuntimeError('Frozen Pro source differs: ' + filename)
if sys.argv[1:] not in (['pro-fixtures'], ['independent']):
    raise RuntimeError('Select one declared new-code suite')
sys.path.insert(0, str(PACKAGE))
if sys.argv[1] == 'pro-fixtures':
    values = runpy.run_path(str(PACKAGE / 'test_c05_namespace_observer_v1.py'),
                           run_name='c05_pro_fixture_controls')
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(values['NamespaceFixtures'])
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    roots = [entry[1] for entry in values['FIXTURE_EVIDENCE']
             if entry[0] == 'root']
    print('RETAINED_PRO_C05_FIXTURES ' + json.dumps(roots), flush=True)
    if not result.wasSuccessful():
        raise RuntimeError('Pro-proposed fixture controls failed; evidence retained')
    print('PASS_PRO_C05_FIXTURES tests=' + str(result.testsRun))
else:
    sys.argv = [str(PACKAGE / 'verify.py')]
    runpy.run_path(sys.argv[0], run_name='__main__')
