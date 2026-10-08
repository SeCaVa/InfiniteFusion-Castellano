# Pokémon Infinite Fusion en castellano

Traducción no oficial al castellano (España) de **Pokémon Infinite Fusion**: el juego de Kanto y el de Hoenn.

Traduce diálogos, menús, objetos, movimientos, habilidades, descripciones de Pokémon base, entrenadores, ropa y lugares. Las descripciones propias de fusiones se incorporan por tandas revisadas. También traduce imágenes con texto, como etiquetas de tipo, estados, botones de combate y la Ficha de Entrenador.

Usa los nombres oficiales españoles más recientes, sacados de PokeAPI, WikiDex y PkParaíso. Los nombres propios de Hoenn siguen Pokémon Rubí.

> Estado: los 79.771 textos distintos de la Pokédex de fusiones están traducidos y revisados (entradas de la comunidad del 6 de octubre de 2026, fijadas el 8 de octubre de 2026). Los textos del resto del juego están ampliamente traducidos y continúan en revisión. Si encuentras errores, abre una *issue*.

## Cambios recientes

- 8 de octubre de 2026: versión congelada. El lanzador instala siempre la versión del juego base para la que está hecha la traducción (Kanto 6.8.2 y Hoenn 1.2.2) y, con el juego en español, los mensajes de inicio y enlaces del menú que se descargan al arrancar quedan fijados a los del 30 de septiembre de 2026, todos traducidos.
- 8 de octubre de 2026: la Pokédex de fusiones queda fijada a la versión traducida. Con el juego en español se descargan las entradas de la comunidad del 6 de octubre de 2026 (commit `86aa014` de [pokedex-entries](https://github.com/infinitefusion/pokedex-entries)), así que no aparecen entradas nuevas sin traducir. En los demás idiomas el juego sigue descargando la versión más reciente. Las entradas posteriores se incorporarán por tandas.
- 13.678 descripciones de fusiones más (79.771 en total), «Piedra Espíritu» unificada en las fusiones de Spiritomb y «Archi7» en la descripción del Pase Seagallop.
- Las entradas automáticas de las fusiones se componen con las descripciones españolas de sus especies base.
- Rótulos «Nv.» y «PS» en castellano, y el icono de estado de combate ya no se corta (veneno grave incluido).
- Pokédex de fusiones completa: 66.093 descripciones revisadas, con los marcadores de nombres y los autores originales conservados. Las descripciones largas se reparten en páginas.
- Traducciones de textos del museo, medallas, registro de misiones, peluquería y selector de sprites de evolución.
- Ajustes del panel de descripciones de las tiendas, las mayúsculas acentuadas y los signos que no incluyen las fuentes del juego.
- Traducción de los tipos de Pokémon insertados en diálogos y correcciones de los rótulos de precios.

## Versiones

| Juego | Versión | Carpeta |
|---|---|---|
| Infinite Fusion (Kanto) | 6.8.2 | `kanto/` |
| Infinite Fusion: Hoenn | 1.2.2 | `hoenn/` |

Cada carpeta lleva archivos de código modificados del juego. Con otra versión pueden no funcionar.

## Instalación

También puedes usar el **lanzador en castellano** de [Releases](https://github.com/SeCaVa/InfiniteFusion-Castellano/releases). Descarga `PokemonInfiniteFusion-Launcher_1.1-Castellano.exe`, elige Kanto o Hoenn y una carpeta. Instala la versión oficial del juego para la que está hecha la traducción (Kanto 6.8.2 y Hoenn 1.2.2) y aplica la traducción de esta rama; al actualizar vuelve a aplicarla. Los botones conservan sus sprites y su fuente originales con rótulos españoles. Dentro del juego, elige **Español**.


1. Haz una copia de seguridad de la carpeta del juego.
2. Copia el contenido de `kanto/` (o de `hoenn/`) dentro de la carpeta del juego y acepta reemplazar los archivos.
3. Abre el juego y elige **Español** en el selector de idioma.

Cada carpeta contiene:

- `Data/spanish.dat`: textos traducidos y revisados disponibles.
- `Data/Scripts/...`: cambios de código.
  - Activa el idioma español.
  - Elige el género gramatical según el del jugador.
  - Encaja los nombres largos en los menús de ancho fijo.
  - Fija la Pokédex de fusiones (6 de octubre de 2026) y los mensajes de inicio (30 de septiembre de 2026) a las versiones traducidas.
- `Graphics/Localized/es/...`: imágenes con texto en castellano. El juego las usa solo cuando el idioma es español.

## Créditos

- **Pokémon Infinite Fusion**: Frogman, chardub y el resto del equipo de Infinite Fusion ([Kanto](https://github.com/infinitefusion/infinitefusion-e18), [Hoenn](https://github.com/infinitefusion/infinitefusion-hoenn-public)).
- **Traducción base**: el `Data/spanish.dat` sin acreditar incluido en el repositorio de Hoenn (rama `releases`). Sirvió de punto de partida y se revisó entero.
- Nombres oficiales: [PokeAPI](https://pokeapi.co/), [WikiDex](https://www.wikidex.net/) y [PkParaíso](https://www.pkparaiso.com/).
- Pokémon y todos sus nombres son marcas de Nintendo, Creatures Inc. y GAME FREAK inc. Proyecto de fans sin ánimo de lucro.
