#!/usr/bin/env python3
"""Run all historical h=8,9 small controls with optional frame-pair reuse.

Hanson Sun, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import gzip
import json
from pathlib import Path
import platform
import resource
import sys
import time

from support import (ROOT, Trace, canonical, digest, expected_controls, need,
                     observed_reference, verify_loaded_sources, verify_sources)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--engine', choices=['reference', 'cached'], default='cached')
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--trace', action='store_true')
    args = parser.parse_args()
    verify_sources()
    need(not args.out.exists(), 'Use a fresh output directory')
    args.out.mkdir(parents=True)
    start = time.perf_counter()
    sys.path.insert(0, str(ROOT / 'scripts'))
    from experiments import ternary_side as reference
    from prepare_layers import serializable
    import fast
    expected = expected_controls()
    controls = []
    measurements = []
    traces = {}
    for h in (8, 9):
        before = time.perf_counter()
        graph = reference.build(h, retain_graph=True)
        scalar = reference.verify_invocation(graph)
        observer = Trace() if args.trace else None
        stats = {}
        frame_start = time.perf_counter()
        if args.engine == 'reference':
            checker = (reference.verify_invocation_frames if observer is None
                       else observed_reference(reference, observer))
            frames = checker(graph)
        else:
            frames = fast.verify_invocation_frames(graph, observe=observer, statistics=stats)
        frame_seconds = time.perf_counter() - frame_start
        graph.pop('_graph')
        result = serializable(dict(construction=graph, scalar=scalar, frames=frames))
        # Match all historical fields, including exact DAG hashes and scalar
        # controls, not merely a summary rank count.
        need(json.loads(json.dumps(result)) == expected[h], 'Historical small controls differ')
        controls.append(result)
        measurements.append(dict(h=h, frame_seconds=frame_seconds,
                                 complete_seconds=time.perf_counter() - before,
                                 cache=stats))
        if observer is not None:
            payload = observer.payload()
            with gzip.open(args.out / ('trace-h%d.json.gz' % h), 'wb') as stream:
                stream.write(canonical(payload))
            count = sum(x['physical_edges'] for x in frames['orientations'])
            need(len(payload['edges']) == count, 'Incomplete observed physical edges')
            traces[str(h)] = dict(physical_edges=count,
                                  exact_frames=len(payload['matrices']),
                                  payload_sha256=digest(payload))
    verify_loaded_sources()
    usage = resource.getrusage(resource.RUSAGE_SELF)
    result = dict(status='PASS_TERNARY_SMALL_CONTROLS', engine=args.engine,
                  controls=controls, trace=traces, measurements=measurements,
                  elapsed_seconds=time.perf_counter() - start,
                  max_rss_bytes=usage.ru_maxrss * (1 if sys.platform == 'darwin' else 1024),
                  python=sys.version, platform=platform.platform(),
                  source_manifest_sha256=digest(verify_sources()))
    (args.out / 'RESULT.json').write_bytes(canonical(result) + b'\n')
    print(result['status'], args.engine, '84672 physical edges')


if __name__ == '__main__':
    main()
