#!/usr/bin/env python3
"""Source-bound connection inventory for the admitted JOINT259 local word.

Reads the already generated final artifact. Does not run prepare/verify, replay
all columns, or modify a supplier. The compact event inventory is lossless given
the pinned raw input. See SCHEMA for the exact columns and version conventions.
"""
import argparse
import base64
from collections import Counter
import gzip
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import struct
import sys
import zlib
from types import ModuleType
import joint259_system_docs_sources as SOURCES

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
PACKAGE = ROOT / 'pr259_interval_compatibility_20261010/hybrid_package'
INPUT = PACKAGE.parent / 'hybrid_admission/fresh_1/hybrid'
MANIFEST_SHA = '9f6d8637b9a119cfe4566a02ab2d704f23c502e5e4357b40c28ef85a3fd4de89'
RAW_SHA = 'acf510b1377a6bd96eea50577de1aa049382499335fa7e5cac9b0300ecb377c7'
GENERATED_PINS = {
    'initial.json': '2ffcd7fa9060653501873475271d48a054d063a528946714a4d23b21fb9bb162',
    'physical.json': '49aa1a8762372d62b5105341696227307b2ba4b04e930bb86aaf8064cebb6eb2',
    'all-gauge-entrances.json': '6717b795c8df73aaf6279455427834889ecdc6e872ed3e9cf8763a1c23bd29a1',
}
PHYSICAL_KEYS = ('scalar_projection_sha256','tagged_scalar_sha256',
    'weighted_scalar_events','coefficient_histogram','categories','category_names',
    'physical_registers','independent_dirty_registers','positive_rank_moves',
    'paid_histogram','used_frames')
def invariant_metadata(name, data):
    value = json.loads(data)
    if name == 'all-gauge-entrances.json':
        value = sorted(value, key=lambda q:q['role'])
    elif name == 'physical.json':
        value = {k:value[k] for k in PHYSICAL_KEYS}
        value['used_frames'] = sorted(value['used_frames'], key=lambda q:q['frame_id'])
    return value
