"""Compile the fixed directory, initialize a fresh receiver and verify their tape clocks."""

import json
import subprocess
import sys
import tarfile
from argparse import ArgumentParser
from hashlib import sha256
from importlib.metadata import version
from io import BytesIO
from pathlib import Path

from bounded_wasi import FileService
from guest_opcodes import census
from module_census import catalogue
from record_census import inspect
from verify_receipt import local_time_bound, time_bound
from wasmtime import Config, Engine, Linker, Module, Store, _bindings

HERE = Path(__file__).resolve().parent
WASM = "e5dc5a398b07b54ea8fdb503bf68fb583d533f10ec3f930963e02b9505f7a763"
ARCHIVE = "6c1cddbb69ae09e87eee2906bdc70539bff5f2969818a6f8457d4e6a6eb67d4d"
LIB_FILES = {
    "lib/python312.zip": "74130c400ba5b818bf58bfc2f41fc075f4350cbb13e53099c84e9c0494ec5444",
    "lib/python3.12/os.py": "e36b0a6d4feefa0ec1f15b84abd87f61da6f5db434586467869ff0e5f5e1dc24",
    "lib/python3.12/lib-dynload/.empty": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
}
SOURCE_IMAGE = "594661d65b3022ba679c29b193800813ed0c41d8f3a8c691e46a7a20ea38229f"
DIRECTORY = "045c482b6d32fc58bae8e047e22d519f9269e0124fe3cb1695e930e4f472f2a8"


def verified(data, digest):
    if sha256(data).hexdigest() != digest:
        raise ValueError("input digest differs")
    return data


def signature(files):
    return sha256(
        b"".join(
            k.encode() + b"\0" + sha256(v).digest() for k, v in sorted(files.items())
        )
    ).hexdigest()


def library(path):
    data = verified(path.read_bytes(), ARCHIVE)
    with tarfile.open(fileobj=BytesIO(data), mode="r:gz") as archive:
        return {
            "/" + k: verified(archive.extractfile("usr/local/" + k).read(), pin)
            for k, pin in LIB_FILES.items()
        }


def sources(repository):
    parent = repository / "research/tiered-native-multiplier"
    manifest = verified(
        (parent / "SOURCES.json").read_bytes(),
        "7a10012734132909e99b0c6160d68d0b8647e1607d25679efb1f5315cf8e23de",
    )
    rows = {"/sources/SOURCES.json": manifest}
    for name in json.loads(manifest)["archive_and_overlay_sha256"]:
        rows["/sources/" + name] = (parent / name).read_bytes()
    weighted = repository / "research/frequency-weighted-native-multiplier"
    spec = json.loads((weighted / "SOURCES.json").read_bytes())
    subset = {
        key: spec[key] for key in ("predecessor", "local_sources", "runtime_images")
    }
    contract = json.dumps(subset, sort_keys=True, separators=(",", ":")).encode()
    rows["/weighted/SOURCES.json"] = verified(
        contract, "2b6dbd7a48dae6b7894a08ddca10eb988147e53fc35e91603c45cc26588a535f"
    )
    for name in spec["local_sources"]:
        rows["/weighted/" + name] = (weighted / name).read_bytes()
    return rows


def flight(engine, module, lib, inputs, entry, modules):
    argv = [
        "python",
        "-B",
        "-S",
        "-c",
        f'import sys;sys.path.insert(0,"/compiler");import {entry};{entry}.run()',
    ]
    service = FileService(argv, ["PYTHONHOME=/", "TMPDIR=/tmp", "PYTHONHASHSEED=0"])
    seeds = {
        **lib,
        **inputs,
        **{"/compiler/" + name: (HERE / name).read_bytes() for name in modules},
    }
    for path, body in sorted(seeds.items()):
        service.create(path, bytearray(body))
    store = Store(engine)
    store.set_limits(
        memory_size=2**30, table_elements=2**20, instances=2, memories=2, tables=2
    )
    fuel = 2**42
    store.set_fuel(fuel)
    linker = Linker(engine)
    for interface in module.imports:
        assert interface.module == "wasi_snapshot_preview1"
        linker.define_func(
            interface.module,
            interface.name,
            interface.type,
            service.handler(interface.name),
            access_caller=True,
        )
    instance = linker.instantiate(store, module)
    try:
        instance.exports(store)["_start"](store)
    except Exception as error:
        if str(error) != "WASI exit 0":
            print(service.files["/stderr"].decode(errors="replace"), file=sys.stderr)
            raise
    receipt = {
        "fuel": fuel - store.get_fuel(),
        "linear_bytes": instance.exports(store)["memory"].data_len(store),
        "host_calls": sum(service.calls.values()),
        "operations": dict(service.calls),
        "maxima": dict(service.maximum),
        "transferred": service.bytecount,
        "source_seed_bytes": sum(map(len, seeds.values())),
        "result": service.files["/stdout"].decode().strip(),
    }
    return service, receipt


