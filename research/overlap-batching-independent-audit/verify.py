#!/usr/bin/env python3
"""Independent finite API/failure audit of Arham Garg's PR2493.

Arham Tahir, with substantial OpenAI Codex assistance. Apache-2.0.
Only authenticated source bytes execute; no network or Git is required.
"""
import ast
import base64
import copy
import hashlib
import itertools
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import types

HERE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def authenticated_sources(directory=HERE):
    records = json.loads((directory / 'DEPENDENCIES.json').read_text(encoding='utf-8'))
    answer = {}
    # Authenticate every input before compiling any of them.
    for record in records:
        data = (directory / record['local_path']).read_bytes()
        require(hashlib.sha256(data).hexdigest() == record['sha256'], 'source SHA mismatch')
        blob = b'blob ' + str(len(data)).encode() + b'\0' + data
        require(hashlib.sha1(blob).hexdigest() == record['git_blob'], 'source blob mismatch')
        answer[Path(record['local_path']).name] = data
    require(set(answer) == {'baseline.py', 'candidate.py', 'candidate-tests.py'}, 'source inventory')
    return answer


def load(data, name):
    module = types.ModuleType(name)
    module.__file__ = str(HERE / 'sources' / (name + '.py'))
    exec(compile(data, module.__file__, 'exec'), module.__dict__)
    return module


def item(identity):
    return {'id':identity, 'body':'Repeated claim κ\n\u0085\u2028\u2029',
            'url':'https://example.invalid/' + identity, 'updatedAt':'2026-10-15T21:00:00Z'}


def corpus(thread_count, comment_count, reply_count):
    """Replies exercise both the embedded and subsequent comment pages."""
    threads = []
    for i in range(thread_count):
        thread = dict(item('thread-' + str(i)), number=1000+i, title='Question ' + str(i))
        thread['children'] = []
        # A second busy thread detects a wrongly reused connection cursor.
        for j in range(comment_count if i in (0, thread_count-1) else i % 3):
            comment = item(f'thread-{i}-comment-{j}')
            n = reply_count if j in (0, 5, comment_count-1) else j % 2
            comment['children'] = [item(f'thread-{i}-comment-{j}-reply-{k}') for k in range(n)]
            thread['children'].append(comment)
        threads.append(thread)
    return threads


def direct_records(threads):
    """No cursors, API page sizes, or collector code enter this oracle."""
    result = []
    for thread in threads:
        def emit(kind, node):
            result.append({'kind':kind, 'number':thread['number'], 'title':thread['title'],
                           'body':node['body'], 'url':node['url'], 'updated_at':node['updatedAt']})
        emit('discussion', thread)
        for comment in thread['children']:
            emit('discussion-comment', comment)
            for reply in comment['children']:
                emit('discussion-reply', reply)
    return result


