"""Extrae los textos traducibles de Pokémon Infinite Fusion (Kanto y Hoenn) y
los fusiona con los diccionarios de traduccion/ sin borrar nada ya traducido.

Fuentes:
  - repos/<juego>/Data/messages.dat  (diálogos de mapas, base de datos, entrenadores…)
  - _INTL/_ISPRINTF de repos/scripts, repos/kanto/Data/Scripts y repos/hoenn/Data/Scripts
  - Data/outfits/*.json de cada juego (ropa, peinados y gorros)

Diccionarios (formato {original: traducción}; "" = sin traducir):
  traduccion/bd/*.json           secciones de la base de datos, comunes a los dos juegos
  traduccion/script.json         textos del código (_INTL)
  traduccion/dialogos/comun.json cadenas que salen en 2 o más mapas
  traduccion/dialogos/<juego>/MapNNN.json  cadenas de un solo mapa
  traduccion/dialogos/<juego>/_indice.json nombre y número de cadenas de cada mapa

Informes en traduccion/_informes/.

Uso: PYTHONIOENCODING=utf-8 python tools/extraer.py
"""
import json
import os
import re
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(__file__))
import rmarshal as rm

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
REPOS = os.path.join(RAIZ, 'repos')
TRAD = os.path.join(RAIZ, 'traduccion')
JUEGOS = ['kanto', 'hoenn']

# Sección de messages.dat -> archivo de diccionario
ARCHIVOS_SECCION = {
    1: 'bd/especies', 2: 'bd/categorias', 3: 'bd/pokedex', 4: 'bd/formas',
    5: 'bd/movimientos', 6: 'bd/movimientos_desc', 7: 'bd/objetos',
    8: 'bd/objetos_plural', 9: 'bd/objetos_desc', 10: 'bd/habilidades',
    11: 'bd/habilidades_desc', 12: 'bd/tipos', 13: 'bd/clases_entrenador',
    14: 'entrenadores/nombres', 15: 'entrenadores/frases',
    16: 'entrenadores/frases', 17: 'entrenadores/frases', 23: 'entrenadores/frases',
    27: 'entrenadores/frases', 18: 'lugares/regiones', 19: 'lugares/lugares',
    20: 'lugares/lugares_desc', 21: 'lugares/mapas', 22: 'telefono',
    24: 'script', 25: 'bd/cintas', 26: 'bd/cintas_desc', 28: 'ropa',
    # secciones añadidas por complementos (concursos y bayas de Hoenn)
    35: 'bd/concursos_efectos', 45: 'bd/bayas_desc', 46: 'bd/bayas_firmeza',
}


# ------------------------------------------------------------ utilidades

def cargar_json(ruta):
    ruta = os.path.join(TRAD, ruta + '.json') if not ruta.endswith('.json') else ruta
    if os.path.exists(ruta):
        with open(ruta, encoding='utf-8') as f:
            return json.load(f)
    return {}


def guardar_json(ruta, datos):
    ruta = os.path.join(TRAD, ruta + '.json') if not ruta.endswith('.json') else ruta
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(datos, f, ensure_ascii=False, indent=1)
        f.write('\n')


def fusionar(ruta, claves):
    """Añade las claves nuevas con "" y conserva lo ya traducido.
    Devuelve (nuevas, obsoletas)."""
    existente = cargar_json(ruta)
    nuevo = {}
    nuevas = 0
    for k in claves:
        if k in existente:
            nuevo[k] = existente[k]
        else:
            nuevo[k] = ''
            nuevas += 1
    obsoletas = [k for k in existente if k not in nuevo]
    for k in obsoletas:            # se conservan al final; revisar.py las lista
        nuevo[k] = existente[k]
    guardar_json(ruta, nuevo)
    return nuevas, obsoletas


def textos_seccion(sec):
    if isinstance(sec, dict):
        return list(sec.keys())
    if isinstance(sec, list):
        return [s for s in sec if isinstance(s, str) and s]
    return []


# ------------------------------------------- cadenas _INTL de los scripts

