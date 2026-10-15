"""The CI planner must skip a verification group only when no changed path can reach it."""
import importlib.util
import json
import os
from pathlib import Path
import re
import runpy
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('plan_verify_groups', ROOT / 'scripts/plan_verify_groups.py')
planner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(planner)

MANIFEST = {
    'python': ['3.11', '3.13'],
    'full_label': 'ci:full-verify',
    'all': ['Makefile', 'scripts/**', '.github/workflows/verify.yml', '.github/verify-groups.json'],
    'skip_safe': ['research/**', 'docs/**', 'README.md', '.github/workflows/**'],
    'groups': {
        'alpha': {'paths': ['certificates/alpha.json', 'certificates/*', 'notes/**']},
        'beta': {'paths': ['research/beta-package/**']},
        'formal-historical': {'job': 'formal', 'package': 'historical', 'paths': ['formal/**']},
        'formal-matrix': {'job': 'formal', 'package': 'matrix', 'paths': ['research/matrix-exponent-synthesis/**']},
        'pkg-bit-elim-144': {'job': 'package', 'package': 'bit-elim-144', 'python': ['3.11', '3.14'],
                             'command': 'python3 research/bit-elim-144/verify.py',
                             'paths': ['research/bit-elim-144/**', 'certificates/paired-cube-bit-input.json']},
        'whole': {'paths': ['**']},
    },
}
ALL_GROUPS = ['alpha', 'beta', 'formal-historical', 'formal-matrix', 'pkg-bit-elim-144', 'whole']


def run_plan(changed, event='pull_request', **kw):
    return planner.plan(MANIFEST, event, changed, **kw)


