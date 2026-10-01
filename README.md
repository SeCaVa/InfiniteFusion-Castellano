# Pokémon Infinite Fusion en castellano

Traducción no oficial al castellano (España) de **Pokémon Infinite Fusion**: el juego de Kanto y el de Hoenn.

Incluye todos los textos del juego: diálogos, menús, objetos, movimientos, habilidades, Pokédex, entrenadores, ropa y lugares. También traduce las imágenes que llevan texto en inglés, como las etiquetas de tipo, los estados, los botones de combate y la Ficha de Entrenador.

Usa los nombres oficiales españoles más recientes, sacados de PokeAPI, WikiDex y PkParaíso. Los nombres propios de Hoenn siguen Pokémon Rubí.

> Estado: los textos están traducidos casi al 100 %, pero aún no se ha probado a fondo en partida. Si encuentras errores, abre una *issue*.

## Versiones

| Juego | Versión | Carpeta |
|---|---|---|
| Infinite Fusion (Kanto) | 6.8.2 | `kanto/` |
| Infinite Fusion: Hoenn | 1.2.2 | `hoenn/` |

Cada carpeta lleva archivos de código modificados del juego. Con otra versión pueden no funcionar.

## Instalación

1. Haz una copia de seguridad de la carpeta del juego.
2. Copia el contenido de `kanto/` (o de `hoenn/`) dentro de la carpeta del juego y acepta reemplazar los archivos.
3. Abre el juego y elige **Español** en el selector de idioma.

Cada carpeta contiene:

- `Data/spanish.dat`: todos los textos.
- `Data/Scripts/...`: cambios de código.
  - Activa el idioma español.
  - Elige el género gramatical según el del jugador.
  - Encaja los nombres largos en los menús de ancho fijo.
- `Graphics/Localized/es/...`: imágenes con texto en castellano. El juego las usa solo cuando el idioma es español.

## Regenerar la traducción

Los textos están en `traduccion/` como diccionarios JSON `{"inglés": "español"}`.

| Carpeta o archivo | Contenido |
|---|---|
| `bd/` | Datos del juego: Pokémon, movimientos, objetos, habilidades… |
| `dialogos/` | Diálogos, por mapa y por juego. |
| `entrenadores/` | Clases, nombres y frases de entrenadores. |
| `lugares/` | Mapas y lugares. |
| `script.json`, `ropa.json`, `telefono.json` | Textos del código, ropa y llamadas. |
| `_personajes.json`, `_sustituciones.json` | Nombres de personajes y sustituciones globales. |

Un archivo `<nombre>_<juego>.json` (por ejemplo `entrenadores/nombres_hoenn.json`) solo se aplica a ese juego.

Las herramientas de `tools/` (Python 3 y Pillow) esperan los repositorios originales del juego en `repos/kanto` y `repos/hoenn`:

```sh
sh aplicar.sh                  # extrae cadenas nuevas, aplica nombres oficiales y genera los spanish.dat
python tools/generar_dat.py    # solo genera los spanish.dat
```

`glosario.md` recoge los términos y las decisiones de traducción.

## Créditos

- **Pokémon Infinite Fusion**: Frogman, chardub y el resto del equipo de Infinite Fusion ([Kanto](https://github.com/infinitefusion/infinitefusion-e18), [Hoenn](https://github.com/infinitefusion/infinitefusion-hoenn-public)).
- **Traducción base**: el `Data/spanish.dat` sin acreditar incluido en el repositorio de Hoenn (rama `releases`). Sirvió de punto de partida y se revisó entero.
- Nombres oficiales: [PokeAPI](https://pokeapi.co/), [WikiDex](https://www.wikidex.net/) y [PkParaíso](https://www.pkparaiso.com/).
- Pokémon y todos sus nombres son marcas de Nintendo, Creatures Inc. y GAME FREAK inc. Proyecto de fans sin ánimo de lucro.
