"""Download only hash-pinned public data; no upstream program is executed."""
import argparse
from pathlib import Path
import urllib.request

from source_data import MANIFEST, verify_bytes


def fetch(destination):
    destination = Path(destination).expanduser().resolve()
    prefix = ('https://raw.githubusercontent.com/' + MANIFEST['repository'] + '/'
              + MANIFEST['commit'] + '/' + MANIFEST['package'] + '/')
    for name, pin in MANIFEST['files'].items():
        target = destination / name
        if target.exists():
            verify_bytes(name, target.read_bytes())
            print('Verified existing ' + name)
            continue
        with urllib.request.urlopen(prefix + name, timeout=60) as response:
            data = response.read(pin['bytes'] + 1)
        verify_bytes(name, data)
        target.parent.mkdir(parents=True, exist_ok=True)
        # Exclusive creation avoids replacing a file written during download.
        with target.open('xb') as output:
            output.write(data)
        print('Verified downloaded ' + name)
    return destination


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--destination', type=Path, required=True)
    args = parser.parse_args()
    print('Input directory: ' + str(fetch(args.destination)))
