"""Artículos de objetos según nombres revisados, independientes del jugador.

Los marcadores {art:1:el} consultan el nombre del argumento 1. Solo se
introducen en mensajes cuyo argumento se ha comprobado que es un objeto.
"""
import json
import re
from pathlib import Path
from collections import defaultdict
from revisar import codigos
import rmarshal as rm

ROOT = Path(__file__).resolve().parents[1]
REL = Path('Data/Scripts/001_Technical/003_Intl_Messages.rb')
FEMALE = set('Flauta Miel Cuerda Parte Piedra Pluma Miniseta Seta Perla Sarta Pepita Maxipepita Escama Cola Ánfora Efigie Corona Sal Concha Tarjeta Muda Bola Moneda Cinta Gafas Roca Garra Banda Raíz Hierba Pila Vidasfera Lupa Llamasfera Toxisfera Toxiestrella Pesa Lente Franja Agua Semilla Flecha Arena Cuchara Tabla Gema Diamansfera Lustresfera Griseosfera HidroROM FulgoROM PiroROM CrioROM Mejora Tela Poción Superpoción Hiperpoción Ceniza Cura Galleta Barrita Limonada Leche Proteína Baya Carta Car. Defensa Def. Velocidad Precisión Protección Bici Caña Supercaña Regadera Botas Pieza Punta Patas Tijeras Carretilla Identificación Cerveza Pokédex Llave Pizza Bota Bandera Superincubadora Máscara Pata Aleta Cáps. Cápsula Dinamita Estatuas Esmeralda Medalla Incubadora Mochila Gafa Nerviosfera Fruta Tablilla Piezas Esporas Algas Cosa Wailmegadera'.split())
INHERENT_PLURAL = set('Gafas Restos PP Botas Patas Tijeras Tablones Ladrillos Estatuas Separadores Recuerdos Piezas Esporas Algas'.split())

def load(rel):
    return json.loads((ROOT / rel).read_text(encoding='utf-8'))

