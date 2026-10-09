#!/usr/bin/env python3
"""Small deterministic tests of checker boundaries; no compiler or network calls."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace
import offline_check as c
import prepare_curated_map as curate


class CheckerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.sources = self.root / "source"
        self.sources.mkdir()
        self.map = self.root / "map.json"
        self.records = []
        for name, imports in [("Base", ["Lean"]), ("Child", ["Base"])]:
            text = f"import {' '.join(imports)}\nnamespace {name}\ntheorem correct : True := by trivial\nend {name}\n#print axioms {name}.correct\n"
            (self.sources / f"{name}.lean").write_text(text)
            self.records.append(dict(module=name,source=f"{name}.lean",source_sha256=c.digest(text.encode()),
                                     declarations=1,imports=imports,expected_axiom_commands=[f"{name}.correct"]))
        self.save()

    def tearDown(self): self.temp.cleanup()

    def save(self):
        self.map.write_text(json.dumps(dict(modules=self.records,external_imports=["Lean"],
                                            accepted_module_count=2,accepted_declarations=2)))

    def plan(self): return c.load_plan(self.map, self.sources)

    def test_exact_inputs_and_dependency_closure(self):
        _, _, deps, order, _ = self.plan()
        self.assertEqual(order,["Base","Child"])
        self.assertEqual(c.selected_order(["Child"],deps,order),order)
        self.assertEqual(c.selected_order(["Base"],deps,order),["Base"])
        with self.assertRaises(c.CheckError):c.selected_order(["Missing"],deps,order)

    def test_missing_and_changed_source_rejected(self):
        (self.sources/"Base.lean").write_text("different")
        with self.assertRaisesRegex(c.CheckError,"Changed accepted"):self.plan()
        (self.sources/"Base.lean").unlink()
        with self.assertRaisesRegex(c.CheckError,"Missing accepted"):self.plan()

    def test_duplicate_and_escaping_paths_rejected(self):
        self.records[1]["module"]="Base";self.save()
        with self.assertRaises(c.CheckError):self.plan()
        with self.assertRaises(c.CheckError):c.relative_file(self.sources,"../outside.lean")

    def test_unlisted_import_rejected(self):
        p=self.sources/"Child.lean";text=p.read_text().replace("import Base","import Missing")
        p.write_text(text);self.records[1].update(imports=["Missing"],source_sha256=c.digest(text.encode()));self.save()
        with self.assertRaisesRegex(c.CheckError,"Missing accepted dependency"):self.plan()

    def test_cycle_rejected(self):
        p=self.sources/"Base.lean";text=p.read_text().replace("import Lean","import Child")
        p.write_text(text);self.records[0].update(imports=["Child"],source_sha256=c.digest(text.encode()));self.save()
        with self.assertRaisesRegex(c.CheckError,"Cyclic"):self.plan()

    def test_comments_cannot_forge_imports_or_prints(self):
        text='/- import Bad /- nested -/\n#print axioms fake -/\nimport Lean -- tail\n#print axioms Good.yes\n'
        self.assertEqual(c.source_commands(text),(["Lean"],["Good.yes"]))
        self.assertIn('"-- not a comment"',c.uncomment('def s := "-- not a comment"'))

    def test_exact_axiom_set_and_duplicates(self):
        good="'Base.correct' depends on axioms: [propext, Quot.sound]\n"
        self.assertEqual(c.audit_output(good,["Base.correct"])["declarations"],1)
        for bad in ["",good+good,good.replace("Quot.sound","sorryAx"),good.replace("Base.correct","Other.x")]:
            with self.assertRaises(c.CheckError):c.audit_output(bad,["Base.correct"])

    def test_compile_success_resume_and_tampering(self):
        _,mods,_,_,map_hash=self.plan();output=self.root/"build";compiler={"version":"fixture"}
        calls=[]
        def run(command,**kwargs):
            calls.append(command);Path(command[command.index("-o")+1]).write_bytes(b"fixture object")
            return SimpleNamespace(returncode=0,stdout="'Base.correct' does not depend on any axioms\n",stderr="")
        with patch.object(c.subprocess,"run",side_effect=run):
            first,reused=c.compile_one(mods["Base"],output,{},compiler,Path("/fixture/lean"),map_hash,60,None,False)
            self.assertFalse(reused);self.assertEqual(first["status"],"PASS")
            second,reused=c.compile_one(mods["Base"],output,{},compiler,Path("/fixture/lean"),"new global map",60,None,True)
            self.assertTrue(reused);self.assertEqual(len(calls),1)
            (output/"objects/Base.olean").write_bytes(b"tampered")
            _,reused=c.compile_one(mods["Base"],output,{},compiler,Path("/fixture/lean"),map_hash,60,None,True)
            self.assertFalse(reused);self.assertEqual(len(calls),2)
            (output/"logs/Base.log").write_text("forged")
            self.assertFalse(c.resume_valid(second,second['build_key'],output/'objects/Base.olean',output/'logs/Base.log',['Base.correct']))

    def test_failed_compiler_never_accepts_existing_object(self):
        _,mods,_,_,h=self.plan();out=self.root/'build';(out/'objects').mkdir(parents=True)
        (out/'objects/Base.olean').write_bytes(b'old object')
        with patch.object(c.subprocess,'run',return_value=SimpleNamespace(returncode=1,stdout='',stderr='failed')):
            with self.assertRaises(c.CheckError):c.compile_one(mods['Base'],out,{}, {},Path('/fixture/lean'),h,60,None,False)
        self.assertEqual(json.loads((out/'receipts/Base.json').read_text())['status'],'FAILED')

    def test_timeout_and_wrong_toolchain_rejected(self):
        _,mods,_,_,h=self.plan()
        with patch.object(c.subprocess,'run',side_effect=c.subprocess.TimeoutExpired('fixture',1)):
            with self.assertRaisesRegex(c.CheckError,'timed out'):c.compile_one(mods['Base'],self.root/'build',{}, {},Path('/fixture/lean'),h,1,None,False)
        fake=self.root/'lean';fake.write_bytes(b'fixture')
        with patch.object(c.subprocess,'run',return_value=SimpleNamespace(returncode=0,stdout='wrong version',stderr='')):
            with self.assertRaises(c.CheckError):c.toolchain_identity(fake)

    def test_curated_map_and_scientific_input_pin(self):
        base=json.loads(self.map.read_text());base['target_commit']='fixture';self.map.write_text(json.dumps(base))
        accepted=self.root/'accepted.json';accepted.write_text(json.dumps(self.records))
        input_file=self.sources/'certificate.json';input_file.write_text('{"fixture":1}')
        inputs=[dict(source='certificate.json',destination='inputs/certificate.json',sha256=c.file_hash(input_file))]
        public,plan=curate.prepare(self.sources,self.map,accepted,inputs)
        self.assertEqual([m['source']for m in public['modules']],['src/Base.lean','src/Child.lean'])
        self.assertFalse(plan['archive_built']);self.assertEqual(public['scientific_inputs'][0]['path'],'inputs/certificate.json')
        input_file.write_text('changed')
        with self.assertRaisesRegex(c.CheckError,'Changed scientific input'):curate.prepare(self.sources,self.map,accepted,inputs)


if __name__ == '__main__': unittest.main()