class PatternSemantics(unittest.TestCase):
    def test_exact_and_recursive_match_any_status(self):
        for status in 'AMD':
            self.assertTrue(planner.pattern_matches('certificates/alpha.json', 'certificates/alpha.json', status))
            self.assertTrue(planner.pattern_matches('notes/**', 'notes/deep/x.tex', status))
            self.assertTrue(planner.pattern_matches('notes/**', 'notes', status))
            self.assertTrue(planner.pattern_matches('**', 'anything/at/all', status))
        self.assertFalse(planner.pattern_matches('notes/**', 'notes-extra/x', 'A'))
        self.assertFalse(planner.pattern_matches('certificates/alpha.json', 'certificates/alpha.json.bak', 'A'))

    def test_listing_patterns_without_tree_information_are_conservative(self):
        self.assertTrue(planner.pattern_matches('certificates/*', 'certificates/new.json', 'A'))
        self.assertTrue(planner.pattern_matches('certificates/*', 'certificates/old.json', 'D'))
        self.assertFalse(planner.pattern_matches('certificates/*', 'certificates/old.json', 'M'))
        self.assertTrue(planner.pattern_matches('certificates/*', 'certificates/sub/new.json', 'A'))  # any ancestor
        self.assertTrue(planner.pattern_matches('*', 'NEWFILE', 'A'))
        self.assertTrue(planner.pattern_matches('*', 'dir/file', 'A'))
        self.assertFalse(planner.pattern_matches('*', 'README.md', 'M'))

    def test_listing_changed_by_uses_the_deepest_existing_ancestor(self):
        base = {'research', 'research/old', 'certificates'}
        self.assertEqual(planner.listing_changed_by('research/new/README.md', 'A', base, base), 'research')
        self.assertEqual(planner.listing_changed_by('research/old/extra.json', 'A', base, base), 'research/old')
        self.assertEqual(planner.listing_changed_by('NEWFILE', 'A', base, base), '')
        self.assertEqual(planner.listing_changed_by('brand/new/tree/x', 'A', base, base), '')
        self.assertEqual(planner.listing_changed_by('research/old/gone.json', 'D', base, {'research'}), 'research')
        self.assertIsNone(planner.listing_changed_by('research/old/x', 'M', base, base))
        self.assertIs(planner.listing_changed_by('research/old/x', 'A'), planner.ANY_ANCESTOR)

    def test_existence_patterns_match_only_creation_or_removal(self):
        base = {'research', 'research/old'}
        self.assertEqual(planner.directories_changed_by('research/new/x', 'A', base, base), {'research/new'})
        self.assertEqual(planner.directories_changed_by('research/old/x', 'A', base, base), set())
        self.assertEqual(planner.directories_changed_by('research/old/x', 'D', base, {'research'}), {'research/old'})
        self.assertIsNone(planner.directories_changed_by('research/old/x', 'M', base, base))
        self.assertTrue(planner.pattern_matches('research/new/', 'research/new/x', 'A', 'research', {'research/new'}))
        self.assertFalse(planner.pattern_matches('research/', 'research/new/x', 'A', 'research', {'research/new'}))
        self.assertFalse(planner.pattern_matches('research/old/', 'research/old/x', 'M', None, None))
        self.assertTrue(planner.pattern_matches('research/', 'research/new/x', 'A'))  # conservative without trees
        manifest = json.loads(json.dumps(MANIFEST)); del manifest['groups']['whole']
        manifest['groups']['alpha']['paths'].append('research/')
        dirs = {'research', 'research/old'}
        result = planner.plan(manifest, 'pull_request', ['A:research/new/x'], base_dirs=dirs, head_dirs=dirs | {'research/new'})
        self.assertEqual(result['mode'], 'none', result['reason'])
        result = planner.plan(manifest, 'pull_request', ['A:research/old/deeper/x'], base_dirs=dirs, head_dirs=dirs | {'research/old/deeper'})
        self.assertEqual(result['mode'], 'none', result['reason'])  # research/old still exists; only a subdirectory was created
        result = planner.plan(manifest, 'pull_request', ['A:research/new/x'])  # no tree information: conservative
        self.assertEqual((result['mode'], result['groups']), ('selected', ['alpha']))

    def test_removing_or_creating_a_listed_directory_matches_its_listing(self):
        base = {'research', 'research/pkg'}
        # deleting the last file of research/pkg removes that directory: its own listing pattern must match
        listing = planner.listing_changed_by('research/pkg/last.json', 'D', base, {'research'})
        removed = planner.directories_changed_by('research/pkg/last.json', 'D', base, {'research'})
        self.assertEqual((listing, removed), ('research', {'research/pkg'}))
        self.assertTrue(planner.pattern_matches('research/pkg/*', 'research/pkg/last.json', 'D', listing, removed))
        self.assertTrue(planner.pattern_matches('research/*', 'research/pkg/last.json', 'D', listing, removed))
        self.assertFalse(planner.pattern_matches('research/other/*', 'research/pkg/last.json', 'D', listing, removed))
        manifest = json.loads(json.dumps(MANIFEST)); del manifest['groups']['whole']
        manifest['groups']['alpha']['paths'].append('research/pkg/*')
        result = planner.plan(manifest, 'pull_request', ['D:research/pkg/last.json'], base_dirs=base, head_dirs={'research'})
        self.assertEqual(result['groups'], ['alpha'])

    def test_listing_patterns_with_tree_information_are_precise(self):
        new = {'research/new'}
        self.assertTrue(planner.pattern_matches('research/*', 'research/new/README.md', 'A', 'research', new))
        self.assertFalse(planner.pattern_matches('*', 'research/new/README.md', 'A', 'research', new))
        self.assertTrue(planner.pattern_matches('research/new/*', 'research/new/README.md', 'A', 'research', new))
        self.assertFalse(planner.pattern_matches('research/*', 'research/old/extra.json', 'A', 'research/old', set()))
        self.assertTrue(planner.pattern_matches('research/old/*', 'research/old/extra.json', 'A', 'research/old', set()))
        self.assertFalse(planner.pattern_matches('research/*', 'research/old/x', 'M', None, None))

    def test_validate_pattern_rejects_other_globs(self):
        for good in ('Makefile', 'scripts/**', 'certificates/*', '*', '**', 'a/b/c.json', 'research/'):
            planner.validate_pattern(good)
        for bad in ('research/*/x', 'foo//', '../x', '*.md', '', '/abs', 'a\\b', 'a/**/b', '/'):
            with self.assertRaises(ValueError, msg=bad):
                planner.validate_pattern(bad)


