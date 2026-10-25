#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Trophies of Persona 5: Dancing in Starlight (CUSA12380): the list and the unlocks.

The game unlocks a trophy through sceNpTrophyUnlockTrophy with its id; the runtime appends
"id unix-time" to <user>/trophies.log and shows the notice in game. The names and descriptions
live here because the game's own trophy texts (TROP.ESFM) are encrypted; the icons are read
from sce_sys/trophy/trophy00.trp, where they are plain PNG files (TROP000.PNG = trophy 0).

As a script: trophies.py <game> --out <dir> writes <dir>/trophies.txt (id, grade, name per line,
read by the runtime) and the icons to <dir>/trophies/.
"""
import argparse
from pathlib import Path
import struct

PLATINUM, GOLD, SILVER, BRONZE = 'platinum', 'gold', 'silver', 'bronze'
GRADES = (PLATINUM, GOLD, SILVER, BRONZE)
PLATINUM_ID = 0
LOG_NAME = 'trophies.log'

# (id, grade, name, description)
TROPHIES = [
    (0, PLATINUM, 'Dancing in Starlight', 'Obtained all trophies.'),
    (1, BRONZE, 'Careful Planning', 'Played a tutorial.'),
    (2, BRONZE, 'Solid Bonds', 'Watched a Social event.'),
    (3, BRONZE, 'Infiltration Mission: Start!', "Explored a friend's room."),
    (4, BRONZE, 'Unwavering Interests', 'Watched 20 Social events.'),
    (5, SILVER, "I've Taken Your Rooms, Lads!", "Explored all the guys' rooms."),
    (6, SILVER, "I'll Steal Your Hearts, My Dears!", "Explored all the girls' rooms."),
    (7, SILVER, 'The Best Reward', 'Obtained an invaluable treasure upon the stage.'),
    (8, GOLD, 'Beyond the Dream', 'Watched all Social events.'),
    (9, BRONZE, 'A Few Small Gifts', "Obtained 5 rewards from the Twins' card hunt."),
    (10, SILVER, 'Prince of the Phantom Thieves', "Obtained all rewards from the Twins' card hunt."),
    (11, BRONZE, 'Follow My Lead, Inmate!', 'Had the Twins join the grand ball.'),
    (12, SILVER, "I'm Just Getting Started", 'Unlocked the highest difficulty level (ALL NIGHT).'),
    (13, BRONZE, 'Ready to Party', 'Obtained a costume.'),
    (14, SILVER, "I've Stolen About Half!", 'Obtained half of all the costumes.'),
    (15, GOLD, 'Phantom Thief in Full Bloom', 'Obtained all the costumes.'),
    (16, BRONZE, "A Phantom Thief's Most Indispensable Tool", 'Obtained all the pairs of glasses.'),
    (17, BRONZE, 'Sparkling Quarry', 'Obtained half of all the accessories.'),
    (18, SILVER, 'Legendary Treasure Cache', 'Obtained all the accessories.'),
    (19, BRONZE, 'Suspect in Custody!', 'Failed a stage.'),
    (20, BRONZE, "It's Showtime!", 'Cleared a stage.'),
    (21, SILVER, 'The First Step to Greatness', 'Earned the highest possible grade on a stage (KING CRAZY).'),
    (22, SILVER, 'The Perfect Crime',
     'Cleared a stage on HARD or harder and earned a PERFECT rating on at least half of the Notes.'),
    (23, BRONZE, 'Unstoppable', 'Beat your own high score.'),
    (24, BRONZE, 'I Am Thou, Thou Art Who?',
     'Started a stage with a different hairstyle, two accessories, color contacts, and a colored wig.'),
    (25, BRONZE, 'Masters of Disguise',
     'Changed costumes and played a stage with each of the Phantom Thieves (excluding Akechi).'),
    (26, GOLD, 'Stars Dancing in Starlight', 'Watched 40 different Fever Time dances.'),
    (27, SILVER, 'The Ultimate Guide for Tricksters', 'Watched every possible dance for the P5 Protagonist (Ren Amamiya).'),
    (28, SILVER, 'Alibaba Fanatic', 'Watched every possible dance for Futaba.'),
    (29, BRONZE, 'The Dragon and the Panther', 'Cleared the stages where Ryuji and Ann dance together.'),
    (30, BRONZE, 'The Student and the Teacher', 'Cleared the stages where Morgana and Haru dance together.'),
    (31, BRONZE, 'The Unusual and the Uptight', 'Cleared the stages where Yusuke and Makoto dance together.'),
    (32, BRONZE, 'Phantom Choreographers', 'Watched a replay.'),
    (33, BRONZE, 'A Mountain of Treasure', 'Unlocked all ???s in Collection.'),
    (34, BRONZE, 'Stylish Phantom Thieves', 'Registered a costume as a Favorite.'),
    (35, SILVER, 'Fully Tuned Up and Ready to Go', 'Unlocked all Custom modifiers.'),
    (36, BRONZE, 'Hype It Your Way', 'Cleared a stage after changing Hype Gauge difficulty in Custom.'),
    (37, BRONZE, 'A Safe Tightrope Walk',
     'Cleared a stage with both "GOOD ratings won\'t break combos" and "Game Over with combo break" enabled.'),
    (38, BRONZE, 'Trick Note', 'Cleared a stage with both "Note paths waver" and "Note speed fluctuates" enabled.'),
    (39, BRONZE, 'Infiltration Route Secured', 'Cleared a stage on HARD or harder with all Support modifiers enabled.'),
    (40, BRONZE, 'Indecisive Advance', 'Cleared a stage with 5 Challenge and 5 Support modifiers simultaneously enabled.'),
    (41, BRONZE, 'An Impossible Mission', 'Started a stage on ALL NIGHT difficulty with 10 or more Challenge modifiers enabled.'),
]
BY_ID = {t[0]: t for t in TROPHIES}
# Spanish: id -> (name, description).
SPANISH = {
    0: ('Dancing in Starlight', 'Consigue el resto de trofeos.'),
    1: ('Planificación prudente', 'Juega un tutorial.'),
    2: ('Vínculos sólidos', 'Ve un evento social.'),
    3: ('Misión de infiltración: ¡Adelante!', 'Explora la habitación de un amigo.'),
    4: ('Intereses inquebrantables', 'Ve 20 eventos sociales.'),
    5: ('¡Os he arrebatado las habitaciones, tíos!', 'Explora las habitaciones de todos los chicos.'),
    6: ('¡Os robaré el corazón, señoritas!', 'Explora las habitaciones de todas las chicas.'),
    7: ('La mejor recompensa', 'Consigue un tesoro de valor incalculable sobre el escenario.'),
    8: ('Más allá de los sueños', 'Ve todos los eventos sociales.'),
    9: ('Unos regalitos', 'Consigue 5 recompensas de la búsqueda de cartas de las gemelas.'),
    10: ('Príncipe de los Phantom Thieves', 'Consigue todas las recompensas de la búsqueda de cartas de las gemelas.'),
    11: ('¡Sígueme, recluso!', 'Consigue que las gemelas se unan al gran baile.'),
    12: ('No he hecho más que empezar', 'Desbloquea la mayor dificultad (ALL NIGHT).'),
    13: ('Que empiece la fiesta', 'Consigue un atuendo.'),
    14: ('¡He robado la mitad!', 'Consigue la mitad de los atuendos.'),
    15: ('Todo un Phantom Thief', 'Consigue todos los atuendos.'),
    16: ('La herramienta indispensable de todo Phantom Thief', 'Consigue todos los pares de gafas.'),
    17: ('Cantera brillante', 'Consigue la mitad de los accesorios.'),
    18: ('Legendario escondite del tesoro', 'Consigue todos los accesorios.'),
    19: ('¡Sospechoso bajo custodia!', 'No superes una fase.'),
    20: ('¡Que el ritmo no pare!', 'Supera una fase.'),
    21: ('El primer paso hacia la gloria', 'Consigue el mayor grado posible en una fase (KING CRAZY).'),
    22: ('El crimen perfecto', 'Completa una fase en HARD o superior y consigue una puntuación PERFECT en al menos la mitad de las notas.'),
    23: ('Imparable', 'Supera tu mejor puntuación.'),
    24: ('Yo soy vos, ¿quién sois vos?', 'Empieza una fase con un peinado diferente, 2 accesorios, lentillas de colores y una peluca de colores.'),
    25: ('Maestro del disfraz', 'Cambia de atuendo y juega una fase con cada uno de los Phantom Thieves (sin incluir a Akechi).'),
    26: ('Estrellas bailando bajo la luz de las estrellas', 'Entra en Fiebre en 40 bailes distintos.'),
    27: ('La guía definitiva del bromista', 'Ve todos los bailes posibles para el protagonista de P5 (Ren Amamiya).'),
    28: ('Fanático de Alibabá', 'Ve todos los bailes posibles para Futaba.'),
    29: ('El dragón y la pantera', 'Completa las fases en las que Ryuji y Ann bailan juntos.'),
    30: ('La estudiante y el profesor', 'Completa las fases en las que Morgana y Haru bailan juntos.'),
    31: ('El diferente y la estirada', 'Completa las fases en las que Yusuke y Makoto bailan juntos.'),
    32: ('Coreógrafos Phantom', 'Ve una repetición.'),
    33: ('Una montaña de tesoros', 'Desbloquea todos los ??? en Collection.'),
    34: ('Phantom Thieves modernos', 'Registra un atuendo como favorito.'),
    35: ('A tono y listo para la marcha', 'Desbloquea todos los modificadores en Personalizado.'),
    36: ('Siente el furor', 'Completa una fase tras cambiar la dificultad del medidor de Furor en Personalizado.'),
    37: ('Un funambulista con red de seguridad', 'Completa una fase con las opciones "GOOD no interrumpe los combos" y "Fin de la partida al interrumpir un combo" habilitadas.'),
    38: ('Notas traviesas', 'Completa una fase con las opciones "La ruta de las notas se mueve" y "La velocidad de las notas varía durante el tema" habilitadas.'),
    39: ('Ruta de infiltración asegurada', 'Completa una fase en HARD o superior con todos los modificadores de Ayuda habilitados.'),
    40: ('Avance indeciso', 'Completa una fase con 5 modificadores de Desafío y 5 de Ayuda habilitados simultáneamente.'),
    41: ('Una misión imposible', 'Empieza una fase en dificultad ALL NIGHT con 10 o más modificadores de Desafío habilitados.'),
}
TRANSLATIONS = {'es': SPANISH}


def text(trophy, language=None):
    """(name, description) of a trophy in `language` ('es', ...) when there is a translation,
    else in English."""
    _id, _grade, name, description = BY_ID[trophy]
    local = TRANSLATIONS.get((language or '')[:2], {}).get(trophy)
    if local:
        return local[0] or name, local[1] or description
    return name, description


def read_log(path):
    """{id: earliest unlock time} from a trophies.log; broken lines are skipped."""
    unlocked = {}
    try:
        text = Path(path).read_text(encoding='utf-8', errors='replace')
    except OSError:
        return unlocked
    for line in text.splitlines():
        parts = line.split()
        if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
            trophy, when = int(parts[0]), int(parts[1])
            if trophy in BY_ID and (trophy not in unlocked or when < unlocked[trophy]):
                unlocked[trophy] = when
    return unlocked


def trp_files(path):
    """{name: bytes} of the unencrypted entries (the PNG icons) of a trophy00.trp."""
    data = Path(path).read_bytes()
    magic, _version, _size, count, entry_size = struct.unpack_from('>IIQII', data, 0)
    if magic != 0xDCA24D00 or entry_size < 52:
        raise ValueError('not a trophy file')
    files = {}
    for i in range(count):
        at = 0x60 + i * entry_size
        name = data[at:at + 32].split(b'\0')[0].decode('ascii', 'replace')
        offset, size, flags = struct.unpack_from('>QQI', data, at + 32)
        blob = data[offset:offset + size]
        if blob[:4] == b'\x89PNG':
            files[name] = blob
    return files


def icon_name(trophy):
    return f'TROP{trophy:03d}.PNG'


def prepare(game, out, language=None):
    """trophies.txt for the runtime (names in `language` when translated) and the icons, from the
    game's trophy file when it has one."""
    out = Path(out)
    folder = out / 'trophies'
    folder.mkdir(parents=True, exist_ok=True)
    icons = 0
    trp = Path(game) / 'sce_sys' / 'trophy' / 'trophy00.trp'
    try:
        for name, blob in trp_files(trp).items():
            target = folder / name
            if not target.is_file() or target.stat().st_size != len(blob):
                target.write_bytes(blob)
            icons += name.startswith('TROP')
    except (OSError, ValueError, struct.error) as error:
        print(f'Trophies: no icons ({error})')
    lines = [f'{trophy}\t{grade}\t{text(trophy, language)[0]}' for trophy, grade, _name, _text in TROPHIES]
    (out / 'trophies.txt').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'Trophies: {len(TROPHIES)} known, {icons} icons')
    return out / 'trophies.txt', folder


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('game', type=Path)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--language', default=None)
    args = parser.parse_args()
    prepare(args.game, args.out, args.language)
