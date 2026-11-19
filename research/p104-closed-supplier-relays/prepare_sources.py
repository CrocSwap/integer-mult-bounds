"""Fetch or verify the immutable inputs for the P104 closed-supplier replay."""

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
from tempfile import NamedTemporaryFile
from time import sleep
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


HERE = Path(__file__).resolve().parent


def verify(data, pin, label):
    blob_header = b"blob " + str(len(data)).encode() + b"\0"
    if (hashlib.sha256(data).hexdigest() != pin["sha256"]
            or hashlib.sha1(blob_header + data).hexdigest() != pin["blob"]):
        raise ValueError(f"source digest mismatch for {label}")


def materialize(job):
    path, url, pin, fetch = job
    if path.exists():
        verify(path.read_bytes(), pin, path)
        return
    if not fetch:
        raise FileNotFoundError(path)
    for attempt in range(3):
        try:
            with urlopen(Request(url, headers={"User-Agent": "P104-source-replay"}), timeout=45) as response:
                data = response.read()
            break
        except (HTTPError, URLError, TimeoutError) as exc:
            if attempt == 2 or isinstance(exc, HTTPError) and exc.code not in (429, 500, 502, 503, 504):
                raise
            sleep(2 ** attempt)
    verify(data, pin, url)
    path.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(dir=path.parent, delete=False) as temporary:
        temporary.write(data)
        name = Path(temporary.name)
    try:
        name.replace(path)
    finally:
        name.unlink(missing_ok=True)


def sources(cache, fetch=False):
    manifest = json.loads((HERE / "SOURCE-LOCK.json").read_bytes())
    jobs = []
    for label, source in manifest["sources"].items():
        prefix = f"https://raw.githubusercontent.com/{source['repository']}/{source['commit']}"
        for filename, pin in source["files"].items():
            remote_name = "/".join(filter(None, (source["path"], filename)))
            jobs.append((cache / label / filename, prefix + "/" + quote(remote_name), pin, fetch))
    with ThreadPoolExecutor(max_workers=4) as pool:
        for _ in pool.map(materialize, jobs):
            pass
    return len(jobs)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cache", type=Path)
    parser.add_argument("--fetch", action="store_true", help="download missing files from the pinned public commits")
    args = parser.parse_args()
    print(f"Verified {sources(args.cache, args.fetch)} source files.")
