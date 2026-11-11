#!/usr/bin/env python3
"""Parent-only outer capture/finally for one independently reviewed v26 run."""
from pathlib import Path
import hashlib, json, math, os, resource, selectors, signal, stat, subprocess, time
D = Path(__file__).resolve().parents[1]
SOURCE = D / 'implementation'
OUT = D / 'parent-validation'
INVENTORY_SHA = 'f9755bce336e48fa8ed5848aac97b91ec193941f9c811327e3bed8578d8a316d'
ORACLE_SHA = '864d60783c206b1e004e9d68f9372c894843e4ba0c3d356da9468269e5692e0a'
CAP = 1024 * 1024
def sha(raw): return hashlib.sha256(raw).hexdigest()
def saved(path, obj):
    raw = (json.dumps(obj, sort_keys=True, indent=2, allow_nan=False) + '\n').encode()
    with path.open('xb') as f:
        if f.write(raw) != len(raw): raise RuntimeError('partial parent record')
        f.flush(); os.fsync(f.fileno())
    if path.read_bytes() != raw: raise RuntimeError('parent record readback')
def limits():
    resource.setrlimit(resource.RLIMIT_AS, (1024**3, 1024**3))
    resource.setrlimit(resource.RLIMIT_CPU, (180, 180))
    resource.setrlimit(resource.RLIMIT_FSIZE, (64*1024**2, 64*1024**2))
def pinned(root, rows):
    out = []
    for row in rows:
        p = root / row['path']
        if p.is_symlink() or not p.is_file(): raise RuntimeError('missing or alias pin')
        raw = p.read_bytes()
        ok = len(raw) == row['bytes'] and sha(raw) == row['sha256']
        out.append({'path': row['path'], 'match': ok})
        if not ok: raise RuntimeError('changed pin: ' + row['path'])
    return {'matched': len(out), 'files': out}
OUT.mkdir(mode=0o700, exist_ok=False)
record = {'schema':'parent-outer-v26-run-v1', 'status':'INCOMPLETE',
          'original_execution':False, 'native_or_decoder_execution':False,
          'new_budget':False, 'errors':[], 'complete_physical_costs':'OPEN_NOT_ZERO'}
command = ['/usr/bin/python3', '-B', str(SOURCE/'validation/run_reviewed_constructor.py'),
           INVENTORY_SHA, ORACLE_SHA]
record['command'] = command
started = time.monotonic()
before = resource.getrusage(resource.RUSAGE_CHILDREN)
own_before = resource.getrusage(resource.RUSAGE_SELF)
process = None
rows = None
try:
    frozen = (SOURCE/'validation/EXECUTION-INVENTORY-v2.json').read_bytes()
    if sha(frozen) != INVENTORY_SHA: raise RuntimeError('inventory pin')
    oracle = (D/'review/INDEPENDENT-EXPECTED-OUTCOMES-v26-v1.json').read_bytes()
    if sha(oracle) != ORACLE_SHA: raise RuntimeError('oracle pin')
    rows = json.loads(frozen)['files']
    record['source_before'] = pinned(SOURCE, rows)
    env = {k:os.environ[k] for k in ('PATH','LANG','LC_ALL','TZ') if k in os.environ}
    env.update(PATH='/usr/bin:/bin', LANG='C.UTF-8', LC_ALL='C.UTF-8',
               TZ='UTC', PYTHONHASHSEED='0', PYTHONDONTWRITEBYTECODE='1')
    with (OUT/'wrapper.stdout').open('xb') as stdout, (OUT/'wrapper.stderr').open('xb') as stderr:
        streams = {'stdout':stdout, 'stderr':stderr}
        sizes = {'stdout':0, 'stderr':0}
        process = subprocess.Popen(command, cwd=str(D), env=env, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, stdin=subprocess.DEVNULL, start_new_session=True, preexec_fn=limits)
        sel = selectors.DefaultSelector()
        sel.register(process.stdout, selectors.EVENT_READ, 'stdout')
        sel.register(process.stderr, selectors.EVENT_READ, 'stderr')
        try:
            while sel.get_map():
                if time.monotonic()-started > 90:
                    record['timeout'] = True
                    raise RuntimeError('parent90-second wall stop')
                for key, mask in sel.select(0.1):
                    name = key.data
                    block = os.read(key.fileobj.fileno(), min(65536, CAP-sizes[name]+1))
                    if not block:
                        sel.unregister(key.fileobj); key.fileobj.close(); continue
                    keep = block[:CAP-sizes[name]]
                    if streams[name].write(keep) != len(keep): raise RuntimeError('partial raw capture')
                    sizes[name] += len(keep)
                    if len(keep) != len(block): raise RuntimeError('parent raw capture overflow')
            record['returncode'] = process.wait(timeout=2)
        finally:
            sel.close()
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGKILL); process.wait(timeout=3)
            for stream in streams.values(): stream.flush(); os.fsync(stream.fileno())
        record['raw_sizes'] = sizes
    if record['returncode'] != 0: raise RuntimeError('reviewed wrapper returned nonzero')
    observed = json.loads((OUT/'wrapper.stdout').read_bytes())
    if observed.get('status') != 'COMPLETE_INERT_INSTALLATION_ONLY' or observed.get('mode_observations') != 44:
        raise RuntimeError('wrapper terminal result')
    if (OUT/'wrapper.stderr').stat().st_size != 0: raise RuntimeError('wrapper stderr')
    record['wrapper_terminal'] = observed
