#!/usr/bin/env python3
"""Byte binding and finite transition witnesses, not interpreter fault injection.

Chris R / Clear1nsight with substantial OpenAI Codex/ChatGPT Pro assistance.
New model: Apache-2.0. External CPython excerpts retain LICENSE-CPYTHON.txt.
"""
import hashlib
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
REPO = PACKAGE.parent.parent
CP = 'f6650f9ad73359051f3e558c2431a109bc016664'
S = '608ad23adc6c01264c8195daf7f18e29c17464a7'


def need(condition, message):
    if not condition:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def acquisition(descriptor, fail_conversion):
    """C acquisition has succeeded; model only the Python integer conversion.

    0..256 are cached in the inspected source. No actual descriptor exists.
    A returned integer still needs separate ownership registration.
    """
    need(type(descriptor) is int and descriptor >= 0, 'descriptor domain')
    need(not fail_conversion or descriptor >= 257,
         'no allocation site at cached positive integer conversion')
    return {'kernel_acquired': True,
            'python_returned': not fail_conversion,
            'pending': 'M' if fail_conversion else None}


def delivery(frame_ready, failure, journaled):
    """Abstract the cited take/allocate/drop/restore and traceback-chain paths.

    E, M and T are symbolic identity labels. Reachability counts only roots
    in this abstraction. This function does not simulate real refcounts, GC,
    allocator behavior, complete C semantics or actual target execution.
    """
    need(type(frame_ready) is bool and type(journaled) is bool, 'flag domain')
    need(failure in ('none', 'frame', 'traceback'), 'failure site')
    need(not (frame_ready and failure == 'frame'), 'no fresh-frame site')
    pending = 'E'
    journal = ('E', 'T') if journaled else ()
    context = None
    saved = None
    if not frame_ready:
        saved, pending = pending, None  # PyErr_GetRaisedException clears it.
        if failure == 'frame':
            pending = 'M'              # frame allocation failed.
            saved = None               # failure branch decreferences saved E.
        else:
            pending, saved = saved, None  # successful branch restores it.
    if pending == 'E' and failure == 'traceback':
        saved, pending = pending, None
        pending = 'M'
        context, saved = saved, None    # _PyErr_ChainExceptions1.
    return {'outward': pending, 'journal': journal, 'context': context,
            'E_reachable': journaled or pending == 'E' or context == 'E'}


