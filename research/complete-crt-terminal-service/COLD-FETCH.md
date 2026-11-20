# Exact public-source cold acquisition

The package already includes and authenticates its 22-file executable
closure, so its scientific replay needs no Git or network access. To
independently verify the copied bytes against public Git objects, use an
empty auxiliary repository and fetch only the exact public joined head:

```sh
git init /tmp/crt-terminal-source-pins
git -C /tmp/crt-terminal-source-pins remote add source https://github.com/CubeJerry/integer-mult-bounds.git
git -C /tmp/crt-terminal-source-pins -c protocol.version=2 fetch --filter=blob:none --no-tags --depth=1 source 7a6334dceef9d03fb5b1aeec4269a2911c0112b4
```

Then, from the checkout containing this new package, retrieve and verify
only the paths listed in SOURCE-PINS.json:

```sh
python3 - <<'PY'
import hashlib, json, pathlib, subprocess
root = pathlib.Path.cwd()
package = root / 'research/complete-crt-terminal-service'
rows = json.loads((package / 'SOURCE-PINS.json').read_text())['files']
for row in rows:
    revision = row['origin_commit'] + ':' + row['origin_path']
    data = subprocess.check_output([
        'git', '-C', '/tmp/crt-terminal-source-pins', 'show', revision
    ])
    assert hashlib.sha256(data).hexdigest() == row['sha256']
    assert hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest() == row['git_blob']
    assert data == (root / row['path']).read_bytes()
print('PASS_COLD_EXACT_CRT_TERMINAL_SOURCE_PINS', len(rows))
PY
```

Git may acquire the individually requested blobs on demand. No recursive
archive, full checkout or million-state generated graph is needed.
The public joined source retains the earlier exact arithmetic and lifecycle
pins and their original notices. The original numerical graph head is
ee6005fe241ab947e511fe9f6d86f5f4fa58478b, and the lifecycle head is
39c309f1aa72af12669d37ae055da0ece1ae0e7d.

After those checks, the replay is:

```sh
python3 -B scripts/research_package.py --package research/complete-crt-terminal-service
```

The new package's publication commit is supplied by its PR. The source
commands above intentionally pin the already-public predecessor and do not
substitute an unmaintained fork's main branch for the canonical base.