def save(rel, data):
    (ROOT / rel).write_text(json.dumps(data, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')

def forms():
    names = load('traduccion/bd/objetos.json')
    plurals = load('traduccion/bd/objetos_plural.json')
    result = {}
    pairs = [(name, plurals.get(en, name)) for en, name in names.items()]
    # English singular and plural keys differ (Oran Berry / Oran Berries).
    # Match them by the game's item index rather than by their spelling.
    for game in ('kanto', 'hoenn'):
        messages = rm.load_messages(str(ROOT / 'repos' / game / 'Data/messages.dat'))
        for en, plural_en in zip(messages[7], messages[8]):
            if en in names and names[en] not in ('objeto_desconocido', 'Objeto desconocido'):
                pairs.append((names[en], plurals.get(plural_en, names[en])))
    for name, plural_name in pairs:
        if not name:
            continue
        head = name.split()[0]
        if re.match(r'^(?:MT|MO)\d+', name):
            plural_name = name
        female = head in FEMALE or bool(re.search(r'\bBalls?\b', name)) or bool(re.match(r'^(?:MT|MO)\d+', name)) or name == 'Poké Flauta'
        mask = int(female) | (2 if head in INHERENT_PLURAL else 0) | (4 if head in ('Agua', 'Ánfora') else 0)
        for value, bits in ((name, mask), (plural_name, mask | 2 if plural_name != name else mask)):
            assert value not in result or result[value] == bits, (value, result.get(value), bits)
            result[value] = bits
    return result

HELPER = r'''
# BEGIN SPANISH ITEM CONCORDANCE
TABLE

def pbResolveItemArticles(text, args)
  return text if !text.is_a?(String)
  return text if !text.include?("{art:")
  return text.gsub(/\{art:(\d+):(el|un|este|del|al|otro)\}/) do
    index, kind = $1.to_i, $2
    name = args[index].to_s
    form = SPANISH_ITEM_FORMS[name] || 0
    female = (form & 1) != 0
    plural = (form & 2) != 0
    stressed_a = (form & 4) != 0 && !plural
    definite = plural ? (female ? "las" : "los") : (female && !stressed_a ? "la" : "el")
    case kind
    when "el"   then definite
    when "un"   then plural ? (female ? "unas" : "unos") : (female && !stressed_a ? "una" : "un")
    when "este" then plural ? (female ? "estas" : "estos") : (female ? "esta" : "este")
    when "otro" then plural ? (female ? "otras" : "otros") : (female ? "otra" : "otro")
    when "del"  then definite == "el" ? "del" : "de " + definite
    when "al"   then definite == "el" ? "al" : "a " + definite
    end
  end
end
# END SPANISH ITEM CONCORDANCE
'''

def article(index, kind='el'):
    return '{art:%d:%s}' % (index, kind)

def translations():
    data = load('traduccion/script.json')
    # Audited item arguments: battle items, pickups, held items, PC, mining, shop.
    indices = {
        '{1} harvested one {2}!': 2, '{1} found one {2}!': 2,
        '{1} frisked the foe and found one {2}!': 2,
        "{1} stole and ate its target's {2}!": 2,
        '{1} found an {2}!': 2, '{1} found a {2}!': 2,
        '{1} threw an {2}!': 2, '{1} threw a {2}!': 2,
        '{1} used an {2}.': 2, '{1} used a {2}.': 2,
        r'\me[{1}]You found an {3}{2}\c[0]!\wtnp[30]': 2,
        r'\me[{1}]You found a {3}{2}\c[0]!\wtnp[30]': 2,
        r'You found an \c[1]{1}\c[0]!\wtnp[30]': 1,
        r'You found a \c[1]{1}\c[0]!\wtnp[30]': 1,
        r'\me[{1}]You obtained an {3}{2}\c[0]!\wtnp[30]': 2,
        r'\me[{1}]You obtained a {3}{2}\c[0]!\wtnp[30]': 2,
        r'Would you like to register the \c[3]{1}\c[0] in the quick actions menu?': 1,
        r'\se[{1}]The \c[3]{2}\c[0] was registered!': 2,
        r'You put the {1} away\nin the <icon=bagPocket{2}>\c[1]{3} Pocket\c[0].': 1,
        '{1} planted a {2} in the soft loamy soil.': 2,
        r'You picked the \c[1]{1}\c[0].\wtnp[10]': 1,
        '{1} put the \\c[1]{2}\\c[0] in the <icon=bagPocket{3}>\\c[1]{4}\\c[0] Pocket.\x01': 2,
        'Want to sprinkle some water with the {1}?': 1,
        'You used an {1}.': 1, 'You used a {1}.': 1,
        '{1} is already holding an {2}.\x01': 2,
        '{1} is already holding a {2}.\x01': 2,
        '{1} is now holding the {2}.': 2,
        'Received the {1} from {2}.': 1,
        "The {1} can't be held.": 1,
        'Turned over the {1} and received ${2}.': 1,
        'What shall I do with this {1}?': 1,
        'Take this {1}?': 1, "Can't store the {1}.": 1, 'Took the {1}.': 1,
        r'One {1} was obtained.\se[Mining item get]\wtnp[30]': 1,
        'You wanna sell me this {1}, is that right?': 1,
        'You gave the {1} to {2}!': 1,
    }
    changes = 0
    for en, index in indices.items():
        assert en in data, en
        es = data[en]
        # Colour codes and other placeholders may sit between article and name.
        pattern = r'\b(el|un|este) (?=(?:\\[cC]\[\d+\]|\{\d+\})*\{' + str(index) + r'\})'
        new = re.sub(pattern, lambda m: article(index, m[1]) + ' ', es)
        assert new != es or '{art:' in es, (en, es)
        assert codigos(en) == codigos(new), en
        changes += new != es
        data[en] = new
    explicit = {
        'Took the {1} from {2} and gave it the {3}.': 'Le quitaste ' + article(1) + ' {1} a {2} y le diste ' + article(3) + ' {3}.',
        'One {1} was found, but you have no room for it.': 'Se encontró ' + article(1, 'un') + ' {1}, pero no hay espacio en la mochila.',
        r'You picked the {1} \c[1]{2}\c[0].\wtnp[10]': r'Recogiste {1} \c[1]{2}\c[0].\wtnp[10]',
        'The {1} has sprouted.': 'La planta de {1} ha brotado.',
        '{1} is selected.': 'Has seleccionado {1}.',
        "{1}'s Taunt wore off!": '¡La Mofa de {1} se pasó!',
        "{1}'s taunt wore off!": '¡La Mofa de {1} se pasó!',
    }
    for en, es in explicit.items():
        assert en in data and codigos(en) == codigos(es), en
        changes += data[en] != es
        data[en] = es
    save('traduccion/script.json', data)
    print(f'{changes} mensajes corregidos; {len(indices) + len(explicit)} plantillas revisadas.')

def apply():
    groups = defaultdict(list)
    for name, bits in sorted(forms().items()):
        groups[bits].append(name)
    table = ['SPANISH_ITEM_FORMS = {}']
    for bits, names in sorted(groups.items()):
        table.append(json.dumps(names, ensure_ascii=False) + f'.each {{ |name| SPANISH_ITEM_FORMS[name] = {bits} }}')
    helper = HELPER.replace('TABLE', '\n'.join(table))
    for game in ('kanto', 'hoenn'):
        path = ROOT / 'repos' / game / REL
        raw = path.read_bytes()
        newline = '\r\n' if b'\r\n' in raw else '\n'
        source = raw.decode('utf-8').replace('\r\n', '\n')
        if '# BEGIN SPANISH ITEM CONCORDANCE' in source:
            source = re.sub(r'\n# BEGIN SPANISH ITEM CONCORDANCE.*?# END SPANISH ITEM CONCORDANCE\n', lambda m: helper, source, flags=re.S)
        else:
            source = source.replace('module MessageTypes\n', helper + '\nmodule MessageTypes\n', 1)
        # Both script and map messages format arguments through these functions.
        for start, end in (('def _INTL(*arg)', 'def _ISPRINTF'), ('def _MAPINTL(mapid, *arg)', 'def _MAPISPRINTF')):
            begin = source.index(start)
            finish = source.index(end, begin) if end else len(source)
            chunk = source[begin:finish]
            old = '  string = string.clone\n'
            new = '  string = pbResolveItemArticles(string.clone, arg)\n'
            if new not in chunk:
                assert chunk.count(old) == 1, start
                source = source[:begin] + chunk.replace(old, new) + source[finish:]
        result = source.replace('\n', newline).encode('utf-8')
        if result != raw:
            path.write_bytes(result)
    print(f'{len(forms())} formas de objetos con género y número.')

if __name__ == '__main__':
    translations()
    apply()