class Selection(unittest.TestCase):
    def test_research_only_pull_request_runs_only_whole_tree_groups(self):
        result = run_plan(['A:research/new-package/README.md', 'A:research/new-package/verify.py'])
        self.assertEqual(result['mode'], 'selected')
        self.assertEqual(result['groups'], ['whole'])
        self.assertEqual(result['include'], [{'python-version': '3.11', 'group': 'whole'},
                                             {'python-version': '3.13', 'group': 'whole'}])
        self.assertEqual(result['jobs'], [])

    def test_whole_tree_group_does_not_explain_unknown_paths(self):
        # `**` selects its group but a path nobody declared still runs everything.
        kind, groups = planner.classify(MANIFEST, 'SOURCES.json', 'M', None)
        self.assertEqual((kind, groups), ('unclassified', ['whole']))
        self.assertEqual(run_plan(['M:SOURCES.json'])['mode'], 'full')
        kind, groups = planner.classify(MANIFEST, 'research/x/y', 'M', None)
        self.assertEqual((kind, groups), ('skip_safe', ['whole']))

    def test_ignored_tracked_path_runs_everything(self):
        result = planner.plan(MANIFEST, 'pull_request', ['A:research/x/__pycache__/m.pyc'],
                              ignored={'research/x/__pycache__/m.pyc'})
        self.assertEqual(result['mode'], 'full')

    def test_declared_package_input_selects_its_group_on_every_python(self):
        result = run_plan(['M:research/beta-package/words.json'])
        self.assertEqual(result['mode'], 'selected')
        self.assertEqual(result['groups'], ['beta', 'whole'])
        self.assertEqual(result['include'], [{'python-version': '3.11', 'group': 'beta'},
                                             {'python-version': '3.13', 'group': 'beta'},
                                             {'python-version': '3.11', 'group': 'whole'},
                                             {'python-version': '3.13', 'group': 'whole'}])

    def test_group_match_takes_precedence_over_skip_safe(self):
        kind, groups = planner.classify(MANIFEST, 'research/beta-package/x', 'M')
        self.assertEqual((kind, groups), ('group', ['beta', 'whole']))

    def test_added_entry_in_listed_directory_selects_group(self):
        result = run_plan(['A:certificates/brand-new.json'])
        self.assertEqual((result['mode'], result['groups']), ('selected', ['alpha', 'whole']))

    def test_root_listing_is_not_changed_by_a_new_file_in_an_existing_directory(self):
        manifest = json.loads(json.dumps(MANIFEST))
        manifest['groups']['alpha']['paths'].append('*')  # make lists the root for every group
        dirs = {'research', 'research/old', 'certificates'}
        result = planner.plan(manifest, 'pull_request', ['A:research/new/README.md'], base_dirs=dirs, head_dirs=dirs)
        self.assertEqual((result['mode'], result['groups']), ('selected', ['whole']), result['reason'])
        result = planner.plan(manifest, 'pull_request', ['A:brand-new-dir/x'], base_dirs=dirs, head_dirs=dirs)
        self.assertEqual(result['mode'], 'full')  # a new root entry always verifies everything
        self.assertEqual(planner.classify(manifest, 'brand-new-dir/x', 'A', '')[0], 'all')
        self.assertEqual(planner.classify(manifest, 'NEWFILE', 'A')[0], 'all')
        result = planner.plan(manifest, 'pull_request', ['A:research/new/README.md'])  # no tree info
        self.assertEqual((result['mode'], result['groups']), ('selected', ['alpha', 'whole']))

    def test_modified_undeclared_file_in_listed_directory_runs_everything(self):
        # Only the listing was recorded, so an edit to an unread file is unclassified: fail closed.
        result = run_plan(['M:certificates/other.json'])
        self.assertEqual(result['mode'], 'full')
        self.assertIn('not declared', result['reason'])
        self.assertEqual(result['groups'], ALL_GROUPS)

    def test_root_documentation_edit_is_inert_but_new_root_file_is_not(self):
        self.assertEqual(run_plan(['M:README.md'])['groups'], ['whole'])
        self.assertEqual(run_plan(['A:NEWFILE.md'])['mode'], 'full')
        self.assertEqual(run_plan(['D:NOTICE'])['mode'], 'full')
        self.assertEqual(run_plan(['M:SOURCES.json'])['mode'], 'full')  # unclassified root file edit

    def test_all_paths_run_everything_and_record_inputs(self):
        for path in ('M:Makefile', 'A:scripts/new_tool.py', 'M:.github/workflows/verify.yml',
                     'M:.github/verify-groups.json'):
            result = run_plan([path, 'A:research/x/y'])
            self.assertEqual(result['mode'], 'full', path)
            self.assertEqual(len(result['include']), 6, path)  # alpha, beta, whole x two Pythons
            self.assertEqual(result['jobs'], ['formal', 'package'], path)
            self.assertEqual(result['formal'], [{'package': 'historical'}, {'package': 'matrix'}], path)
            self.assertEqual([p['python-version'] for p in result['packages']], ['3.11', '3.14'], path)
            self.assertEqual(result['packages'][0]['command'], 'python3 research/bit-elim-144/verify.py', path)

    def test_formal_only_change_runs_that_formal_package_without_matrix(self):
        manifest = json.loads(json.dumps(MANIFEST)); del manifest['groups']['whole']
        result = planner.plan(manifest, 'pull_request', ['M:formal/lean/Foo.lean'])
        self.assertEqual(result['mode'], 'selected')
        self.assertEqual(result['include'], [])
        self.assertEqual(result['jobs'], ['formal'])
        self.assertEqual(result['formal'], [{'package': 'historical'}])
        self.assertEqual(result['packages'], [])

    def test_package_verifier_selected_on_its_pinned_input(self):
        result = run_plan(['M:certificates/paired-cube-bit-input.json'])
        self.assertEqual(result['groups'], ['pkg-bit-elim-144', 'whole'])
        self.assertEqual(len(result['include']), 2)
        self.assertEqual(result['jobs'], ['package'])
        self.assertEqual([p['package'] for p in result['packages']], ['bit-elim-144', 'bit-elim-144'])

    def test_root_git_configuration_files_run_everything(self):
        for path in ('M:.gitattributes', 'A:.gitignore', 'A:x/.gitmodules', 'M:.gitmodules'):
            self.assertEqual(run_plan([path])['mode'], 'full', path)

    def test_nested_git_configuration_files_count_as_their_whole_subtree(self):
        manifest = json.loads(json.dumps(MANIFEST)); del manifest['groups']['whole']
        # inside a research package: everything below is skip-safe, beta's declared package is unaffected
        result = planner.plan(manifest, 'pull_request', ['A:research/new/.gitattributes'])
        self.assertEqual(result['mode'], 'none', result['reason'])
        # inside beta's declared package: beta runs
        result = planner.plan(manifest, 'pull_request', ['A:research/beta-package/.gitattributes'])
        self.assertEqual((result['mode'], result['groups']), ('selected', ['beta']))
        # above a declared input (notes/** of alpha): alpha runs
        result = planner.plan(manifest, 'pull_request', ['M:notes/.gitignore'])
        self.assertEqual((result['mode'], result['groups']), ('selected', ['alpha']))
        # in an undeclared directory: unclassified, everything runs
        self.assertEqual(planner.plan(manifest, 'pull_request', ['A:references/.gitattributes'])['mode'], 'full')
        # in scripts/: an `all` path
        self.assertEqual(planner.plan(manifest, 'pull_request', ['A:scripts/x/.gitattributes'])['mode'], 'full')
        self.assertTrue(planner.subtree_matches('research/beta-package/**', 'research'))  # pattern below the directory
        self.assertTrue(planner.subtree_matches('research/**', 'research/beta-package'))  # pattern above it
        self.assertFalse(planner.subtree_matches('notes/**', 'research'))

    def test_other_workflow_edits_are_inert(self):
        manifest = json.loads(json.dumps(MANIFEST)); del manifest['groups']['whole']
        self.assertEqual(planner.plan(manifest, 'pull_request', ['M:.github/workflows/other.yml'])['mode'], 'none')

    def test_bare_paths_are_treated_as_additions(self):
        self.assertEqual(planner.split_status('certificates/x.json'), ('A', 'certificates/x.json'))
        self.assertEqual(planner.split_status('M:certificates/x.json'), ('M', 'certificates/x.json'))
        self.assertEqual(run_plan(['certificates/new.json'])['groups'], ['alpha', 'whole'])


