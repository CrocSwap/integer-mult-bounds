import pathlib,json,subprocess,hashlib
P=pathlib.Path('/tmp/pr-efficient1800');D=P/'combined-2505';R='/tmp/integer-mult-efficient1100-20261015';py='/tmp/pr-efficient200-venv/bin/python'
actual=json.loads(subprocess.check_output([py,'-B','scripts/research_package.py','--changed-since','0','--matrix-batch-size','256'],cwd=D))
expected=sorted(x[:-12] for x in subprocess.check_output(['git','ls-tree','-r','--name-only','HEAD'],cwd=R,text=True).splitlines() if x.startswith('research/') and x.endswith('/VERIFY.json') and len(pathlib.PurePosixPath(x).parts)==3)
# Remove the exact slash plus VERIFY.json suffix, without assuming its length.
expected=sorted(str(pathlib.PurePosixPath(x).parent) for x in subprocess.check_output(['git','ls-tree','-r','--name-only','HEAD'],cwd=R,text=True).splitlines() if x.startswith('research/') and x.endswith('/VERIFY.json') and len(pathlib.PurePosixPath(x).parts)==3)
flat=[p for row in actual['include'] for p in row['packages']];assert flat==expected and len(flat)==len(set(flat));sizes=[len(row['packages']) for row in actual['include']];assert sizes==[256,256,256,195],sizes
old=subprocess.check_output(['git','show','HEAD:.github/workflows/research-packages.yml'],cwd=R,text=True);new=(D/'.github/workflows/research-package-batch.yml').read_text()
assert old[old.index('    steps:',old.index('  replay:')):]==new[new.index('    steps:'):]
assert 'max-parallel: 4' in new and 'timeout-minutes: 30' in new and 'contents: read' in new
record=dict(status='PASS',packages=len(flat),batches=sizes,complete_ordered_coverage=True,original_replay_steps_byte_identical=True,matrix_utf16_bytes=len(json.dumps(actual).encode('utf-16-le')),main=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),docs=['https://docs.github.com/en/actions/reference/limits','https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows'],scope='Full current tracked registry and actual grouped CLI; exact original replay steps preserved. Local proof of complete selection, not hosted GitHub workflow execution or all-package scientific replay.')
(P/'provenance-2505.json').write_text(json.dumps(record,indent=2)+'\n');print('PASS_MATRIX_COVERAGE',json.dumps(record))
