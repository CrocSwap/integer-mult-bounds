"""Registered, deterministic replay of the scoped certificate package."""
from pathlib import Path
import argparse
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from source_binding import ROOT, authenticate, inputs, require
import operator_ring
import dual_certificate
import owned_lowering
import invoice
import scan_audit
import check_controls


def formal():
    caller, old, word, bases = inputs()
    return {'forward': operator_ring.replay(caller),
            'independent_backward_covectors': dual_certificate.certificate(caller),
            'universal_scope': 'Commuting Q,D_1,...,D_18 with Q^4=I; exact independent input coefficients. No finite D substitutions.'}


def closure():
    caller, old, word, bases = inputs()
    binding, patch = owned_lowering.inventory(caller, word)
    return {'source_expansion': binding,
            'adapter_binding': owned_lowering.adapter_records(caller, word, bases),
            'physical_scan_costs': scan_audit.verify()}


def complete_invoice():
    caller, old, word, bases = inputs()
    # Bind declared caller target masks to the supplied source root objects.
    for name, source in (('root_A_6936.json', old), ('root_A_efree.json', caller)):
        root = json.loads((ROOT/'data'/name).read_bytes())
        require(root['n'] == source['types']['A']['roles'] and len(root['stages']) == 18, 'actual root/caller role interface')
        masks = [[int(r in stage['mask']) for stage in root['stages']] for r in range(root['n'])]
        require([[-1, 0]+mask for mask in masks] == source['types']['A']['diagonal'], 'every literal root mask binds its caller target')
    return invoice.verify(old, caller, word)


SUITES = {'formal': formal, 'closure': closure, 'invoice': complete_invoice,
          'controls': check_controls.verify}


def canonical(value):
    return json.loads(json.dumps(value, sort_keys=True))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--suite', choices=SUITES)
    parser.add_argument('--regenerate', action='store_true')
    args = parser.parse_args()
    count = authenticate()
    if args.regenerate:
        require(args.suite is None, 'regeneration writes the complete result only')
        result = {name: canonical(fn()) for name, fn in SUITES.items()}
        result['source_files_authenticated'] = count
        (ROOT/'RESULT.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
        caller, old, word, bases = inputs()
        patch = owned_lowering.inventory(caller, word)[1]
        (ROOT/'QSELF-PATCH.json').write_text(json.dumps(patch, separators=(',', ':'))+'\n')
        print('WROTE_QSELF_OWNED_RECEIPTS')
        return
    require(args.suite is not None, 'choose an explicit registered suite')
    expected = json.loads((ROOT/'RESULT.json').read_bytes())
    result = canonical(SUITES[args.suite]())
    require(expected[args.suite] == result and expected['source_files_authenticated'] == count, 'exact stored scoped result')
    if args.suite == 'closure':
        caller, old, word, bases = inputs()
        patch = canonical(owned_lowering.inventory(caller, word)[1])
        require(json.loads((ROOT/'QSELF-PATCH.json').read_bytes()) == patch, 'exact complete published IR patch')
    print(json.dumps(result, sort_keys=True))
    print('PASS_QSELF_OWNED_'+args.suite.upper())


if __name__ == '__main__':
    main()