class FullRunTriggers(unittest.TestCase):
    def test_schedule_and_dispatch_always_run_everything(self):
        for event in ('schedule', 'workflow_dispatch'):
            result = run_plan(None, event=event)
            self.assertEqual(result['mode'], 'full', event)
            self.assertEqual(len(result['include']), 6)
            self.assertEqual(len(result['formal']), 2)
            self.assertEqual(len(result['packages']), 2)

    def test_missing_or_failed_diff_fails_closed(self):
        self.assertEqual(run_plan(None)['mode'], 'full')
        self.assertEqual(run_plan(None, diff_error='base is the all-zero SHA')['mode'], 'full')
        self.assertEqual(run_plan(None, event='push', diff_error='fetch failed')['mode'], 'full')

    def test_full_label(self):
        self.assertEqual(run_plan([], action='labeled', label='ci:full-verify')['mode'], 'full')
        self.assertEqual(run_plan(['A:research/x/y'], labels=['ci:full-verify'])['mode'], 'full')

    def test_unrelated_label_preserves_existing_full_request(self):
        result = run_plan(['M:research/beta-package/words.json'], action='labeled',
                          label='needs-review', labels=['ci:full-verify', 'needs-review'])
        self.assertEqual(result['mode'], 'full')
        self.assertEqual(result['groups'], ALL_GROUPS)

    def test_unrelated_label_verifies_the_same_changes_as_a_regular_run(self):
        for changed, options in ((['M:research/beta-package/words.json'], {}),
                                 (['M:scripts/exclusion_circuit.py'], {}),
                                 (None, {'diff_error': 'merge parent unavailable'})):
            with self.subTest(changed=changed, options=options):
                expected = run_plan(changed, **options)
                result = run_plan(changed, action='labeled', label='needs-review',
                                  labels=['needs-review'], **options)
                self.assertEqual(result, expected)

    def test_unknown_event_runs_everything(self):
        self.assertEqual(run_plan(['A:research/x/y'], event='merge_group')['mode'], 'full')

    def test_force_full(self):
        self.assertEqual(run_plan(['A:research/x/y'], force_full=True)['mode'], 'full')