class API:
    def __init__(self, threads, fail_at=None, failure='graphql'):
        self.threads = threads
        self.nodes = {node['id']:node for thread in threads
                      for node in [thread, *thread['children']]}
        self.calls = []
        self.fail_at, self.failure = fail_at, failure

    @staticmethod
    def page(nodes, size, cursor, owner):
        start = 0
        if cursor is not None:
            decoded_owner, start = json.loads(base64.b64decode(cursor, validate=True))
            require(decoded_owner == owner and 0 < start <= len(nodes), 'wrong connection cursor')
        end = min(start+size, len(nodes))
        opaque = base64.b64encode(json.dumps([owner, end]).encode()).decode() if end else None
        return {'nodes':[{k:v for k,v in node.items() if k != 'children'}
                         for node in nodes[start:end]],
                'pageInfo':{'hasNextPage':end < len(nodes), 'endCursor':opaque}}

    def comments(self, thread, size, reply_size, cursor):
        page = self.page(thread['children'], size, cursor, thread['id'] + ':comments')
        for node in page['nodes']:
            node['replies'] = self.page(self.nodes[node['id']]['children'], reply_size, None,
                                        node['id'] + ':replies')
        return page

    def __call__(self, query, variables):
        self.calls.append((query, copy.deepcopy(variables)))
        if len(self.calls) == self.fail_at:
            if self.failure == 'transport':
                raise OSError('injected transport failure')
            if self.failure == 'malformed':
                return {}  # Required connection absent: no partial cache admission.
            raise ValueError('GitHub GraphQL errors: injected page failure')
        sizes = dict((name,int(size)) for name,size in re.findall(
            r'(discussions|comments|replies)\(first:(\d+)', query))
        require(sizes and all(0 < n <= 100 for n in sizes.values()), 'unexpected query')
        cursor = variables['cursor']
        if 'discussions' in sizes:
            result = self.page(self.threads, sizes['discussions'], cursor, 'listing')
            if 'comments' in sizes:
                for node in result['nodes']:
                    node['comments'] = self.comments(self.nodes[node['id']], sizes['comments'],
                                                     sizes['replies'], None)
            return {'repository':{'discussions':result}}
        node = self.nodes[variables['id']]
        if 'comments' in sizes:
            result = self.comments(node, sizes['comments'], sizes['replies'], cursor)
            return {'node':{'comments':result}}
        return {'node':{'replies':self.page(node['children'], sizes['replies'], cursor,
                                           node['id'] + ':replies')}}


def collect(module, threads):
    api = API(threads)
    module.graphql = api
    records = module.fetch_discussions()
    require(records == direct_records(threads), 'ordered record mismatch')
    return len(api.calls)


def failure_checks(module, threads, work):
    request_count = collect(module, threads)
    previous = {'fetched_at':'2020-01-02T03:04:05+00:00', 'complete_pagination':True,
                'records':[{'kind':'discussion', 'body':'Previously complete sentinel'}]}
    cases = 0
    for fail_at, failure, existing in itertools.product(
            range(1, request_count+1), ('graphql','transport','malformed'), (False,True)):
        cache = work / 'cache.json'
        cache.unlink(missing_ok=True)
        if existing:
            cache.write_text(json.dumps({'schema_version':1,
                'repository':'CrocSwap/integer-mult-bounds',
                'sources':{'discussions':previous}}), encoding='utf-8')
        module.graphql = API(threads, fail_at, failure)
        module.gh_json = lambda *args, **kwargs: [[]]
        snapshot, warnings = module.remote_snapshot(cache, refresh=True)
        stored = json.loads(cache.read_text(encoding='utf-8'))
        require(any('discussions: refresh failed' in w for w in warnings), 'missing failure warning')
        require(len(module.graphql.calls) == fail_at, 'failure injection missed')
        for observed in (snapshot, stored):
            if existing:
                require(observed['sources']['discussions'] == previous, 'changed complete source or timestamp')
            else:
                require('discussions' not in observed['sources'], 'partial first-fetch source admitted')
        cases += 1
    return {'request_positions':request_count, 'failure_cases':cases}


def corruption_controls(sources, work):
    isolated = work / 'corrupted'
    isolated.mkdir()
    (isolated / 'sources').mkdir()
    (isolated / 'DEPENDENCIES.json').write_bytes((HERE / 'DEPENDENCIES.json').read_bytes())
    for name, data in sources.items():
        (isolated / 'sources' / name).write_bytes(data)
    for name, data in sources.items():
        # This would execute a visible failure if authentication happened too late.
        (isolated / 'sources' / name).write_bytes(data + b'\nraise RuntimeError("executed corrupt source")\n')
        try:
            authenticated_sources(isolated)
        except ValueError as error:
            require(str(error) == 'source SHA mismatch', 'unexpected source rejection')
        else:
            raise ValueError('corrupt source admitted')
        (isolated / 'sources' / name).write_bytes(data)
    return len(sources)


