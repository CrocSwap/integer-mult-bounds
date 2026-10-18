"""Full original macro schedule, packed or original arithmetic, same fixture."""
import argparse
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import resource
import sys
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import adapter
from lanes import need


def vendor():
    adapter.authenticate()
    spec = importlib.util.spec_from_file_location('tensor_oracle', HERE / 'vendor/oracle.py')
    oracle = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(oracle)
    tree = ast.parse((HERE / 'vendor/verify.py').read_bytes())
    nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'fixture']
    need(len(nodes) == 1, 'one retained fixture')
    ns = {}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), 'credited_fixture', 'exec'), ns)
    return oracle, ns['fixture']


def digest(values):
    return hashlib.sha256(json.dumps(values, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def run(mode='packed', multiplicity=1, fixture='promoted', plan='derived'):
    n, width = 9 * multiplicity, 160
    oracle, make_fixture = vendor()
    sources, query, f, beta = make_fixture(multiplicity, fixture)
    value_width = max(8, max(abs(z).bit_length() for field in sources+[query] for pair in field for z in pair) + 2)
    module, context = adapter.load(n, width, mode == 'packed', value_width=value_width)
    source_digests, query_digest = [digest(x) for x in sources], digest(query)
    d = next(k for k in range(width, 0, -1) if k**1000 <= width**997)
    parameters = dict(width=width, d=d, spacing=1, suffix=(width+d-1)//d, outer=7*multiplicity)
    if plan == 'defaults':
        parameters = dict(width=width, d=2, spacing=2, suffix=1, outer=3)
    engine = module.Executor(n, **parameters)
    start = time.perf_counter()
    packed_sources = [context.pack(x) for x in sources] if mode == 'packed' else sources
    packed_query = context.pack(query) if mode == 'packed' else query
    recipe = module.SOURCE['recipes'][0]
    result = module.collector(engine, packed_sources, packed_query, f, beta, recipe, multiplicity)
    result = {key: (list(value) if key != 'grid' else value) for key, value in result.items()}
    elapsed = time.perf_counter() - start
    oracle_start = time.perf_counter()
    F, total, fine, sent, updated = oracle.collector_query(sources, query, f, beta, recipe, multiplicity)
    for key, expected in [('entrance', total), ('sent', sent), ('query', updated), ('returned', fine)]:
        need(result[key] == expected, 'complete independent array: ' + key)
    need(result['grid'] == F, 'same working grid')
    need(all(x == (0, 0) for x in result['private']), 'complete private zero')
    need([digest(x) for x in sources] == source_digests and digest(query) == query_digest, 'original entrances preserved')
    need([list(x) for x in packed_sources] == sources and list(packed_query) == query, 'borrowed evaluator inputs preserved')
    need(engine.counts['address_gates'] == 52 and engine.counts['address_oracles'] == 104, 'unchanged four wrapper schedule')
    # Corroborate the published predecessor receipt when this fixture is retained.
    previous = json.loads((HERE / 'vendor/RESULT.json').read_text())
    match = [row for row in previous['cases'] if row['multiplicity'] == multiplicity and row['mode'] == fixture]
    if match:
        need(len(match) == 1, 'unique retained tensor fixture')
        row = match[0]
        need(row['source_sha256'] == source_digests and row['entrance_query_sha256'] == query_digest,
             'retained predecessor entrances')
        need(row['output_grid'] == F and row['query_sha256'] == digest(updated) and row['sent_sha256'] == digest(sent),
             'retained predecessor output receipt')
    oracle_elapsed = time.perf_counter() - oracle_start
    return dict(mode=mode, multiplicity=multiplicity, components=1<<n, fixture=fixture,
                plan=plan, parameters=parameters, packed_payload_bits=context.bits, grid=F, counts=engine.counts,
                source_sha256=source_digests, entrance_query_sha256=query_digest,
                arrays={k:digest(v) for k,v in result.items() if k != 'grid'},
                private_zero=True, full_array_comparison=True,
                execution_seconds=elapsed, oracle_check_seconds=oracle_elapsed,
                peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                python=sys.version)


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--mode',choices=['packed','original'],default='packed')
    p.add_argument('--multiplicity',type=int,choices=[1,2],default=1)
    p.add_argument('--fixture',choices=['promoted','rounding','cancellation','zero'],default='promoted')
    p.add_argument('--plan',choices=['derived','defaults'],default='derived')
    p.add_argument('--check-result', action='store_true')
    args=p.parse_args()
    result=run(args.mode,args.multiplicity,args.fixture,args.plan)
    if args.check_result:
        need(args.mode == 'packed' and args.multiplicity == 2 and args.fixture == 'promoted' and args.plan == 'derived', 'registered tensor fixture')
        from verify import stable, equal
        equal(stable(result), json.loads((HERE / 'RESULT.json').read_text())['tensor'], 'typed retained tensor receipt')
    print(json.dumps(result,indent=2,sort_keys=True))
    print('PASS_P104_PACKED_TENSOR' if args.check_result else 'PASS_PACKED_COLLECTOR complete_arrays_and_cleanup', file=sys.stderr)


if __name__ == '__main__':
    main()
