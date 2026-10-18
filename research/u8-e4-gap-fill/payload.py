"""Run PR942 payload boundary controls against this construction's receipts.

Only the geometry status, nominated kappa, and source-root locator change.
Prepared with OpenAI Codex assistance; Apache-2.0.
"""
import argparse
import subprocess
import sys
from pathlib import Path
from support import P, ROOT, T37, dump, read, require, sha


def adaptation():
    source = T37 / 'independent/check_payload_controls.py'
    changes = [
        ('ROOT=HERE.parents[2]', 'ROOT=Path(' + repr(str(ROOT)) + ')'),
        ("geometry['status']=='PASS_INDEPENDENT_VARIABLE_T_LITERAL_WINDOWS_CHARTS_PREFIX_ROW'",
         "geometry['status']=='PASS_INDEPENDENT_MIXED_E4_T37_WINDOWS_CHARTS_PREFIX_ROW'"),
        ("baseline['kappa_decimal']=='0.001661960547713947'",
         "baseline['kappa_decimal']==" + repr(read(P / 'CLAIM.json')['kappa_decimal']))]
    text = source.read_text()
    for before, after in changes:
        require(text.count(before) == 1, 'Payload adaptation anchor')
        text = text.replace(before, after)
    return text, changes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work', type=Path, required=True)
    args = parser.parse_args()
    text, changes = adaptation()
    path = args.work / 'payload_controls_adapter.py'
    path.write_text(text, encoding='utf-8')
    subprocess.run([sys.executable, '-B', str(path), '--work', str(args.work),
                    '--out', str(args.work / 'PAYLOAD-CONTROLS.json')], check=True, cwd=ROOT)
    dump(args.work / 'PAYLOAD-ADAPTATION.json', dict(
        source_sha256=sha(T37 / 'independent/check_payload_controls.py'),
        generated_sha256=sha(path), changes=changes))


if __name__ == '__main__':
    main()
