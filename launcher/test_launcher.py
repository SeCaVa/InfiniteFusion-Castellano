"""Pruebas aisladas: nunca llaman a Git/red ni utilizan el juego o AppData."""
import io
import importlib.util
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import launcher_es as es

def archive(entries):
    out = io.BytesIO()
    with zipfile.ZipFile(out, 'w') as z:
        for path, data in entries:
            z.writestr('repo-traduccion/' + path, data)
    return out.getvalue()

class TranslationTests(unittest.TestCase):
    def test_real_remote_packages(self):
        sample = ROOT / 'translation-sample.zip'
        if not sample.exists():
            self.skipTest('Muestra remota opcional: guardar el ZIP de la rama traduccion como launcher/translation-sample.zip.')
        raw = sample.read_bytes()
        for game in ('kanto', 'hoenn'):
            files = es.translation_files(raw, game)
            self.assertGreater(len(files), 10)
            self.assertIn('Data/spanish.dat', dict(files))
            self.assertFalse(any(rel.endswith('.exe') or rel.startswith('.git') for rel, _ in files))

    def test_game_selection_and_whitelist(self):
        raw = archive([('kanto/Data/spanish.dat', b'kanto'), ('hoenn/Data/spanish.dat', b'hoenn'),
                       ('kanto/Game.exe', b'not allowed'), ('traduccion/script.json', b'not a game file')])
        self.assertEqual(es.translation_files(raw, 'kanto'), [('Data/spanish.dat', b'kanto')])
        self.assertEqual(es.translation_files(raw, 'hoenn'), [('Data/spanish.dat', b'hoenn')])

    def test_invalid_package_does_not_pass(self):
        for raw in (archive([('kanto/Data/../../Game.exe', b'bad')]),
                    archive([('kanto/Data/Scripts/Words.rb', b'first'), ('kanto/Data/Scripts/words.rb', b'second')])):
            with self.assertRaises(ValueError):
                es.translation_files(raw, 'kanto')

    def test_apply_preserves_game_and_save(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
            game = Path(tmp)
            (game / 'Game.exe').write_bytes(b'original')
            (game / 'save.rxdata').write_bytes(b'untouched')
            es.apply_translation(game, [('Data/spanish.dat', b'es'), ('Data/Scripts/words.rb', b'text')], lambda s: None)
            self.assertEqual((game / 'Game.exe').read_bytes(), b'original')
            self.assertEqual((game / 'save.rxdata').read_bytes(), b'untouched')
            self.assertEqual((game / 'Data/spanish.dat').read_bytes(), b'es')

    def test_failed_write_rolls_back(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
            game = Path(tmp)
            (game / 'Data').mkdir()
            (game / 'Data/spanish.dat').write_bytes(b'old')
            writer = es._write_atomic
            failed = False
            def fail_once(path, data):
                nonlocal failed
                if path.name == 'words.rb' and not failed:
                    failed = True
                    raise OSError('simulated failure')
                writer(path, data)
            with patch.object(es, '_write_atomic', fail_once):
                with self.assertRaises(OSError):
                    es.apply_translation(game, [('Data/spanish.dat', b'new'), ('Data/Scripts/words.rb', b'text')], lambda s: None)
            self.assertEqual((game / 'Data/spanish.dat').read_bytes(), b'old')
            self.assertFalse((game / 'Data/Scripts/words.rb').exists())

    def test_installer_applies_translation_after_update(self):
        remote = types.ModuleType('remote_config')
        remote.fetch_games = lambda: {}
        with patch.dict(sys.modules, remote_config=remote):
            spec = importlib.util.spec_from_file_location('test_installer_es', ROOT / 'src/installer.py')
            installer = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(installer)
        installer.GAMES = installer._fallback_games()
        files = [('Data/spanish.dat', b'es'), ('Data/Scripts/words.rb', b'translated')]
        commands = []
        class Process:
            stdout = []
            returncode = 0
            def wait(self): return 0
        with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
            target = Path(tmp) / 'InfiniteFusion'
            target.mkdir()
            def popen(cmd, **kwargs):
                commands.append(cmd)
                if 'reset' in cmd:
                    (target / 'Data/Scripts').mkdir(parents=True, exist_ok=True)
                    (target / 'Data/Scripts/words.rb').write_bytes(b'upstream')
                return Process()
            results = []
            with patch.object(installer, 'download_translation', return_value=files), \
                 patch.object(installer, '_resolve_git', return_value='fake-git'), \
                 patch.object(installer, 'is_existing_folder', return_value=True), \
                 patch.object(installer.subprocess, 'Popen', side_effect=popen), \
                 patch.object(installer.subprocess, 'run', return_value=types.SimpleNamespace(returncode=0, stdout='same-head')):
                installer.run_install('kanto', str(target), lambda *args: None, lambda *args: results.append(args))
            self.assertTrue(results[0][0], results)
            self.assertIn('castellano', results[0][1])
            self.assertEqual((target / 'Data/Scripts/words.rb').read_bytes(), b'translated')
            self.assertEqual((target / 'Data/spanish.dat').read_bytes(), b'es')
            self.assertTrue(any('reset' in cmd for cmd in commands))

    def test_new_install_and_translation_download_failure(self):
        remote = types.ModuleType('remote_config')
        remote.fetch_games = lambda: {}
        with patch.dict(sys.modules, remote_config=remote):
            spec = importlib.util.spec_from_file_location('test_new_installer', ROOT / 'src/installer.py')
            installer = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(installer)
        installer.GAMES = installer._fallback_games()
        class Process:
            stdout = []
            returncode = 0
            def wait(self): return 0
        with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
            results = []
            with patch.object(installer, 'download_translation', side_effect=OSError('offline')), \
                 patch.object(installer, '_resolve_git') as git:
                installer.run_install('hoenn', tmp, lambda *args: None, lambda *args: results.append(args))
                git.assert_not_called()
            self.assertFalse(results[0][0])
            self.assertFalse((Path(tmp) / 'InfiniteFusion2').exists())
            results.clear()
            with patch.object(installer, 'download_translation', return_value=[('Data/spanish.dat', b'hoenn')]), \
                 patch.object(installer, '_resolve_git', return_value='fake-git'), \
                 patch.object(installer.subprocess, 'Popen', return_value=Process()) as clone:
                installer.run_install('hoenn', tmp, lambda *args: None, lambda *args: results.append(args))
            self.assertTrue(results[0][0], results)
            self.assertIn('clone', clone.call_args.args[0])
            self.assertEqual((Path(tmp) / 'InfiniteFusion2/Data/spanish.dat').read_bytes(), b'hoenn')

if __name__ == '__main__':
    unittest.main()