CONNECTION_SHA = '14d13b5b4e851a66c20af1850d77a71fe21cbe3fda35c72000709f767275222e'
V, N = 1760, 20107
RAW = struct.Struct('<6i')
LINK = struct.Struct('<20i')
OP_NAMES = ('MOVE', 'ADD', 'COPY', 'ERASE')
SCHEMA = {
    'schema': 'joint259-operation-connections/1',
    'raw_columns': ['opcode', 'a', 'b', 'c', 'f', 'z'],
    'link_columns': [
        'destination', 'source', 'destination_value_before',
        'destination_value_after', 'source_value_version',
        'destination_frame_before', 'destination_frame_after',
        'source_frame', 'destination_frame_version_before',
        'destination_frame_version_after', 'source_frame_version',
        'destination_value_producer', 'source_value_producer',
        'destination_frame_producer', 'source_frame_producer',
        'copy_source', 'copy_event', 'copy_source_value_version',
        'copy_source_frame_version', 'copy_generation'],
    'record_id': 'zero-based position in pinned records.bin.gz',
    'event_id': 'local:{record_id}; a read producer >=0 names local:{producer}',
    'initial_producer': '-(register_id+2); -1 means absent, never an initial value',
    'version_convention': 'Value versions change on ADD and COPY. Frame versions change on MOVE and COPY. ERASE removes both; every scratch COPY gets a fresh generation, so versions are never reused. MOVE preserves the semantic payload version; its recursive implementation is not expanded here.',
    'links': 'Each nonabsent producer column is a producer-to-current-consumer edge. Output value/frame producer is the current event when its corresponding version changes; unchanged versions retain their producer. Consumer lists are exactly the transpose of these edges, without duplicating a massive adjacency list.',
    'MOVE': 'raw=(0,q,old_frame,new_frame,rank,0); destination=q, source=q; payload preserved; frame advances',
    'ADD': 'raw=(1,dst,src,coefficient,frame,category); read both old payloads before writing dst; src preserved; frames unchanged',
    'COPY': 'raw=(2,source,temp,source_frame,output_frame,paid_rank); destination=temp; copy unchanged source to new temporary. Global lowering expands this macro into COPY then paid MOVE.',
    'ERASE': 'raw=(3,source,temp,source_frame,output_frame,paid_rank); destination=temp, source=retained source; verify immutable source and temporary lifetime, then remove temporary',
    'address_check_scope': 'Injectivity checks distinguish syntactic full (family, route-word) keys. Algebraic rational/mod-q route nonaliasing is inherited from the separately admitted bank proof, not newly proved.',
    'scope': 'Exact finite local operation/def-use inventory plus callable global BankPlan address maps. Not a complete arbitrary-input-size compiler and not the overview graph.',
    'unexpanded': ['finite cover class enumeration', 'recursive child programs and stopping policy', 'q-local fallback implementation', 'complex supplier internals', 'all-size tape movements'],
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read_json(path):
    return json.loads(path.read_text())


def compact(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


class Inputs:
    """Read and pin static inputs; reconstruct ownership without source replay."""
    def __init__(self, package=PACKAGE, inputs=INPUT):
        self.package, self.inputs = SOURCES.open_source(package), Path(inputs)
        SOURCES.integrity(self.package, MANIFEST_SHA)
        manifest_bytes = (self.package / 'MANIFEST.json').read_bytes()
        require(sha(manifest_bytes) in (MANIFEST_SHA, SOURCES.BINDING['accepted_public_manifest_sha256']), 'selected manifest changed')
        self.manifest = json.loads(manifest_bytes)['files']
        self.pins = {'package_manifest': sha(manifest_bytes), 'scientific_archive_manifest': MANIFEST_SHA}
        self.raw = gzip.decompress(self.generated('records.bin.gz'))
        require(sha(self.raw) == RAW_SHA, 'not the admitted final local word')
        require(len(self.raw) % RAW.size == 0, 'incomplete six-int raw row')
        self.initial = {int(k): v for k, v in json.loads(self.generated('initial.json')).items()}
        self.physical = json.loads(self.generated('physical.json'))
        self.entrances = json.loads(self.generated('all-gauge-entrances.json'))
        self.dimensions = {r['frame_id']: r['dimension'] for r in self.physical['used_frames']}
        self.zero = next(f for f, d in self.dimensions.items() if d == 0)
        require(set(self.initial) == set(range(N)), 'initial register coverage')
        require(len(self.raw) // RAW.size == 859771, 'unexpected final operation count')
        self.roles, self.borrow, self.removed = self.reconstruct_roles()
        gauges = {r['role']: r['frame'] for r in self.entrances}
        require(len(gauges) == len(self.entrances) == 2827, 'entrance ownership count')
        require(all(self.initial[2*V+i] == gauges.get(r, self.zero)
                    for i, r in enumerate(self.roles)), 'role/initial-frame binding')
        families = {}
        for role in self.roles:
            rank = 24 - self.dimensions[gauges[role]] if role in gauges else 24
            families.setdefault(rank, []).append(role)
        self.static('bank_template.py')
        self.static('code/global_lowering.py')
        self.static('code/physical527.py')
        self.static('hybrid_transform.py')
        module = ModuleType('joint259_connection_bank')
        exec(compile(self.static('bank_template.py'), 'verified bank_template.py', 'exec'), module.__dict__)
        self.plan = module.BankPlan(families, gauges, self.roles)

    def generated(self, name):
        data = (self.inputs / name).read_bytes()
        if name == 'records.bin.gz':
            require(sha(gzip.decompress(data)) == RAW_SHA, 'generated raw word changed')
            self.pins['generated/records.decompressed'] = RAW_SHA
        else:
            digest = sha(compact(invariant_metadata(name, data)))
            require(digest == GENERATED_PINS[name], 'generated invariant metadata changed: ' + name)
            self.pins['generated-invariant/' + name] = digest
        return data

    def static(self, name):
        data = (self.package / name).read_bytes()
        require(name in self.manifest and sha(data) == self.manifest[name], 'source changed: ' + name)
        self.pins[name] = sha(data)
        return data

    def reconstruct_roles(self):
        base = 'loader/source_inputs/base_bit/research/paired-cube-diagonal-bit-168/selected/bit/'
        joint = 'loader/source_inputs/pr210/research/coordinated-crossover-pr200/'
        word = json.loads(gzip.decompress(self.static(base+'word_p12.json.gz')))
        profile = json.loads(self.static(base+'profile_p12.json'))
        donor = dict(json.loads(self.static(joint+'joint/pairs.json')))
        removed = {word['rootroles'][r['root']] for r in json.loads(self.static(base+'sinks.json'))}
        borrow = {}
        selections = [(joint+'borrow/selection.json', 'role'),
                      (joint+'gaugeb/selection.json', 'role'),
                      (joint+'newg/selection.json', 'role'),
                      ('source527/extra/selection.json', 'role'),
                      ('source527/fresh/selection.json', 'role'),
                      ('source527/paired-selection.json', 'aliased_role')]
        for path, key in selections:
            rows = json.loads(self.static(path))
            rows = rows['selection'] if isinstance(rows, dict) else rows
            for r in rows:
                require(r[key] not in borrow, 'duplicate source loan')
                borrow[r[key]] = r['source']
        roles = sorted({donor.get(q, q) for q in range(profile['R'])} - set(borrow) - removed)
        require(len(roles) == 16587 and len(borrow) == 527 and len(removed) == 34, 'ownership census')
        return roles, borrow, removed

    def rows(self):
        return RAW.iter_unpack(self.raw)


class Inventory:
    """O(registers) working memory; every row reads before it writes."""
    def __init__(self, initial, dimensions, categories):
        # State = [value version, frame ID, frame version, value producer, frame producer].
        self.state = {q: [0, frame, 0, -q-2, -q-2] for q, frame in initial.items()}
        self.dimensions = dimensions
        self.categories = categories
        self.counts = Counter()
        self.category_counts = Counter()
        self.coefficients = Counter()
        self.paid = Counter()
        self.copy = None
        self.generation = 0
        self.lifetimes = []
        self.link_count = 0
        self.semantic = hashlib.sha256()
        self.tagged = hashlib.sha256()

    def read(self, q, event):
        require(q in self.state, f'read-before-definition or read-after-erase: {event}:{q}')
        state = self.state[q]
        require(state[3] < event and state[4] < event, 'read is not before write')
        return state[:]

    def guard_write(self, q, event):
        require(self.copy is None or q != self.copy['source'], f'copied source mutated in lifetime: {event}:{q}')

    def step(self, event, row):
        op, a, b, c, f, z = row
        require(op in range(4), 'unknown opcode')
        self.counts[OP_NAMES[op]] += 1
        dst, src = (b, a) if op in (2, 3) else (a, b) if op == 1 else (a, a)
        old = None if op == 2 else self.read(dst, event)
        source = self.read(src, event)
        copy = self.copy
        if op == 0:
            self.guard_write(dst, event)
            require(old[1] == b and c in self.dimensions, 'MOVE before/after frame')
            require(f == self.dimensions[c]-self.dimensions[b] and f >= 0, 'MOVE rank')
            require(z == 0, 'MOVE reserved field')
            new = [old[0], c, old[2]+1, old[3], event]
            self.state[dst] = new
            if f:
                self.paid[f] += 1
        elif op == 1:
            self.guard_write(dst, event)
            require(dst != src and dst != N, 'ADD operands alias or overwrite work')
            require(old[1] == source[1] == f, 'ADD required frames')
            require(0 <= z < len(self.categories), 'ADD category')
            category = self.categories[z]
            require((src == N) == (category == 'center'), 'center/scratch binding')
            if src == N:
                require(copy is not None, 'scratch read without COPY')
                require(self.state[copy['source']] == copy['snapshot'], 'copy source changed')
                copy['reads'] += 1
            new = [old[0]+1, old[1], old[2], event, old[4]]
            self.state[dst] = new
            self.category_counts[category] += 1
            self.coefficients[abs(c)] += 1
            logical_source = copy['source'] if src == N else src
            self.semantic.update(json.dumps([a, logical_source, c], separators=(',', ':')).encode()+b'\n')
            self.tagged.update(json.dumps([a, b, c, f, category], separators=(',', ':')).encode()+b'\n')
        elif op == 2:
            require(self.copy is None and dst == N and dst not in self.state, 'COPY while temporary live')
            require(src != N and source[1] == c, 'COPY source/frame')
            require(self.dimensions[c] == z == 22 and self.dimensions[f] == 0, 'COPY rank/output frame')
            self.generation += 1
            new = [self.generation, f, self.generation, event, event]
            self.state[dst] = new
            self.copy = copy = dict(source=src, temporary=dst, copy_event=event,
                snapshot=source[:], generation=self.generation, reads=0)
            self.paid[z] += 1
        else:
            require(copy is not None and dst == N and src == copy['source'], 'ERASE lifetime/source')
            require(source == copy['snapshot'] and source[1] == c and old[1] == f, 'ERASE immutable source/frame')
            require(copy['reads'] == 220 and z == 22, 'ERASE scatter coverage')
            new = None
            self.lifetimes.append(dict(copy_event=copy['copy_event'], erase_event=event,
                source=src, source_value_version=source[0], source_frame_version=source[2],
                source_value_producer=source[3], source_frame_producer=source[4],
                temporary=dst, generation=copy['generation'], reads=copy['reads'], immutable=True))
            del self.state[dst]
            self.copy = None
        before = old if old is not None else [-1]*5
        after = new if new is not None else [-1]*5
        edge = (dst, src, before[0], after[0], source[0], before[1], after[1], source[1],
                before[2], after[2], source[2], before[3], source[3], before[4], source[4],
                copy['source'] if copy else -1, copy['copy_event'] if copy else -1,
                copy['snapshot'][0] if copy else -1, copy['snapshot'][2] if copy else -1,
                copy['generation'] if copy else -1)
        self.link_count += sum(p != -1 for p in edge[11:15])
        return edge

    def finish(self):
        require(self.copy is None and N not in self.state, 'unclosed COPY')
        return dict(opcode_counts=dict(self.counts), categories=dict(self.category_counts),
            coefficient_histogram=dict(self.coefficients), paid_histogram=dict(sorted(self.paid.items())),
            producer_consumer_links=self.link_count, copied_source_lifetimes=self.lifetimes,
            scalar_projection_sha256=self.semantic.hexdigest(), tagged_scalar_sha256=self.tagged.hexdigest(),
            final_state_sha256=sha(compact(self.state)), final_live_registers=len(self.state))


def validate_inventory(inputs, inventory, count, links):
    summary = inventory.finish()
    summary.update(events=count, link_bytes_sha256=links.hexdigest(), link_record_bytes=LINK.size)
    require(count == 859771 and links.hexdigest() == CONNECTION_SHA, 'complete inventory count/digest')
    for key in ('scalar_projection_sha256', 'tagged_scalar_sha256'):
        require(summary[key] == inputs.physical[key], key+' metadata mismatch')
    require(summary['opcode_counts'] == {'MOVE':99340,'ADD':760383,'COPY':24,'ERASE':24}, 'opcode census')
    require(summary['paid_histogram'] == {int(k):v for k,v in inputs.physical['paid_histogram'].items()}, 'paid census')
    require(summary['categories'] == inputs.physical['categories'], 'category census')
    return summary


def write_inventory(inputs, output):
    """Write complete plain JSONL to a binary stream, suitable for gzip wrapping."""
    output.write(compact(dict(kind='metadata', **SCHEMA, source_pins=inputs.pins, raw_sha256=RAW_SHA))+b'\n')
    inventory = Inventory(inputs.initial, inputs.dimensions, inputs.physical['category_names'])
    links = hashlib.sha256()
    count = 0
    for event, row in enumerate(inputs.rows()):
        edge = inventory.step(event, row)
        links.update(LINK.pack(*edge))
        output.write(compact(dict(event_id=event, raw=row, connections=edge))+b'\n')
        count += 1
    summary = validate_inventory(inputs, inventory, count, links)
    output.write(compact(dict(kind='validation', **summary))+b'\n')
    return summary


def scan(inputs, start=0, stop=None, capture=False):
    inventory = Inventory(inputs.initial, inputs.dimensions, inputs.physical['category_names'])
    links = hashlib.sha256()
    compressed = io.BytesIO()
    encoder = zlib.compressobj(level=9)
    count = 0
    for event, row in enumerate(inputs.rows()):
        if stop is not None and event >= stop:
            break
        edge = inventory.step(event, row)
        packed = LINK.pack(*edge)
        links.update(packed)
        count += 1
        if capture and event >= start:
            compressed.write(encoder.compress(packed))
    if capture:
        compressed.write(encoder.flush())
    summary = validate_inventory(inputs, inventory, count, links) if stop is None else {'partial_prefix_events': count}
    summary.update(events=count, link_bytes_sha256=links.hexdigest(), link_record_bytes=LINK.size)
    if stop is None:
        for key in ('scalar_projection_sha256', 'tagged_scalar_sha256'):
            require(summary[key] == inputs.physical[key], key+' metadata mismatch')
        require(summary['opcode_counts'] == {'MOVE': 99340, 'ADD': 760383, 'COPY': 24, 'ERASE': 24}, 'opcode census')
        require(summary['paid_histogram'] == {int(k):v for k,v in inputs.physical['paid_histogram'].items()}, 'paid census')
        require(summary['categories'] == inputs.physical['categories'], 'category census')
    return summary, compressed.getvalue()


def iter_stage_rows(inputs, stage):
    """Exact eight-field logical lowering, retaining local-record provenance."""
    require(0 <= stage < 5, 'stage out of range')
    reverse = stage in (1, 3)
    offsets = range(len(inputs.raw)-RAW.size, -1, -RAW.size) if reverse else range(0, len(inputs.raw), RAW.size)
    plan = inputs.plan
    def family(local):
        return 4*V+len(inputs.roles) if local == N else (
            plan.active[stage][0]*V+local if local < V else
            plan.active[stage][1]*V+local-V if local < 2*V else 4*V+local-2*V)
    for offset in offsets:
        op, a, b, c, f, z = RAW.unpack_from(inputs.raw, offset)
        common = (stage, int(reverse))
        if op == 0:
            yield offset//RAW.size, (0, family(a), c if reverse else b, b if reverse else c, f, 0, *common)
        elif op == 1:
            yield offset//RAW.size, (1, family(a), family(b), -c if reverse else c, f, z, *common)
        elif op == (3 if reverse else 2):
            yield offset//RAW.size, (2, family(b), family(a), 0, c, 0, *common)
            yield offset//RAW.size, (0, family(b), c, f, z, 0, *common)
        else:
            yield offset//RAW.size, (3, family(b), -1, 0, f, 0, *common)


def iter_global_connections(inputs, stage, replica, cover='d'):
    """Call for any of 200 stage/replica pairs; d stays an exact formal key."""
    for local_event, row in iter_stage_rows(inputs, stage):
        yield local_event, inputs.plan.map_stage_row(stage, replica, row, cover)


def iter_saved_connections(root=ROOT):
    """Decode the persisted inventory and verify every shard and the full digest."""
    inputs = Inputs()
    manifest = read_json(Path(root)/'JOINT259_CONNECTION_EVENTS_MANIFEST.json')
    require(manifest['raw_sha256'] == RAW_SHA, 'inventory raw binding')
    require(manifest['link_bytes_sha256'] == CONNECTION_SHA, 'inventory expected connection digest')
    digest = hashlib.sha256()
    cursor = 0
    for shard in manifest['shards']:
        require(shard['start'] == cursor, 'inventory gap or overlap')
        encoded = (Path(root)/shard['file']).read_bytes()
        require(sha(encoded) == shard['file_sha256'], 'inventory shard changed')
        data = zlib.decompress(base64.b64decode(encoded, validate=False))
        require(len(data) == (shard['stop']-shard['start'])*LINK.size, 'inventory shard length')
        digest.update(data)
        for edge in LINK.iter_unpack(data):
            yield cursor, RAW.unpack_from(inputs.raw, cursor*RAW.size), edge
            cursor += 1
    require(cursor == 859771, 'incomplete persisted inventory')
    require(digest.hexdigest() == manifest['link_bytes_sha256'], 'inventory full digest')


def address_map(inputs, exhaustive=False):
    plan = inputs.plan
    result = dict(schema='joint259-parametric-bank-map/1',
        source_sha256=inputs.pins['bank_template.py'], stages=5, replicas=40,
        active_data_banks=plan.active, helper_roles=inputs.roles,
        residual_rank_families=plan.families, gauge_frames=plan.gauge_frames,
        patterns=plan.patterns, segments=plan.segments,
        helper_occurrences=5*40*len(inputs.roles),
        local_registers=N, external_work_local=N, external_work_family=plan.work_family,
        data_families=plan.data_families, banks_per_stage=plan.banks_per_stage,
        live_families=plan.live_families,
        assignment='q=role_index*40+replica; select residual-rank segment [lo,hi); (bank_offset,within)=divmod(q-lo,len(blocks)); family=281600+117089*stage+bank_start+bank_offset; block=blocks[within]; offset=sum(pattern widths before block)',
        data_route='stage0:(family,class(d)); stage>0:(family,right(d,rho(stage,port)))',
        helper_route='(family,right(d,tau(stage),inverse(normalizer(stage,pattern,block,frame))))',
        normalizer='scalar=(block+1); exact permutation from stage window residual coordinates to block; inverse chart identified by source-bound gauge frame. Apply factors right-to-left. Cover arithmetic is not reduced modulo 2.',
        phase_schedule=list(plan.phase_schedule()),
        completion='No COMPLETE emitted by bank mapper. Discharged by separately admitted bank endpoint theorem; not newly proved by this extractor.',
        boundary_methods='BankPlan.map_boundary_row handles IDLE(4), BRIDGE(5), EXCHANGE(7); rejects COMPLETE(6).',
        callable='Inputs.plan.local_address(stage,replica,local,cover); iter_global_connections(inputs,stage,replica,cover)')
    if exhaustive:
        digest = hashlib.sha256()
        assignments = 0
        for stage in range(5):
            for replica in range(40):
                addresses = [plan.local_address(stage, replica, local) for local in range(N+1)]
                require(len(set(addresses)) == N+1, 'full address collision')
                require(addresses[-1] == (plan.work_family, ('external_work',0)), 'work address')
                digest.update(compact(addresses))
                assignments += len(addresses)
        result['fresh_full_address_checks'] = dict(namespaces=200, addresses=assignments,
            address_digest_sha256=digest.hexdigest(), all_full_keys_injective=True,
            check_scope='Distinct syntactic (family, route-word) keys; algebraic route nonaliasing inherited, not re-proved.')
    return result


def validate_output_path(path, package):
    path=Path(path)
    require(not path.exists() and not path.is_symlink(), 'output must be a new file')
    resolved=path.resolve();package_path=Path(package)
    if package_path.is_dir():
        require(not resolved.is_relative_to(package_path.resolve()), 'output must be outside source package')
    return resolved


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', type=Path, default=PACKAGE, help='admitted original/public source directory or ZIP')
    parser.add_argument('--inputs', type=Path, default=INPUT, help='fresh final hybrid directory from verifier OUTPUT/hybrid')
    parser.add_argument('--summary', action='store_true')
    parser.add_argument('--map', action='store_true')
    parser.add_argument('--check-addresses', action='store_true')
    parser.add_argument('--schema', action='store_true')
    parser.add_argument('--chunk', nargs=2, type=int, metavar=('START','STOP'))
    parser.add_argument('--inventory', type=Path, help='write complete gzip JSONL inventory, metadata first')
    args = parser.parse_args()
    if args.schema:
        print(json.dumps(SCHEMA, indent=2)); return
    inputs = Inputs(args.package, args.inputs)
    if args.chunk:
        start, stop = args.chunk
        require(0 <= start < stop <= len(inputs.raw)//RAW.size, 'chunk range')
        _, data = scan(inputs, start, stop, capture=True)
        print(base64.b64encode(data).decode()); return
    if args.map:
        print(json.dumps(address_map(inputs, args.check_addresses), indent=2)); return
    if args.inventory:
        destination=validate_output_path(args.inventory,args.package)
        with destination.open('xb') as raw_output:
            with gzip.GzipFile(fileobj=raw_output, mode='wb', mtime=0) as output:
                write_inventory(inputs, output)
        print(json.dumps({'inventory':str(args.inventory), 'sha256':sha(args.inventory.read_bytes())})); return
    summary, _ = scan(inputs)
    summary.update(schema=SCHEMA['schema'], scope=SCHEMA['scope'], source_pins=inputs.pins,
                   raw_sha256=RAW_SHA, raw_records=len(inputs.raw)//RAW.size,
                   address_map=address_map(inputs, args.check_addresses) if args.check_addresses else {
                       'exact_parametric':True, 'scope':'Syntactic full address keys; algebraic route nonaliasing inherited.', 'stage_replica_pairs':200,
                       'helper_occurrences':3317400, 'live_families':867045})
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
