"""The game is found next to the port in any region, by its param.sfo (scripts/game_id.py)."""
import struct
import tempfile
import unittest
from pathlib import Path

from paths import ROOT  # noqa: F401  (puts scripts/ on sys.path)
import game_id

US = dict(TITLE='Persona 5: Dancing in Starlight', TITLE_ID='CUSA12380',
          CONTENT_ID='UP2611-CUSA12380_00-PERSONA5DUS00000', CATEGORY='gd')
# Other regions as their param.sfo would read: the label of the content ID, or the title.
EU = dict(TITLE='Persona 5: Dancing in Starlight', TITLE_ID='CUSA90001',
          CONTENT_ID='EP2475-CUSA90001_00-PERSONA5DEU00000', CATEGORY='gd')
JP = dict(TITLE='ペルソナ5 ダンシング・スターナイト', TITLE_ID='CUSA90002',
          CONTENT_ID='JP0177-CUSA90002_00-P5DSNJP000000000', CATEGORY='gd')
OTHER = dict(TITLE='Another Game', TITLE_ID='CUSA90003', CONTENT_ID='UP0000-CUSA90003_00-ANOTHERGAME00000',
             CATEGORY='gd')
UPDATE = dict(US, CATEGORY='gp')


def sfo_bytes(values):
    """A minimal param.sfo (PSF 1.1) holding string values."""
    entries, keys, data = b'', b'', b''
    for key, value in values.items():
        text = value.encode() + b'\0'
        entries += struct.pack('<HHIII', len(keys), 0x204, len(text), len(text), len(data))
        keys += key.encode() + b'\0'
        data += text
    keys_offset = 20 + len(entries)
    return (struct.pack('<4sIIII', b'\0PSF', 0x101, keys_offset, keys_offset + len(keys), len(values))
            + entries + keys + data)


def dump(folder, values):
    (folder / 'sce_sys').mkdir(parents=True)
    (folder / 'eboot.bin').write_bytes(b'\x7fELF')
    (folder / 'sce_sys' / 'param.sfo').write_bytes(sfo_bytes(values))
    return folder


class GameIdTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.port = self.base / 'port'
        self.port.mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def test_any_region_is_this_game(self):
        for name, values in (('us', US), ('eu', EU), ('jp', JP)):
            with self.subTest(name):
                self.assertTrue(game_id.is_this_game(values))
        for name, values in (('other game', OTHER), ('update', UPDATE), ('empty', {})):
            with self.subTest(name):
                self.assertFalse(game_id.is_this_game(values))

    def test_finds_a_region_under_any_folder_name(self):
        found = dump(self.base / 'juego' / 'Mi copia JP', JP)
        dump(self.base / 'juego' / 'otro', OTHER)
        self.assertEqual(game_id.default_game_dir(self.port), found)

    def test_american_first_then_juego_before_beside(self):
        dump(self.base / 'CUSA12380', US)
        eu = dump(self.base / 'juego' / 'CUSA90001', EU)
        self.assertEqual(game_id.default_game_dir(self.port), eu)  # juego/ is looked at first
        us = dump(self.base / 'juego' / 'CUSA12380', US)
        self.assertEqual(game_id.default_game_dir(self.port), us)  # the American one wins there

    def test_nothing_found_keeps_the_usual_path(self):
        dump(self.base / 'juego' / 'otro', OTHER)
        self.assertEqual(game_id.default_game_dir(self.port), self.base / 'CUSA12380')


if __name__ == '__main__':
    unittest.main()