except BaseException as error:
    record['errors'].append({'type':type(error).__name__, 'message':str(error)[:4096]})
finally:
    if process is not None and process.poll() is None:
        os.killpg(process.pid, signal.SIGKILL); process.wait(timeout=3)
    if rows is not None:
        for key, root in [('source_after',SOURCE),('cold_after',D/'validation/cold-exact-v2')]:
            try: record[key] = pinned(root, rows)
            except BaseException as error: record['errors'].append({'stage':key,'type':type(error).__name__,'message':str(error)[:4096]})
    try:
        external = D/'validation/EXTERNAL-FINAL-v2.json'
        value = json.loads(external.read_bytes())
        record['wrapper_external_sha256'] = sha(external.read_bytes())
        record['wrapper_external_status'] = value['status']
        record['child_runs'] = value.get('runs',[])
        for mode in ('normal','optimized'):
            state = value[mode+'_finalization']
            if state['status'] != 'COMPLETE_INERT_INSTALLATION_ONLY': raise RuntimeError('mode finalization')
            stage = D/'validation'/('preparation-'+mode)/'full-stage'
            expected = json.loads((SOURCE/'payload/REQUEST-v2.json').read_bytes())['constructor_request']['manifest']
            checked = pinned(stage,[{'path':r['installed_relative_path'],'bytes':r['bytes'],'sha256':r['sha256']} for r in expected])
            record[mode+'_stage_final'] = {'file_count':checked['matched'],'all_bytes_match':True}
        if value['status'] != 'COMPLETE_INERT_INSTALLATION_ONLY' or value['errors']: raise RuntimeError('external final ledger incomplete')
    except BaseException as error:
        record['errors'].append({'stage':'parent_external_ack','type':type(error).__name__,'message':str(error)[:4096]})
    attempts = {r['tag']:r for r in record.get('child_runs',[])}
    for attempt_path in sorted((D/'validation').glob('*.attempt.json')):
        try:
            retained = json.loads(attempt_path.read_bytes())
            if retained['tag'] in attempts and attempts[retained['tag']] != retained:
                raise RuntimeError('retained child attempt mismatch')
            attempts[retained['tag']] = retained
        except BaseException as error:
            record['errors'].append({'stage':'attempt_ledger','type':type(error).__name__,'message':str(error)[:4096]})
    record['all_retained_child_attempts'] = list(attempts.values())
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    own_after = resource.getrusage(resource.RUSAGE_SELF)
    record['child_cpu_seconds'] = after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime
    record['parent_cpu_seconds'] = own_after.ru_utime+own_after.ru_stime-own_before.ru_utime-own_before.ru_stime
    record['cpu_seconds'] = record['child_cpu_seconds']+record['parent_cpu_seconds']
    record['cumulative_child_peak_rss_kib'] = after.ru_maxrss
    record['wall_seconds'] = time.monotonic()-started
    child_debit = sum(math.ceil(r['wall_seconds']) for r in attempts.values())
    record['new_conservative_policy_debit_seconds'] = max(math.ceil(record['wall_seconds']),child_debit)
    record['canonical_policy_seconds'] = 94.550533479
    record['previous_supplemental_combined_policy_seconds'] = 115.890533479
    record['supplemental_combined_policy_seconds'] = 115.890533479+record['new_conservative_policy_debit_seconds']
    if not record['errors']: record['status'] = 'PARENT_ACKNOWLEDGED_COMPLETE_INERT_PREPARATION_ONLY'
    saved(OUT/'PARENT-FINAL-ACK-v1.json',record)
print(json.dumps({'status':record['status'],'errors':record['errors'],
                  'new_policy_debit_seconds':record['new_conservative_policy_debit_seconds']}))
raise SystemExit(0 if not record['errors'] else 1)