def verify_sources():
    record = json.loads((PACKAGE / 'SOURCE-EXCERPTS.json').read_text())
    sources = record['sources']
    windows = record['excerpts']
    need(len(sources) == 11 and len(windows) == 19, 'source dimensions')
    ids = {row['id'] for row in windows}
    need(len(ids) == len(windows), 'duplicate source window')
    need(sha((PACKAGE / 'LICENSE-CPYTHON.txt').read_bytes()) ==
         record['cpython_license_sha256'], 'CPython license bytes')
    for key, source in sources.items():
        expected = S if key == 'S-parent' else CP
        need(source['commit'] == expected, 'source revision ' + key)
        need(len(source['sha256']) == 64 and source['bytes'] > 0,
             'whole-source identity ' + key)
    for row in windows:
        source = sources[row['source']]
        need(row['first_line'] >= 1 and row['last_line'] >= row['first_line'],
             'line domain ' + row['id'])
        need(len(row['text'].splitlines()) ==
             row['last_line'] - row['first_line'] + 1, 'line count ' + row['id'])
        need(sha(row['text'].encode()) == row['sha256'], 'window bytes ' + row['id'])
        expected_url = (f"https://github.com/{source['repository']}/blob/"
                        f"{source['commit']}/{source['path']}#L"
                        f"{row['first_line']}-L{row['last_line']}")
        need(row['url'] == expected_url, 'source URL ' + row['id'])
    by_id = {row['id']: row['text'] for row in windows}
    # These checks bind the model to inspected branch text; they do not parse
    # C or prove that this abstraction implements its entire operational model.
    for key, terms in {
        'capture-loss': ['PyErr_GetRaisedException()', 'if (f == NULL)',
                         'Py_XDECREF(exc)', 'PyErr_SetRaisedException(exc)'],
        'take-current': ['tstate->current_exception = NULL'],
        'before-handler': ['PyTraceBack_Here(f)', 'JUMPTO(handler)'],
        'traceback-replacement': ['if (newtb == NULL)', '_PyErr_ChainExceptions1(exc)'],
        'chain-context': ['PyException_SetContext(exc2, exc)',
                          '_PyErr_SetRaisedException(tstate, exc2)'],
        'open-convert': ['os_open_impl', 'PyLong_FromLong', 'path_cleanup(&path)'],
        'pidfd-acquire-convert': ['syscall(__NR_pidfd_open', 'PyLong_FromLong(fd)'],
        'integer-cache': ['_PY_NSMALLPOSINTS           257'],
        'integer-allocation': ['PyObject_Malloc', 'PyErr_NoMemory()'],
        'S-cleanup-handler': ['os.close(descriptor)', 'except BaseException as error'],
        'S-propagation': ['raise error.with_traceback(traceback)'],
    }.items():
        for term in terms:
            need(term in by_id[key], 'missing source anchor ' + key + ': ' + term)
    manifest = json.loads((PACKAGE / 'SOURCES.json').read_text())
    inputs = [r for r in manifest['files'] if r.get('usage') == 'input']
    need(len(inputs) == 3, 'canonical input count')
    for row in inputs:
        need(sha((REPO / row['path']).read_bytes()) == row['sha256'],
             'canonical contract bytes ' + row['path'])
    caller = next(r for r in inputs if 'CALLER-EQUALITY' in r['path'])
    contract = (REPO / caller['path']).read_text()
    need('"id": "CP12"' in contract and '"id": "CP15"' in contract,
         'original contract scope')
    return len(windows)


def verify_transitions():
    cases = []
    for fd, fail, expected in [(3, False, True), (257, False, True),
                               (257, True, False)]:
        state = acquisition(fd, fail)
        need(state['kernel_acquired'] and state['python_returned'] is expected,
             'acquisition witness/control')
        need(state['pending'] == ('M' if fail else None), 'conversion exception')
        cases.append({'kind': 'acquisition', 'fd': fd, 'failure': fail, **state})
    # Two no-failure controls and three admitted one-failure placements, each
    # with and without an external E/T journal root: ten delivery cases.
    paths = [(False, 'none', 'E', None), (True, 'none', 'E', None),
             (False, 'frame', 'M', None),
             (False, 'traceback', 'M', 'E'),
             (True, 'traceback', 'M', 'E')]
    for ready, failure, outward, context in paths:
        for journaled in (False, True):
            state = delivery(ready, failure, journaled)
            need(state['outward'] == outward and state['context'] == context,
                 'outward identity / context witness')
            need(state['journal'] == (('E', 'T') if journaled else ()),
                 'journal identity labels')
            need(state['E_reachable'] is
                 (journaled or failure != 'frame'), 'raw reachability boundary')
            cases.append({'kind': 'delivery', 'frame_ready': ready,
                          'failure': failure, **state})
    need(len(cases) == 13, 'finite case count')
    # Reject inconsistent fault placements instead of treating an impossible
    # failure at a nonallocating site as an additional admitted witness.
    for thunk in (lambda: acquisition(3, True),
                  lambda: delivery(True, 'frame', False)):
        try:
            thunk()
        except ValueError:
            pass
        else:
            raise ValueError('impossible fault placement accepted')
    return cases


def main():
    windows = verify_sources()
    cases = verify_transitions()
    print(json.dumps({'transition_cases': cases, 'source_windows': windows,
        'target_runtime_qualified': False, 'original_acceptance': False,
        'C_execution': False, 'target_fault_injection': False}, sort_keys=True))
    print('PASS_G12_INTERPRETER_BOUNDARY transition_cases=13 source_windows=19 '
          'target_runtime_qualified=false original_acceptance=false')


if __name__ == '__main__':
    main()
