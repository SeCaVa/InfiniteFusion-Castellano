"""Lectura y escritura de Ruby Marshal 4.8, lo justo para los .dat de mensajes
de Pokémon Essentials (Pokémon Infinite Fusion).

Estructura de messages.dat (ver Data/Scripts/001_Technical/003_Intl_Messages.rb):
  [ [OrderedHash por mapa (0 = eventos comunes)], lista Species, lista Kinds, ... ]
  - Secciones "lista": Array de String indexado por id (vacío = usa el inglés).
  - Secciones "hash": OrderedHash {clave normalizada del inglés => traducción}.
  - OrderedHash se vuelca con _dump: Marshal.dump([claves, valores]) (tipo 'u').
  - messages.dat va cifrado con XOR (Encryption.xor); el juego acepta también
    archivos sin cifrar (así va french.dat).

Uso:
  from rmarshal import load_messages, dump_messages, OrderedHash
"""
import struct

ENCRYPTION_KEY = bytes([0x4A, 0x8F, 0x2C, 0xE1, 0x73, 0xB5, 0x96, 0x0D,
                        0x5E, 0xA2, 0x3F, 0xC7, 0x81, 0x14, 0x6B, 0xD9])


def xor(data: bytes) -> bytes:
    import numpy as np
    a = np.frombuffer(data, dtype=np.uint8)
    k = np.resize(np.frombuffer(ENCRYPTION_KEY, dtype=np.uint8), len(a))
    return (a ^ k).tobytes()


class OrderedHash(dict):
    """dict ordenado que se vuelca como el OrderedHash de Essentials."""


class RObj:
    def __init__(self, cls):
        self.cls = cls
        self.attrs = {}
        self.data = None

    def __repr__(self):
        return f"<{self.cls}>"


# ---------------------------------------------------------------- lectura

class _Reader:
    def __init__(self, b):
        self.b = b
        self.i = 0
        self.syms = []
        self.objs = []

    def byte(self):
        v = self.b[self.i]
        self.i += 1
        return v

    def long(self):
        c = struct.unpack('b', bytes([self.byte()]))[0]
        if c == 0:
            return 0
        if 5 <= c <= 127:
            return c - 5
        if -128 <= c <= -5:
            return c + 5
        if c > 0:
            v = 0
            for k in range(c):
                v |= self.byte() << (8 * k)
            return v
        c = -c
        v = 0
        for k in range(c):
            v |= self.byte() << (8 * k)
        return v - (1 << (8 * c))

    def raw(self):
        n = self.long()
        s = self.b[self.i:self.i + n]
        self.i += n
        return s

    def sym(self):
        t = chr(self.byte())
        if t == ':':
            s = self.raw().decode('utf-8', 'replace')
            self.syms.append(s)
            return s
        if t == ';':
            return self.syms[self.long()]
        raise ValueError(f"se esperaba símbolo, hay {t!r} en {self.i}")

    def read(self):
        t = chr(self.byte())
        if t == '0':
            return None
        if t == 'T':
            return True
        if t == 'F':
            return False
        if t == 'i':
            return self.long()
        if t in ':;':
            self.i -= 1
            return self.sym()
        if t == '@':
            return self.objs[self.long()]
        if t == 'I':
            o = self.read()
            for _ in range(self.long()):
                self.sym()
                self.read()
            return o
        if t == '"':
            s = self.raw().decode('utf-8', 'replace')
            self.objs.append(s)
            return s
        if t == '[':
            a = []
            self.objs.append(a)
            for _ in range(self.long()):
                a.append(self.read())
            return a
        if t in '{}':
            h = {}
            self.objs.append(h)
            for _ in range(self.long()):
                k = self.read()
                if isinstance(k, list):       # claves compuestas (p. ej. trainers.dat)
                    k = tuple(k)
                h[k] = self.read()
            if t == '}':
                self.read()
            return h
        if t == 'u':
            cls = self.sym()
            data = self.raw()
            if cls == 'OrderedHash':
                r = _Reader(data)
                r.i = 2
                keys, values = r.read()
                o = OrderedHash(zip(keys, values))
            else:
                o = RObj(cls)
                o.data = data
            self.objs.append(o)
            return o
        if t == 'o':
            cls = self.sym()
            o = RObj(cls)
            self.objs.append(o)
            for _ in range(self.long()):
                k = self.sym()
                o.attrs[k] = self.read()
            return o
        if t == 'f':
            s = self.raw().decode()
            self.objs.append(s)
            return s
        if t == 'l':
            sign = chr(self.byte())
            n = self.long()
            d = self.b[self.i:self.i + 2 * n]
            self.i += 2 * n
            v = int.from_bytes(d, 'little')
            v = -v if sign == '-' else v
            self.objs.append(v)
            return v
        if t == 'C':
            self.sym()
            return self.read()
        if t == 'e':
            self.sym()
            return self.read()
        raise ValueError(f"tipo Marshal no soportado {t!r} en {self.i}")


