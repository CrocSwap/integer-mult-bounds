"""Download immutable upstream data only; never execute upstream programs."""
from pathlib import Path
import argparse,json,urllib.request
from source_data import ROOT,pins,validate,HEAD

def run(destination):
    destination=Path(destination).resolve();destination.mkdir(parents=True,exist_ok=True)
    manifest=pins()
    for name,row in manifest['files'].items():
        target=destination/row['local']
        assert destination in target.resolve().parents
        url=row['url'];commit=row.get('commit',HEAD)
        assert url.startswith('https://raw.githubusercontent.com/') and '/'+commit+'/' in url
        if target.exists():raw=target.read_bytes()
        else:
            with urllib.request.urlopen(url,timeout=90) as response:raw=response.read()
        validate(name,raw);target.parent.mkdir(parents=True,exist_ok=True)
        if not target.exists():target.write_bytes(raw)
    return dict(status='PASS_ALL_IMMUTABLE_INPUT_HASHES',files=len(manifest['files']),bytes=sum(z['bytes']for z in manifest['files'].values()),destination=str(destination),upstream_programs_executed=False)
if __name__=='__main__':
    if not __debug__:raise RuntimeError('Assertions required')
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=ROOT/'inputs')
    print(json.dumps(run(parser.parse_args().output),indent=2))