ESCAPES = {'n': '\n', 't': '\t', 'r': '\r', 's': ' ', '0': '\0', 'e': '\x1b',
           'a': '\a', 'b': '\b', 'f': '\f', 'v': '\v'}
RE_LLAMADA = re.compile(r'\b(_INTL|_ISPRINTF)\s*\(\s*')


def leer_literal(src, i):
    """Lee un literal de Ruby en src[i:]. Devuelve (valor, fin, interpolado)
    o None si no hay literal."""
    q = src[i] if i < len(src) else ''
    if q not in '"\'':
        return None
    i += 1
    out = []
    interp = False
    while i < len(src):
        c = src[i]
        if c == q:
            return ''.join(out), i + 1, interp
        if c == '\\':
            n = src[i + 1]
            if q == "'":
                out.append(n if n in "'\\" else '\\' + n)
                i += 2
                continue
            if n in ESCAPES:
                out.append(ESCAPES[n])
                i += 2
            elif n == 'u':
                m = re.match(r'u\{([0-9a-fA-F ]+)\}|u([0-9a-fA-F]{4})', src[i + 1:])
                if m:
                    cps = (m.group(1) or m.group(2)).split()
                    out.append(''.join(chr(int(x, 16)) for x in cps))
                    i += 1 + m.end()
                else:
                    out.append('u')
                    i += 2
            elif n in '01234567':
                m = re.match(r'[0-7]{1,3}', src[i + 1:])
                out.append(chr(int(m.group(0), 8)))
                i += 1 + m.end()
            elif n == 'x':
                m = re.match(r'x([0-9a-fA-F]{1,2})', src[i + 1:])
                out.append(chr(int(m.group(1), 16)))
                i += 1 + m.end()
            elif n == '\n':
                i += 2
            else:
                out.append(n)
                i += 2
            continue
        if q == '"' and c == '#' and src[i + 1:i + 2] == '{':
            interp = True
            prof = 0
            j = i + 1
            while j < len(src):
                if src[j] == '{':
                    prof += 1
                elif src[j] == '}':
                    prof -= 1
                    if prof == 0:
                        break
                j += 1
            out.append(src[i:j + 1])
            i = j + 1
            continue
        out.append(c)
        i += 1
    return None


def extraer_scripts(carpetas):
    """{clave: [archivo:línea, ...]} y lista de avisos (interpolaciones, concatenaciones)."""
    textos = {}
    avisos = []
    for carpeta in carpetas:
        for dirpath, _, files in os.walk(carpeta):
            for fn in sorted(files):
                if not fn.endswith('.rb'):
                    continue
                ruta = os.path.join(dirpath, fn)
                rel = os.path.relpath(ruta, REPOS).replace('\\', '/')
                src = open(ruta, encoding='utf-8', errors='replace').read()
                for m in RE_LLAMADA.finditer(src):
                    linea = src.count('\n', 0, m.start()) + 1
                    lit = leer_literal(src, m.end())
                    if not lit:
                        avisos.append(f'SIN LITERAL  {rel}:{linea}  {src[m.start():m.start() + 70]!r}')
                        continue
                    valor, fin, interp = lit
                    resto = src[fin:fin + 40].lstrip(' \t')
                    if resto.startswith('+') or resto.startswith('\\\n') or resto[:1] in '"\'':
                        avisos.append(f'CONCATENADO  {rel}:{linea}  {valor[:60]!r}')
                    if interp:
                        avisos.append(f'INTERPOLADO  {rel}:{linea}  {valor[:80]!r}')
                        continue
                    if not valor.strip():
                        continue
                    clave = rm.string_to_key(valor)
                    textos.setdefault(clave, [])
                    if len(textos[clave]) < 3:
                        textos[clave].append(f'{rel}:{linea}')
    return textos, avisos


# ------------------------------------------------------------ principal

