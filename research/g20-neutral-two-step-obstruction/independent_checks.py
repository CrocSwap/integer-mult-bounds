"""Run separately authored geometry, distance, sign and interface checks.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
"""
from pathlib import Path
import gzip
import json
import subprocess
import sys

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def main():
    source = ROOT / 'research/g20-conjugation-admission'
    archive = ROOT / 'research/bit-g20-contact-expansion-bound/FRAMES.json.gz'
    current = source / 'prior/prior/prior/source/vendor/g20/inputs/FRAMES.json'
    certificate = json.loads(gzip.decompress((PACKAGE / 'NATIVE-CERTIFICATE.json.gz').read_bytes()))
    checks = [
        ('review_geometry.py', ['--current', str(current), '--older', str(archive),
                                '--paths', str(source / 'PATHS.json')], 40),
        ('review_distances.py', ['--frames', str(current)], 45),
        ('review_partitions.py', ['--certificate', str(PACKAGE / 'NATIVE-CERTIFICATE.json.gz')], 10),
        ('review_partitions.py', ['--certificate', str(PACKAGE / 'NATIVE-ONE-STEP.json.gz')], 10),
        ('crosscheck_prefix.py', [], 30),
        ('review_two_step_domain.py', ['--word', str(source / 'WORD.json.gz'),
                                     '--one-step', str(PACKAGE / 'NATIVE-ONE-STEP.json.gz'),
                                     '--two-step', str(PACKAGE / 'NATIVE-CERTIFICATE.json.gz')], 30),
    ]
    for filename, arguments, timeout in checks:
        for optimized in (False, True):
            command = [sys.executable, '-I', '-W', 'error', '-B']
            if optimized:
                command.append('-O')
            result = subprocess.run(command + [str(PACKAGE / filename)] + arguments,
                                    cwd=ROOT, check=True, capture_output=True, text=True, timeout=timeout)
            if filename == 'review_distances.py':
                receipt = json.loads(result.stdout)
                if receipt['author_keyed_encoding_sha256'] != certificate['graph']['metric_sha256']:
                    raise ValueError('independent complete metric differs from primary')
            print(result.stdout, end='', flush=True)
    print('PASS_G20_INDEPENDENT_CHECKS geometry_distance_partition_prefix_domain_normal_optimized')


if __name__ == '__main__':
    main()