class GitDiff(unittest.TestCase):
    def test_statuses_and_renames(self):
        with tempfile.TemporaryDirectory() as tmp:
            env = dict(os.environ, GIT_AUTHOR_NAME='t', GIT_AUTHOR_EMAIL='t@x', GIT_COMMITTER_NAME='t',
                       GIT_COMMITTER_EMAIL='t@x', GIT_CONFIG_GLOBAL='/dev/null', GIT_CONFIG_NOSYSTEM='1')
            git = lambda *a: subprocess.run(['git', *a], cwd=tmp, env=env, check=True, stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE).stdout.decode().strip()
            git('init', '-q')
            Path(tmp, 'keep.txt').write_text('a')
            Path(tmp, 'gone.txt').write_text('b')
            Path(tmp, 'moved.txt').write_text('c' * 100)
            git('add', '.'); git('commit', '-qm', 'base'); base = git('rev-parse', 'HEAD')
            Path(tmp, 'keep.txt').write_text('a2')
            Path(tmp, 'gone.txt').unlink()
            Path(tmp, 'moved.txt').rename(Path(tmp, 'renamed.txt'))
            Path(tmp, 'new.txt').write_text('d')
            git('add', '-A'); git('commit', '-qm', 'change')
            changed, links = planner.git_changed(base, 'HEAD', cwd=tmp)
            self.assertEqual(sorted(changed), ['A:new.txt', 'A:renamed.txt', 'D:gone.txt', 'D:moved.txt', 'M:keep.txt'])
            self.assertEqual(links, set())
            os.symlink('keep.txt', Path(tmp, 'alias.txt'))
            Path(tmp, '.gitignore').write_text('*.log\n'); Path(tmp, 'noise.log').write_text('x')
            git('add', '-A'); git('add', '-f', 'noise.log'); git('commit', '-qm', 'link')
            changed, links = planner.git_changed('HEAD^', 'HEAD', cwd=tmp)
            self.assertEqual(links, {'alias.txt'})
            self.assertEqual(planner.git_ignored(['noise.log', 'keep.txt'], cwd=tmp), {'noise.log'})
            with self.assertRaises(ValueError):
                planner.git_changed(planner.ZERO_SHA, 'HEAD', cwd=tmp)
            with self.assertRaises(ValueError):
                planner.git_changed('0123456789abcdef0123456789abcdef01234567', 'HEAD', cwd=tmp)
            Path(tmp, 'sub/deeper').mkdir(parents=True); Path(tmp, 'sub/deeper/f').write_text('x')
            git('add', '-A'); git('commit', '-qm', 'dirs')
            self.assertEqual(planner.git_dirs('HEAD', cwd=tmp), {'sub', 'sub/deeper'})
            self.assertEqual(planner.git_dirs(base, cwd=tmp), set())