def machine_files(service):
    return {
        k.removeprefix("/machine/"): bytes(v)
        for k, v in service.files.items()
        if k.startswith("/machine/") and v is not None
    }


def write_tree(destination, files):
    for name, data in files.items():
        path = destination / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)


def main():
    cli = ArgumentParser(description=__doc__)
    cli.add_argument("--wasm", required=True, type=Path)
    cli.add_argument("--archive", required=True, type=Path)
    cli.add_argument("--work", required=True, type=Path)
    cli.add_argument("--repository", type=Path, default=HERE.parents[2])
    args = cli.parse_args()
    if sys.flags.optimize:
        raise ValueError("run with assertions enabled")
    if version("wasmtime") != "38.0.0":
        raise ValueError("wasmtime 38.0.0 is required")
    root = args.repository.resolve()
    work = args.work.resolve()
    work.mkdir(exist_ok=True, parents=True)
    if any(work.iterdir()):
        raise ValueError("use an empty replay directory")
    blob = verified(args.wasm.read_bytes(), WASM)
    lib = library(args.archive)
    code = catalogue(blob)
    operators, depth, free = census(blob)
    assert free == 274
    assert (
        depth,
        code["max_locals"],
        code["max_params"],
        code["max_results"],
        code["max_body_bytes"],
    ) == (284, 187, 18, 1, 106184)
    assert len(operators) > 100 and all(len(op) == 2 for op in operators)
    cfg = Config()
    cfg.consume_fuel = True
    cfg.strategy = "cranelift"
    _bindings.wasmtime_config_cranelift_nan_canonicalization_set(cfg.ptr(), True)
    eng = Engine(cfg)
    module = Module(eng, blob)
    common = ("compiler_state.py", "tape_directory.py")
    service, producer = flight(
        eng,
        module,
        lib,
        sources(root),
        "producer",
        (*common, "source_image.py", "producer.py"),
    )
    raw = bytes(service.files["/tmp/compiled.dag"])
    verified(raw, DIRECTORY)
    compiled = machine_files(service)
    assert signature(compiled) == SOURCE_IMAGE and len(compiled) == 106
    del service
    dag = work / "installed-native.dag"
    dag.write_bytes(raw)
    c = inspect(dag)
    assert (
        c["largest_key_bytes"] <= 28
        and c["largest_integer_bits"] < 4096
        and c["edges"] < 2**23
        and c["bytes"] < 2**26
    )
    seeds = {"/machine/" + k: v for k, v in compiled.items()}
    seeds["/machine/installed-native.dag"] = raw
    service, consumer = flight(
        eng,
        module,
        lib,
        seeds,
        "consumer",
        (*common, "fixed_directory.py", "consumer.py"),
    )
    linked = machine_files(service)
    del service
    assert len(linked) == 110
    write_tree(work / "machine", linked)
    assert (
        signature(linked)
        == "3b4c1c8ae6b15cf97c49f801f3b0059da0eaefb2db2aae79d52957e651eaee30"
    )
    full_store = time_bound(producer, code, depth) + time_bound(consumer, code, depth)
    bound = local_time_bound(producer, code, depth, free) + local_time_bound(
        consumer, code, depth, free
    )
    assert bound < 2**113 and full_store < 2**142
    evidence = {
        "installer": producer,
        "receiver": consumer,
        "opcodes": sum(operators.values()),
        "module": code,
        "max_depth": depth,
        "max_free_segment": free,
        "directory": c,
        "directory_sha256": DIRECTORY,
        "compiled_sha256": signature(compiled),
        "linked_sha256": signature(linked),
        "compiled_files": len(compiled),
        "compiled_bytes": sum(map(len, compiled.values())),
        "linked_files": len(linked),
        "linked_bytes": sum(map(len, linked.values())),
        "transition_bound": str(bound),
        "exponent": 146,
        "full_store_bound": str(full_store),
        "full_store_trace_exponent": full_store.bit_length(),
        "trace_exponent": bound.bit_length(),
    }
    (work / "clock.json").write_text(
        json.dumps(evidence, sort_keys=True, indent=2) + "\n"
    )
    print(
        f"fixed setup < 2^{bound.bit_length()} transitions on this trace; receipts at",
        work / "clock.json",
        flush=True,
    )
    result = subprocess.run(
        [sys.executable, "-B", str(HERE / "signed.py"), str(work / "machine")],
        check=True,
        capture_output=True,
        text=True,
    )
    (work / "signed.json").write_text(result.stdout)
    print(result.stdout, flush=True)


if __name__ == "__main__":
    main()
