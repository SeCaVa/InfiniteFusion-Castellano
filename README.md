# Pokémon Infinite Fusion en castellano

Traducción no oficial al castellano (España) de **Pokémon Infinite Fusion**: el juego de Kanto y el de Hoenn.

Traduce diálogos, menús, objetos, movimientos, habilidades, descripciones de Pokémon base, entrenadores, ropa y lugares. Las descripciones propias de fusiones se incorporan por tandas revisadas. También traduce imágenes con texto, como etiquetas de tipo, estados, botones de combate y la Ficha de Entrenador.

Usa los nombres oficiales españoles más recientes, sacados de PokeAPI, WikiDex y PkParaíso. Los nombres propios de Hoenn siguen Pokémon Rubí.

> Estado: 960 de los 66.093 textos distintos de fusiones de las versiones actuales de Kanto y Hoenn están revisados (1,45 %). Las entradas pendientes muestran el original. Los textos del resto del juego están ampliamente traducidos y continúan en revisión. Si encuentras errores, abre una *issue*.

## Versiones

| Juego | Versión | Carpeta |
|---|---|---|
| Infinite Fusion (Kanto) | 6.8.2 | `kanto/` |
| Infinite Fusion: Hoenn | 1.2.2 | `hoenn/` |

Cada carpeta lleva archivos de código modificados del juego. Con otra versión pueden no funcionar.

## Instalación

También puedes usar el **lanzador en castellano** de [Releases](https://github.com/SeCaVa/InfiniteFusion-Castellano/releases). Descarga `PokemonInfiniteFusion-Launcher_1.1-Castellano.exe`, elige Kanto o Hoenn y una carpeta. Instala la base oficial y aplica la traducción de esta rama; al actualizar vuelve a aplicarla. Los botones conservan sus sprites y su fuente originales con rótulos españoles. Dentro del juego, elige **Español**.

Las fuentes del lanzador y las instrucciones para recompilar están en [`launcher/`](launcher/README.md). El ejecutable se distribuye como adjunto de una release.

1. Haz una copia de seguridad de la carpeta del juego.
2. Copia el contenido de `kanto/` (o de `hoenn/`) dentro de la carpeta del juego y acepta reemplazar los archivos.
3. Abre el juego y elige **Español** en el selector de idioma.

Cada carpeta contiene:

- `Data/spanish.dat`: textos traducidos y revisados disponibles.
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
| `pokedex/fusiones.json` | Descripciones de fusiones revisadas, sin modificar las entradas originales ni sus autores. |
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