def main():
    informes = os.path.join(TRAD, '_informes')
    os.makedirs(informes, exist_ok=True)
    resumen = []

    mensajes = {}
    for j in JUEGOS:
        ruta = os.path.join(REPOS, j, 'Data', 'messages.dat')
        print(f'Cargando {ruta}…', flush=True)
        mensajes[j] = rm.load_messages(ruta)

    # --- secciones de la base de datos y demás (comunes a los dos juegos)
    por_archivo = defaultdict(list)
    for sec, archivo in ARCHIVOS_SECCION.items():
        if sec == 24:
            continue          # los textos del código salen de los scripts
        for j in JUEGOS:
            m = mensajes[j]
            if sec < len(m):
                for t in textos_seccion(m[sec]):
                    if t not in por_archivo[archivo]:
                        por_archivo[archivo].append(t)

    # --- ropa: también desde los JSON (el juego los añade a OutfitTexts)
    for j in JUEGOS:
        carpeta = os.path.join(REPOS, j, 'Data', 'outfits')
        if os.path.isdir(carpeta):
            for fn in sorted(os.listdir(carpeta)):
                if fn.endswith('.json'):
                    for e in json.load(open(os.path.join(carpeta, fn), encoding='utf-8')):
                        for campo in ('name', 'description'):
                            t = e.get(campo)
                            if isinstance(t, str) and t and t not in por_archivo['ropa']:
                                por_archivo['ropa'].append(t)

    # --- textos del código
    carpetas = [os.path.join(REPOS, 'scripts')] + \
        [os.path.join(REPOS, j, 'Data', 'Scripts') for j in JUEGOS]
    scr, avisos = extraer_scripts(carpetas)
    claves_script = list(scr.keys())
    for j in JUEGOS:        # y los que solo están en messages.dat (scripts antiguos)
        m = mensajes[j]
        for t in textos_seccion(m[24]):
            if t not in scr:
                claves_script.append(t)
                scr[t] = ['messages.dat']
    por_archivo['script'] = claves_script
    guardar_json(os.path.join(informes, 'script_origen.json'), scr)
    with open(os.path.join(informes, 'script_avisos.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(avisos) + '\n')

    for archivo, claves in sorted(por_archivo.items()):
        nuevas, obs = fusionar(archivo, claves)
        resumen.append(f'{archivo:28} {len(claves):6} cadenas  +{nuevas} nuevas  {len(obs)} obsoletas')

    # --- diálogos de mapas
    uso = defaultdict(set)            # cadena -> {(juego, mapa)}
    for j in JUEGOS:
        for mid, oh in enumerate(mensajes[j][0] or []):
            if isinstance(oh, dict):
                for k in oh:
                    uso[k].add((j, mid))
    comunes = [k for k, v in uso.items() if len(v) > 1]
    nuevas, obs = fusionar('dialogos/comun', comunes)
    resumen.append(f'{"dialogos/comun":28} {len(comunes):6} cadenas  +{nuevas} nuevas  {len(obs)} obsoletas')
    comunes = set(comunes)
    for j in JUEGOS:
        m = mensajes[j]
        nombres = m[21] if isinstance(m[21], list) else []
        indice = {}
        total = 0
        for mid, oh in enumerate(m[0] or []):
            if not isinstance(oh, dict) or not oh:
                continue
            propias = [k for k in oh if k not in comunes]
            nombre = nombres[mid] if mid < len(nombres) and nombres[mid] else ''
            indice[f'Map{mid:03d}'] = {'nombre': nombre, 'propias': len(propias),
                                       'comunes': len(oh) - len(propias)}
            if propias:
                fusionar(f'dialogos/{j}/Map{mid:03d}', propias)
                total += len(propias)
        guardar_json(f'dialogos/{j}/_indice', indice)
        resumen.append(f'{"dialogos/" + j:28} {total:6} cadenas en {len(indice)} mapas')

    resumen.append(f'avisos de scripts: {len(avisos)} (traduccion/_informes/script_avisos.txt)')
    with open(os.path.join(informes, 'extraccion.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(resumen) + '\n')
    print('\n'.join(resumen))


if __name__ == '__main__':
    main()
