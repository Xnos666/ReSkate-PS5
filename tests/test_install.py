import hashlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock
import install


class InstallerTests(unittest.TestCase):
    def test_path_attacks(self):
        for path in ('../x', '/x', 'x/../y', 'x\\y', 'x\nDELE y', 'C:/x', 'x//y', 'x/./y'):
            with self.subTest(path=path), self.assertRaises(ValueError):
                install.relative(path)

    def test_remote_confinement(self):
        for path in ('/data/wowps5/x', '/data/reskate/../wowps5/x', '/data/reskate2/x', '/user/app.db', '/data/reskate/x\rDELE y'):
            with self.subTest(path=path), self.assertRaises(ValueError):
                install.confined(path)
        self.assertEqual(install.GAME + 'Skate.exe', install.confined(install.GAME + 'Skate.exe'))

    def test_external_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'file').write_bytes(b'test')
            try:
                (root / 'link').symlink_to(root / 'file')
            except OSError:
                self.skipTest('Host does not permit symlinks')
            with self.assertRaises(ValueError):
                install.local_file(root, 'link')

    def test_same_size_corruption_is_replaced_and_verified(self):
        console = object.__new__(install.Console)
        console.ftp = Mock()
        console.mkdirs = Mock()
        good = hashlib.sha256(b'good').hexdigest()
        console.remote_hash = Mock(side_effect=[hashlib.sha256(b'evil').hexdigest(), good])
        console.put(install.ROOT + '/file', io.BytesIO(b'good'), good)
        console.ftp.storbinary.assert_called_once()
        console.ftp.rename.assert_called_once()

    def test_corrupt_upload_never_renamed(self):
        console = object.__new__(install.Console)
        console.ftp = Mock()
        console.mkdirs = Mock()
        console.remote_hash = Mock(side_effect=[None, 'wrong'])
        with self.assertRaises(RuntimeError):
            console.put(install.ROOT + '/file', io.BytesIO(b'good'), 'correct')
        console.ftp.rename.assert_not_called()

    def test_verified_file_is_not_rewritten(self):
        console = object.__new__(install.Console)
        console.ftp = Mock()
        console.remote_hash = Mock(return_value='correct')
        console.put(install.ROOT + '/file', io.BytesIO(b'good'), 'correct')
        console.ftp.storbinary.assert_not_called()

    def test_unrelated_existing_install_is_rejected(self):
        console = object.__new__(install.Console)
        console.exists = Mock(return_value=True)
        console.remote_hash = Mock(return_value=None)
        console.put = Mock()
        with self.assertRaises(RuntimeError):
            console.claim()
        console.put.assert_not_called()

    def test_public_or_loopback_host_is_rejected(self):
        for host in ('8.8.8.8', '127.0.0.1', 'example.com', '::1'):
            with self.subTest(host=host), self.assertRaises(ValueError):
                install.Console(host, 2121)

    def test_recognized_runtime_does_not_authorize_another_title(self):
        console = object.__new__(install.Console)
        console.exists = Mock(return_value=True)
        expected = hashlib.sha256(install.MARKER).hexdigest()
        console.remote_hash = Mock(side_effect=lambda path: expected if path == install.ROOT + '/.reskate-installer' else None)
        console.put = Mock()
        with self.assertRaises(RuntimeError):
            console.claim()
        console.put.assert_not_called()
        self.assertEqual(console.remote_hash.call_args_list[-1].args[0], install.TITLE + '/.reskate-installer')


if __name__ == '__main__':
    unittest.main()
