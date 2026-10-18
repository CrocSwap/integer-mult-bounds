"""Benign stale-value regressions and source-bound consumer export controls."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import py_compile
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location('child_replay', HERE/'replay.py')
R = importlib.util.module_from_spec(spec)
spec.loader.exec_module(R)
CURRENT, OLD = 2147483647, 2147483629


def stale_numeric_copy(path, mode):
    raw, stat = path.read_bytes(), path.stat()
    marker = b'PRIME = 2147483647'
    if raw.count(marker) != 1:
        raise ValueError('numeric fixture anchor')
    path.write_bytes(raw.replace(marker, b'PRIME = 2147483629'))
    os.utime(path, ns=(stat.st_atime_ns, stat.st_mtime_ns))
    # Fixture location must not inherit the *test parent's* pycache_prefix:
    # the source-adjacent cache is the deliberately observed old namespace.
    cache = path.parent/'__pycache__'/(path.stem+'.'+sys.implementation.cache_tag+'.pyc')
    py_compile.compile(str(path), cfile=str(cache),
                       doraise=True, invalidation_mode=mode, optimize=0)
    path.write_bytes(raw)
    os.utime(path, ns=(stat.st_atime_ns, stat.st_mtime_ns))
    return hashlib.sha256(raw).hexdigest()


class Controls(unittest.TestCase):
    def test_benign_numeric_cache_modes(self):
        for mode in py_compile.PycInvalidationMode:
            with self.subTest(mode=mode.name), tempfile.TemporaryDirectory() as temp:
                directory = Path(temp)
                leaf = directory/'closure.py'
                shutil.copyfile(R.SOURCE/'closure.py', leaf)
                digest = stale_numeric_copy(leaf, mode)
                observer = directory/'observe.py'
                observer.write_text('from pathlib import Path\nimport sys\n'
                                    'sys.path.insert(0,str(Path(__file__).resolve().parent))\n'
                                    'import closure\nprint(closure.PRIME)\n', encoding='utf-8')
                # Use the actual adapter's interpreter flags, with a harmless
                # numeric observer as the script. This is not a checker bypass.
                cache = directory/'fresh'
                cache.mkdir()
                routed = R.child_command([sys.executable,'-I','-B',str(R.SOURCE/'run.py')], cache, directory)
                flags = routed[:routed.index(str(HERE/'replay.py'))]
                fresh = subprocess.run([*flags,str(observer)], capture_output=True,text=True,check=True)
                old = subprocess.run([sys.executable,'-I','-B',str(observer)],
                                     capture_output=True,text=True,check=True)
                env = dict(os.environ, PYTHONPYCACHEPREFIX=str(directory/'env-only'))
                ignored = subprocess.run([sys.executable,'-I','-B',str(observer)],
                                         env=env,capture_output=True,text=True,check=True)
                expected = CURRENT if mode == py_compile.PycInvalidationMode.CHECKED_HASH else OLD
                self.assertEqual(int(old.stdout),expected)
                self.assertEqual(int(ignored.stdout),expected)
                self.assertEqual(int(fresh.stdout),CURRENT)
                self.assertEqual(hashlib.sha256(leaf.read_bytes()).hexdigest(),digest)

    def test_exact_child_grammar_and_optimization(self):
        with tempfile.TemporaryDirectory() as temp:
            for flags in (['-I','-B'],['-I','-O','-B']):
                argv=[sys.executable,*flags,str(R.SOURCE/'run.py'),'--case','pr589']
                result=R.child_command(argv,Path(temp),Path(temp))
                self.assertEqual(result[1:1+len(flags)],flags)
                self.assertEqual(result[-3:],['--','--case','pr589'])
            for argv in ([sys.executable,'-B',str(R.SOURCE/'run.py')],
                         [sys.executable,'-I','-B',str(R.SOURCE/'closure.py')],
                         [sys.executable,'-I','-B','-X','pycache_prefix=old',str(R.SOURCE/'run.py')]):
                with self.assertRaises(ValueError):
                    R.child_command(argv,Path(temp),Path(temp))
        for name in ('verify.py','run.py','test_closure.py'):
            self.assertIsNotNone(R.program(name))

    def export(self, base):
        package=base/'research'/HERE.name
        shutil.copytree(HERE,package,ignore=shutil.ignore_patterns('__pycache__'))
        for row in json.loads((HERE/'SOURCES.json').read_text())['files']:
            if row['usage']=='input':
                target=base/row['path']
                target.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(ROOT/row['path'],target)
        return package

    def test_changed_current_source_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            base=Path(temp)/'export'
            package=self.export(base)
            leaf=base/'research/bit-frame-closure-basis/closure.py'
            leaf.write_bytes(leaf.read_bytes().replace(b'2147483647',b'2147483629',1))
            process=subprocess.run([sys.executable,'-I','-B',str(package/'replay.py')],
                                   capture_output=True,text=True,timeout=30)
            self.assertNotEqual(process.returncode,0)
            self.assertIn('source SHA256',process.stderr)

    def test_full_git_free_consumer_with_prior_numeric_bytecode(self):
        with tempfile.TemporaryDirectory() as temp:
            base=Path(temp)/'export'
            package=self.export(base)
            leaf=base/'research/bit-frame-closure-basis/closure.py'
            digest=stale_numeric_copy(leaf,py_compile.PycInvalidationMode.TIMESTAMP)
            env=dict(os.environ,PATH='',PYTHONPYCACHEPREFIX=str(Path(temp)/'old-env'))
            process=subprocess.run([sys.executable,'-I','-O','-B',str(package/'replay.py')],
                                   env=env,cwd=base,capture_output=True,text=True,timeout=600)
            self.assertEqual(process.returncode,0,process.stderr)
            self.assertEqual(json.loads(process.stdout),json.loads((HERE/'RESULT.json').read_text()))
            self.assertIn('Ran 9 tests',process.stderr)
            self.assertEqual(hashlib.sha256(leaf.read_bytes()).hexdigest(),digest)


if __name__=='__main__':
    unittest.main()
