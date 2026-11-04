# SPDX-License-Identifier: GPL-2.0-or-later
"""Which folders hold Persona 5: Dancing in Starlight, in any region.

The game is recognized by its param.sfo, not by one fixed title ID: the CONTENT_ID label
(UP2611-CUSA12380_00-PERSONA5DUS00000 -> PERSONA5D...) or, failing that, the title in English or
Japanese. Known title IDs are only an order of preference when several regions sit side by side."""
from pathlib import Path

# The American release, preferred when there are several; other regions are found by their param.sfo.
KNOWN_TITLE_IDS = ('CUSA12380',)
CONTENT_LABEL = 'PERSONA5D'
TITLES = ('Dancing in Starlight', 'Dancing Star Night', 'ダンシング・スターナイト')


def sfo(folder):
    """The values of folder/sce_sys/param.sfo, or {} (prepare.read_sfo)."""
    try:
        from prepare import read_sfo
    except ImportError:
        return {}
    try:
        return read_sfo(Path(folder) / 'sce_sys' / 'param.sfo') or {}
    except (OSError, ValueError):
        return {}


def is_this_game(values):
    """Whether param.sfo values are those of this game (a base game, not an update or a DLC)."""
    if not values or values.get('CATEGORY', 'gd') not in ('gd', 'gde'):
        return False
    label = (values.get('CONTENT_ID') or '')[20:]
    if label.startswith(CONTENT_LABEL):
        return True
    title = (values.get('TITLE') or '').replace('™', '').replace('®', '')
    return any(name.casefold() in title.casefold() for name in TITLES)


def game_folders(parents):
    """[folder] with eboot.bin and this game's param.sfo directly inside each of `parents`: the
    known title IDs first (in their order), then the rest by name."""
    found = []
    for parent in parents:
        try:
            children = sorted((p for p in Path(parent).iterdir() if p.is_dir()), key=lambda p: p.name.casefold())
        except OSError:
            continue
        rank = {tid: i for i, tid in enumerate(KNOWN_TITLE_IDS)}
        children.sort(key=lambda p: rank.get(p.name.upper(), len(rank)))
        for child in children:
            if (child / 'eboot.bin').is_file() and is_this_game(sfo(child)):
                found.append(child)
    return found


def default_game_dir(port_dir):
    """The game next to the port, any region: ../juego/<folder> or ../<folder>; else ../CUSA12380."""
    port_dir = Path(port_dir)
    found = game_folders((port_dir.parent / 'juego', port_dir.parent))
    return found[0] if found else port_dir.parent / KNOWN_TITLE_IDS[0]