def inherited_tests(sources, work):
    root = work / 'predecessor-tests'
    (root / 'scripts').mkdir(parents=True)
    (root / 'tests').mkdir()
    script = root / 'tests/test_research_discussion_batching.py'
    script.write_bytes(sources['candidate-tests.py'])
    (root / 'scripts/find_overlap.py').write_bytes(sources['candidate.py'])
    for options in ([], ['-O']):
        result = subprocess.run([sys.executable, '-I', *options, '-B', str(script)],
            capture_output=True, text=True, encoding='utf-8', timeout=60, cwd=root)
        require(result.returncode == 0 and 'Ran 6 tests' in result.stderr,
                'predecessor suite failed: ' + result.stderr[-2000:])
    return {'tests':6, 'modes':['normal','optimized']}


def run():
    sources = authenticated_sources()
    modules = {name:load(sources[name + '.py'],name) for name in ('baseline','candidate')}
    thresholds = (0,1,4,5,6,99,100,101,104,105,106,205)
    cases = records = parameter_cases = 0
    seen = set()
    for n,c,r in itertools.product((0,1,49,50,51,101), thresholds, thresholds):
        parameter_cases += 1
        threads = corpus(n,c,r)
        digest = hashlib.sha256(json.dumps(threads,sort_keys=True).encode()).hexdigest()
        if digest in seen:
            continue
        seen.add(digest)
        for module in modules.values():
            collect(module, threads)
        cases += 1
        records += len(direct_records(threads))
    small = corpus(101,4,4)
    request_counts = {name:collect(module,small) for name,module in modules.items()}
    require(request_counts == {'baseline':104,'candidate':3}, 'small-thread request count')
    busy = corpus(51,205,205)
    with tempfile.TemporaryDirectory(prefix='overlap-independent-') as tmp:
        work = Path(tmp)
        failures = {name:failure_checks(module,busy,work) for name,module in modules.items()}
        source_controls = corruption_controls(sources,work)
        inherited = inherited_tests(sources,work)
    mutants = {}
    for label, expression in (
            ('stop_comments','connection'), ('stop_replies','replies'), ('stop_listing','result')):
        before = f'if not {expression}["pageInfo"]["hasNextPage"]:'
        code = sources['candidate.py'].decode('utf-8')
        function = next(node for node in ast.parse(code).body
                        if isinstance(node,ast.FunctionDef) and node.name == 'fetch_discussions')
        lines = code.splitlines(keepends=True)
        body = ''.join(lines[function.lineno-1:function.end_lineno])
        require(body.count(before) == 1, 'mutation site changed')
        lines[function.lineno-1:function.end_lineno] = [body.replace(before,'if True:')]
        mutant = load(''.join(lines).encode(),'mutant')
        try:
            collect(mutant,busy)
        except ValueError as error:
            require(str(error) == 'ordered record mismatch', 'unexpected mutant rejection')
            mutants[label] = 'ordered record mismatch'
        else:
            raise ValueError('truncation mutant accepted')
    return {'status':'PASS_OVERLAP_BATCHING_INDEPENDENT_AUDIT',
            'parameter_cases':parameter_cases,'static_graph_cases':cases,'records_per_collector':records,
            'boundary_sizes':list(thresholds),'thread_counts':[0,1,49,50,51,101],
            'small_thread_requests':request_counts,'fault_injection':failures,
            'source_corruptions_rejected':source_controls,'truncation_mutants':mutants,
            'predecessor_suite':inherited,
            'scope':'Finite static-API and cache-failure audit; no live timing, adoption or kappa claim.'}


if __name__ == '__main__':
    result = run()
    if sys.argv[1:] == ['--write']:
        (HERE / 'RESULT.json').write_text(json.dumps(result,indent=2) + '\n', encoding='utf-8')
    else:
        require(not sys.argv[1:], 'unknown argument')
        expected = json.loads((HERE / 'RESULT.json').read_text(encoding='utf-8'))
        require(json.dumps(result,sort_keys=True) == json.dumps(expected,sort_keys=True), 'receipt mismatch')
    print(json.dumps(result,indent=2))
