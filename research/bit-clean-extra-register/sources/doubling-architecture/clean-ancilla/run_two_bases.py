"""Run all basis alphabets with three independent worker processes."""
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from pathlib import Path
import subprocess
import time


folder = Path(__file__).resolve().parent
result_folder = folder/'all-basis-results'


def run(index):
    out = result_folder/f'{index:03d}.json'
    log = result_folder/f'{index:03d}.log'
    with log.open('w') as stream:
        subprocess.run([str(folder/'two_bases'), str(folder/'ALPHABETS.txt'),
                        str(index), str(out)], check=True, stderr=stream)
    return json.loads(out.read_text())


if __name__ == '__main__':
    result_folder.mkdir(exist_ok=True)
    count = len((folder/'ALPHABETS.txt').read_text().splitlines())
    start = time.monotonic()
    results = []
    with ThreadPoolExecutor(max_workers=3) as executor:
        jobs = [executor.submit(run, index) for index in range(count)]
        for future in as_completed(jobs):
            result = future.result()
            results.append(result)
            summary = dict(alphabets=count, completed=len(results),
                           searched_words=sum(r['searched_words'] for r in results),
                           states=[sum(r['states'][k] for r in results) for k in range(4)],
                           terminals=sum(r['terminals'] for r in results),
                           robust=sum(r['robust'] for r in results),
                           seconds=time.monotonic()-start,
                           results=sorted(results, key=lambda r:r['basis']))
            (folder/'ALL-BASIS-SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n')
            print(json.dumps({k:v for k,v in summary.items() if k!='results'}),flush=True)
