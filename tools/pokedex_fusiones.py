"""Inventario, lotes y aplicación de traducciones revisadas de la Pokédex.

El material de trabajo queda en traduccion/_pokedex; únicamente los textos
revisados se guardan en traduccion/pokedex/fusiones.json. No cambia dex.json
ni sus autores. Los lotes conservan el original y las pistas terminológicas.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / 'traduccion/_pokedex'
DEST = ROOT / 'traduccion/pokedex/fusiones.json'
sys.path.insert(0, str(ROOT / 'tools'))
from revision_ia import terminos_oficiales
from revisar import codigos

def read(path, default=None):
    return json.loads(path.read_text(encoding='utf-8')) if path.exists() else default

def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=1) + '\n', encoding='utf-8', newline='\n')

def key(text):
    return re.sub(r'\s+', ' ', text).strip()

def inventory():
    records = {}
    counts = {}
    for game in ('kanto', 'hoenn'):
        source = ROOT / 'repos' / game / 'Data/pokedex/dex.json'
        data = read(source)
        counts[game] = {'records': len(data), 'sha256': hashlib.sha256(source.read_bytes()).hexdigest()}
        for row in data:
            en = key(row['entry'])
            if en not in records:
                records[en] = {'en': en, 'sprites': []}
            if row['sprite'] not in records[en]['sprites']:
                records[en]['sprites'].append(row['sprite'])
    values = list(records.values())
    for i, row in enumerate(values):
        row['id'] = i
    write(WORK / 'inventory.json', values)
    write(WORK / 'sources.json', counts)
    print(f'{len(values)} textos distintos de fusiones, identificadores y autores originales intactos.')

def batches(size):
    values = read(WORK / 'inventory.json')
    reviewed = read(DEST, {})
    remaining = [row for row in values if not reviewed.get(row['en'])]
    rx, terms = terminos_oficiales()
    dest = WORK / 'lotes'
    dest.mkdir(parents=True, exist_ok=True)
    pending_batches = 0
    # Stable IDs and batch numbers keep interrupted work resumable.
    for offset in range(0, len(values), size):
        number = offset // size
        sources = values[offset:offset + size]
        if all(reviewed.get(row['en']) for row in sources):
            continue
        pending_batches += 1
        rows = []
        for source in sources:
            row = dict(source)
            row['terminos'] = {m.group(1): terms[m.group(1)] for m in rx.finditer(row['en'])}
            rows.append(row)
        path = dest / f'{number:04d}.json'
        if path.exists() and read(path) != rows:
            raise ValueError('No se sobrescribe un lote distinto. Archivar los lotes anteriores antes de preparar otra tanda.')
        write(path, rows)
    print(f'{len(remaining)} pendientes; {pending_batches} lotes estables de hasta {size}.')

def import_reviewed(batch, response):
    source = read(WORK / 'lotes' / f'{batch:04d}.json')
    proposals = [json.loads(line) for line in Path(response).read_text(encoding='utf-8').splitlines() if line.strip()]
    by_id = {row['id']: row for row in source}
    assert len(proposals) == len(source), 'Respuesta incompleta'
    assert len({row['id'] for row in proposals}) == len(source), 'Identificadores repetidos'
    assert {row['id'] for row in proposals} == set(by_id), 'Identificadores incorrectos'
    result = read(DEST, {})
    for proposal in proposals:
        en = by_id[proposal['id']]['en']
        es = proposal['es']
        assert isinstance(es, str) and es.strip() and es != en
        assert codigos(en) == codigos(es), f'Códigos alterados: {proposal["id"]}'
        assert en.count('POKENAME') == es.count('POKENAME'), f'POKENAME alterado: {proposal["id"]}'
        assert not re.search(r'[\u0000-\u0008\u000b\u000c\u000e-\u001f]', es)
        result[en] = key(es)
    write(DEST, result)
    values = read(WORK / 'inventory.json', [])
    pending = [row['id'] for row in values if not result.get(row['en'])]
    write(WORK / 'progreso.json', {
        'total': len(values), 'revisadas': len(result), 'pendientes': len(pending),
        'siguiente_id': min(pending) if pending else None,
        'ultimo_lote_importado': batch,
        'respuesta_revisada': str(Path(response).relative_to(ROOT)) if Path(response).is_absolute() else str(response),
        'sha256_respuesta': hashlib.sha256(Path(response).read_bytes()).hexdigest(),
        'publicado': False,
    })
    print(f'{len(proposals)} textos revisados importados; {len(result)} traducciones de fusiones disponibles.')

def model_input(batch, size):
    """Prepare translation-only input, with no authors or project metadata."""
    if size <= 0:
        raise ValueError('El tamaño debe ser positivo')
    source = read(WORK / 'lotes' / f'{batch:04d}.json')
    items = read(ROOT / 'traduccion/bd/objetos.json', {})
    berries = {en[:-6]: es for en, es in items.items() if en.endswith(' Berry') and es}
    _, official = terminos_oficiales()
    compound = [en for en in official if ' ' in en or '-' in en]
    plurals = re.compile(r'\b(' + '|'.join(re.escape(en) for en in sorted(compound, key=len, reverse=True)) + r')(?:s|es)\b')
    outputs = []
    for offset in range(0, len(source), size):
        values = []
        for row in source[offset:offset + size]:
            hints = dict(row['terminos'])
            for match in plurals.finditer(row['en']):
                hints[match.group()] = official[match.group(1)]
            for stem, es in berries.items():
                for match in re.finditer(r'\b' + re.escape(stem) + r' berr(?:y|ies)\b', row['en'], re.I):
                    hints[match.group()] = es
            values.append({'id': row['id'], 'en': row['en'], 'terminos': hints})
        path = WORK / 'lotes' / f'{batch:04d}_modelo_{offset // size}.json'
        write(path, values)
        outputs.append(str(path.relative_to(ROOT)))
    print('\n'.join(outputs))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('inventario')
    batch = sub.add_parser('lotes')
    batch.add_argument('--size', type=int, default=160)
    imp = sub.add_parser('importar')
    imp.add_argument('batch', type=int)
    imp.add_argument('response')
    imp.add_argument('--revisado', action='store_true', required=True)
    model = sub.add_parser('preparar', help='Entrada de traducción sin autores, con nombres oficiales de bayas')
    model.add_argument('batch', type=int)
    model.add_argument('--size', type=int, default=160)
    args = parser.parse_args()
    if args.command == 'inventario': inventory()
    elif args.command == 'lotes': batches(args.size)
    elif args.command == 'preparar': model_input(args.batch, args.size)
    else: import_reviewed(args.batch, args.response)
