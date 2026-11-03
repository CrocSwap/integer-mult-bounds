#!/usr/bin/env python3
"""Non-executing binding of reviewed source tariff clauses.

This authenticates bytes and matches a written, reviewed source contract to AST
clauses. It does not prove a tariff's physical meaning or execute source code.
Source tariff fragments retain Ali Romman's and predecessor authors' credit.
Prepared for DLamdata with substantial OpenAI Codex assistance; Apache-2.0.
"""
import argparse
import ast
from hashlib import sha256
import json
from pathlib import Path

PINS = {
    'pr6545': '924820ca1a75324e4a73e43361b9a6907d06d2d6ff56b26464a4e58400a81254',
    'pr6551': '9d69fdfbeb15e80f9cc2637a3c239203b2d8fa0daaf50e51d45a26034b752ef7',
}

# This is an explicit copied SOURCE CONTRACT, not an independently proved law.
# The scientific counters remain independently implemented in accounting.py.
TARIFF_PREFIX = """
paid, targets = Counter(), Counter()
counts = Counter(e[0] for e in word['events'])
need(local['helpers'] == native['helpers'], 'All source helper targets have native maps')
idle = Counter()
for event in word['events']:
    if event[0] == 'LOCAL':
        paid.update(local['paid'])
        targets.update(local['helpers'])
    elif event[0] == 'QUERY':
        paid[1] += 104
    elif event[0] in ('IDLE', 'IDLE_ONE'):
        rank = 8*len(event[3] if event[0] == 'IDLE' else event[2])
        count = 208 if event[0] == 'IDLE' else 104
        paid[rank] += count
        idle[rank] += count
main = Counter()
for term in word['diagonal']:
    main[int(term[0] % 2)+8*sum(term[1:])] += 104
targets.update(main)
"""
ROUTE_ASSIGNMENT = "local_routes = (sum(local['paid'].values())+native['helper_normalizers']+native['main_adapters']+4*104+4*local['owned_lifetimes'])*1000"
RAW_ASSIGNMENT = "raw = 18*10**7 + 17*1664 + 32*35*104*len(word['events']) + 35*104*(26+1000)"
LOCAL_BUDGET = "need(local['real_scalar_allowance']+local_routes < 10**7, 'Every local ordinary operation is funded')"
RAW_BUDGET = "need(raw < 10**9, 'Complete ordinary-work budget')"


def need(test, reason):
    if not test:
        raise ValueError(reason)


def form(node):
    return ast.dump(node, include_attributes=False)


def tree(source):
    return ast.parse(source)


def matching_statement(function, source, label):
    expected = form(tree(source).body[0])
    matches = [n for n in function.body if form(n) == expected]
    need(len(matches) == 1, label)
    return {'first_line': matches[0].lineno, 'last_line': matches[0].end_lineno}


def inspect_clauses(text):
    """Test static syntax only. A changed source must be explicitly re-reviewed."""
    module = tree(text)
    functions = {}
    for name in ('assemble','run'):
        nodes = [n for n in module.body if isinstance(n,ast.FunctionDef) and n.name == name]
        need(len(nodes) == 1, 'unique top-level '+name)
        functions[name] = nodes[0]
    expected = tree(TARIFF_PREFIX).body
    actual = functions['assemble'].body[:len(expected)]
    need([form(x) for x in actual] == [form(x) for x in expected], 'reviewed tariff prefix')
    return {
        'tariff_prefix': {'first_line': actual[0].lineno, 'last_line': actual[-1].end_lineno},
        'local_routes': matching_statement(functions['run'],ROUTE_ASSIGNMENT,'reviewed local route formula'),
        'raw': matching_statement(functions['run'],RAW_ASSIGNMENT,'reviewed raw ordinary formula'),
        'local_budget': matching_statement(functions['run'],LOCAL_BUDGET,'reviewed local allowance'),
        'raw_budget': matching_statement(functions['run'],RAW_BUDGET,'reviewed raw allowance'),
    }


def bind(raw, label):
    need(sha256(raw).hexdigest() == PINS[label], 'exact pricing source pin: '+label)
    return {'sha256':PINS[label],'clauses':inspect_clauses(raw.decode('utf-8'))}


def reject(action, expected):
    try:
        action()
    except ValueError as error:
        need(str(error) == expected, 'unexpected control rejection: '+str(error))
        return str(error)
    raise ValueError('control accepted: '+expected)


def run(old_path, new_path):
    old,new = old_path.read_bytes(),new_path.read_bytes()
    result = {'pr6545':bind(old,'pr6545'),'pr6551':bind(new,'pr6551')}
    text = new.decode()
    # The first control tests the immutable source boundary. The subsequent
    # controls call the static clause checker directly to demonstrate that
    # clause matching also rejects changes even if a pin were regenerated.
    need(text.count('paid[1] += 104') == 1, 'unique query mutation site')
    tariff_mutant = text.replace('paid[1] += 104','paid[1] += 103')
    need(text.count('32*35*104*len') == 1, 'unique ordinary mutation site')
    ordinary_mutant = text.replace('32*35*104*len','31*35*104*len')
    controls = {
        'changed_source_pin':reject(lambda:bind(tariff_mutant.encode(),'pr6551'),'exact pricing source pin: pr6551'),
        'changed_query_tariff_clause':reject(lambda:inspect_clauses(tariff_mutant),'reviewed tariff prefix'),
        'changed_raw_tariff_clause':reject(lambda:inspect_clauses(ordinary_mutant),'reviewed raw ordinary formula'),
    }
    return {
        'status':'PASS_REVIEWED_PRICING_SOURCE_BINDING',
        'sources':result,
        'controls':controls,
        'coverage':'Immutable bytes and static source clauses only; no pricing source executes, and tariff validity is a retained physical premise.'
    }


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('predecessor',type=Path)
    parser.add_argument('candidate',type=Path)
    args=parser.parse_args()
    print(json.dumps(run(args.predecessor,args.candidate),sort_keys=True,indent=2))