class Outputs(unittest.TestCase):
    def test_github_output_and_summary(self):
        result = run_plan(['M:research/beta-package/words.json'])
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp, 'out')
            planner.write_outputs(result, out)
            text = out.read_text()
        values = dict(line.split('=', 1) for line in text.strip().splitlines())
        self.assertEqual(json.loads(values['matrix']), {'include': result['include']})
        self.assertEqual(values['count'], '4')
        self.assertEqual(values['groups'], 'beta,whole')
        self.assertEqual(values['jobs'], '')
        self.assertEqual(json.loads(values['formal']), {'include': []})
        self.assertEqual(values['formal_count'], '0')
        self.assertEqual(json.loads(values['packages']), {'include': []})
        self.assertEqual(values['package_count'], '0')
        self.assertEqual(values['mode'], 'selected')
        self.assertNotIn('trace', values)
        summary = planner.summary_markdown(result, 'pull_request')
        self.assertIn('**selected**', summary)
        self.assertIn('M:research/beta-package/words.json', summary)


class RepositoryManifest(unittest.TestCase):
    """The committed manifest must match the Makefile's CI groups and validate."""
    def test_new_nearer_lean_project_selects_historical_formal(self):
        manifest = planner.load_manifest(ROOT / '.github/verify-groups.json')
        base_dirs = {'formal', 'formal/lean', 'research', 'research/ranked-pair-verification',
                     'research/ranked-pair-verification/lean'}
        # ranked-pair's default_project probes these nearer ancestors before
        # formal/lean. Creating a toolchain file can change the project it uses.
        for directory in ('research/formal/lean', 'research/ranked-pair-verification/formal/lean'):
            head_dirs = base_dirs | {directory, directory.rsplit('/', 1)[0]}
            for event in ('pull_request', 'push'):
                with self.subTest(directory=directory, event=event):
                    result = planner.plan(manifest, event, ['A:' + directory + '/lean-toolchain'],
                                          base_dirs=base_dirs, head_dirs=head_dirs)
                    self.assertEqual(result['mode'], 'selected', result['reason'])
                    self.assertIn('formal-historical', result['groups'])
                    self.assertIn({'package': 'historical'}, result['formal'])

    def test_historical_formal_follows_its_external_source_references(self):
        manifest = planner.load_manifest(ROOT / '.github/verify-groups.json')
        sources = runpy.run_path(str(ROOT / 'formal/lean/sources.py'))
        # The source audit runs after compilation and reads notes, certificate
        # values and upstream paper lines outside the formal project tree.
        paths = {ref.path for row in sources['ROWS'] for ref in row[3]}
        self.assertIn('notes/compact-control-note.tex', paths)
        self.assertIn('certificates/compact-control-layer.json', paths)
        self.assertIn('upstream/build/sections/03-motifs.tex', paths)
        for event in ('pull_request', 'push'):
            for path in sorted(paths):
                with self.subTest(event=event, path=path):
                    result = planner.plan(manifest, event, ['M:' + path])
                    self.assertIn('formal-historical', result['groups'], result['reason'])
                    self.assertIn({'package': 'historical'}, result['formal'])

    def test_manifest_loads_and_groups_match_makefile(self):
        manifest = planner.load_manifest(ROOT / '.github/verify-groups.json')
        self.assertEqual(manifest['python'], ['3.11', '3.13', '3.14'])
        makefile = (ROOT / 'Makefile').read_text()
        targets = set(re.findall(r'^verify-([a-z0-9-]+):', makefile, re.M))
        verify_groups = {g for g, spec in manifest['groups'].items() if spec.get('job', 'verify') == 'verify'}
        self.assertEqual(verify_groups, targets - {'parallel'})
        self.assertEqual({spec.get('job', 'verify') for spec in manifest['groups'].values()},
                         {'verify', 'ranked-pair-finite', 'formal', 'package'})
        formal = {spec['package'] for spec in manifest['groups'].values() if spec.get('job') == 'formal'}
        self.assertEqual(formal, set(re.findall(r'^formal-([a-z]+)-verify:', makefile, re.M)))
        packages = {spec['package'] for spec in manifest['groups'].values() if spec.get('job') == 'package'}
        self.assertEqual(packages, {'bit-elim-144', 'bit-reuse-147', 'early-reset-reuse', 'graded-box-convolution'})
        full = planner.plan(manifest, 'workflow_dispatch')
        self.assertEqual(len(full['include']), 48)
        self.assertEqual(len({(i['python-version'], i['group']) for i in full['include']}), 48)
        self.assertEqual(len(full['formal']), 3)
        self.assertEqual(len(full['packages']), 8)
        for key in ('Makefile', 'scripts/**', '.github/workflows/verify.yml', '.github/verify-groups.json',
                    '.gitattributes'):
            self.assertIn(key, manifest['all'])

    def test_a_new_research_package_runs_only_whole_tree_groups(self):
        manifest = planner.load_manifest(ROOT / '.github/verify-groups.json')
        dirs = planner.git_dirs('HEAD')
        result = planner.plan(manifest, 'pull_request',
                              ['A:research/zz-new-package/README.md', 'A:research/zz-new-package/verify.py',
                               'A:research/zz-new-package/VERIFY.json', 'A:.github/workflows/zz-new-package.yml'],
                              base_dirs=dirs, head_dirs=dirs | {'research/zz-new-package'})
        self.assertNotEqual(result['mode'], 'full', result['reason'])
        broad = {g for g, spec in manifest['groups'].items()
                 if '**' in spec['paths'] or 'research/**' in spec['paths'] or 'research/*' in spec['paths']}
        self.assertEqual(set(result['groups']), broad, result['reason'])
        for group in result['matrix_groups']:
            self.assertEqual([i['python-version'] for i in result['include'] if i['group'] == group],
                             manifest['python'])


if __name__ == '__main__':
    unittest.main()