def loads(b: bytes):
    if b[:2] != b'\x04\x08':
        raise ValueError("no es Ruby Marshal 4.8")
    r = _Reader(b)
    r.i = 2
    return r.read()


def load_messages(path):
    """Carga un .dat de mensajes, cifrado o no."""
    raw = open(path, 'rb').read()
    if raw[:2] != b'\x04\x08':
        raw = xor(raw)
    return loads(raw)


# --------------------------------------------------------------- escritura

class _Writer:
    def __init__(self):
        self.out = bytearray()
        self.syms = {}

    def long(self, v):
        o = self.out
        if v == 0:
            o.append(0)
        elif 0 < v < 123:
            o.append(v + 5)
        elif -124 < v < 0:
            o.append((v - 5) & 0xff)
        else:
            n = 0
            x = v
            bs = bytearray()
            for _ in range(4):
                bs.append(x & 0xff)
                x >>= 8
                n += 1
                if (v >= 0 and x == 0) or (v < 0 and x == -1):
                    break
            o.append(n if v >= 0 else (256 - n))
            o.extend(bs)

    def sym(self, s):
        if s in self.syms:
            self.out.append(ord(';'))
            self.long(self.syms[s])
        else:
            self.syms[s] = len(self.syms)
            b = s.encode('utf-8')
            self.out.append(ord(':'))
            self.long(len(b))
            self.out.extend(b)

    def write(self, v):
        o = self.out
        if v is None:
            o.append(ord('0'))
        elif v is True:
            o.append(ord('T'))
        elif v is False:
            o.append(ord('F'))
        elif isinstance(v, int):
            if not (-2**30 <= v < 2**30):
                raise ValueError("entero demasiado grande")
            o.append(ord('i'))
            self.long(v)
        elif isinstance(v, str):
            b = v.encode('utf-8')
            o.append(ord('I'))
            o.append(ord('"'))
            self.long(len(b))
            o.extend(b)
            self.long(1)
            self.sym('E')
            o.append(ord('T'))
        elif isinstance(v, OrderedHash):
            # Como Ruby: datos de _dump y después la variable @keys del objeto
            inner = dumps([list(v.keys()), list(v.values())])
            o.append(ord('I'))
            o.append(ord('u'))
            self.sym('OrderedHash')
            self.long(len(inner))
            o.extend(inner)
            self.long(1)
            self.sym('@keys')
            self.write(list(v.keys()))
        elif isinstance(v, (list, tuple)):
            o.append(ord('['))
            self.long(len(v))
            for x in v:
                self.write(x)
        elif isinstance(v, dict):
            o.append(ord('{'))
            self.long(len(v))
            for k, x in v.items():
                self.write(k)
                self.write(x)
        else:
            raise TypeError(f"tipo no soportado: {type(v)}")


def dumps(v) -> bytes:
    w = _Writer()
    w.out.extend(b'\x04\x08')
    w.write(v)
    return bytes(w.out)


def dump_messages(messages, path, encrypt=False):
    b = dumps(messages)
    if encrypt:
        b = xor(b)
    open(path, 'wb').write(b)


# ------------------------------------------------ utilidades de Essentials

import re as _re


def string_to_key(s):
    """Messages.stringToKey: la clave con la que el juego busca un texto."""
    if s and _re.search(r'[\r\n\t\x01]|^\s+|\s+$|\s{2,}', s):
        s = _re.sub(r'^\s+', '', s)
        s = _re.sub(r'\s+$', '', s)
        s = _re.sub(r'\s{2,}', ' ', s)
    return s


# Índices de MessageTypes
SECCIONES = {
    1: 'Species', 2: 'Kinds', 3: 'Entries', 4: 'FormNames', 5: 'Moves',
    6: 'MoveDescriptions', 7: 'Items', 8: 'ItemPlurals', 9: 'ItemDescriptions',
    10: 'Abilities', 11: 'AbilityDescs', 12: 'Types', 13: 'TrainerTypes',
    14: 'TrainerNames', 15: 'BeginSpeech', 16: 'EndSpeechWin',
    17: 'EndSpeechLose', 18: 'RegionNames', 19: 'PlaceNames',
    20: 'PlaceDescriptions', 21: 'MapNames', 22: 'PhoneMessages',
    23: 'TrainerLoseText', 24: 'ScriptTexts', 25: 'RibbonNames',
    26: 'RibbonDescriptions', 27: 'TrainerInfoText', 28: 'OutfitTexts',
    35: 'ContestMoveEffects', 45: 'BerryDexDescriptions', 46: 'BerryFirmness',
}
