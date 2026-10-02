# Glosario de la traducción de Pokémon Infinite Fusion

## Criterios

- Castellano de España, tuteo al jugador: en Rojo Fuego oficial también tutean la enfermera ("Tus POKéMON están de nuevo en forma. ¡Esperamos que te vaya bien!") y los menús ("¿Qué deseas hacer?").
- Team Rocket (no "Equipo Rocket"); Equipo Aqua, Equipo Magma, Equipo Plasma. Trainer Card = Ficha de Entrenador. Wonder Trade = Intercambio Prodigioso. PokéMart = Tienda Pokémon.
- Nombres oficiales **más recientes** de España (PokeAPI → WikiDex → PkParaíso). Si no caben: nombre oficial antiguo; si tampoco, el actual abreviado.
- Pokémon: mismo nombre que en inglés (también las fusiones triples propias de PIF: Zapmolcuno, Enraicune…).
- Género del jugador en diálogos con marcas `[[o|a]]` (masculino|femenino): "¿Estás list[[o|a]]?". Nunca en menús.
- Códigos de control intactos: `\PN`, `\v[n]`, `{1}`, `<r>`, `\c[n]`… En `\ch[a,b,opciones]` se traducen las opciones, pero se respetan los dos primeros parámetros y el **número de comas** del inglés (aunque tenga erratas).
- Dinero: "15.000$" (formato de los juegos oficiales en España).
- Plantas: S1 (sótano), P1, P2… como en la base.

## Objetos y términos propios de PIF

| Inglés | Castellano | Nota |
|---|---|---|
| Racing Bicycle | Bici Veloz | Provisional. "Bici de Carreras" es el nombre oficial de la Mach Bike (Hoenn). |
| DNA Splicers | Punta ADN | Oficial (Pokémon Negro 2/Blanco 2). |
| Super Splicers | Superfusionador | De la base. **Decidir**: ¿"Superpunta ADN" para concordar con el oficial? |
| Infinite Splicers | Fusionador Infinito | De la base. **Decidir** igual que el anterior. |
| DNA Reverser | Invertidor de ADN | De la base. Revisar. |
| Infinite Reversers | Separadores Infinitos | De la base. Revisar: no concuerda con "Invertidor". |
| Quest | Misión | |

| Exp. Candy | Caramelo Exp. | Como los oficiales (Caramelo Exp. S, M…). |
| Resoli Berry | Baya Hibis | Errata del original por Roseli Berry (mismo efecto). |
| Quest Journal / Quest Notebook | Diario de Misiones / Cuaderno de Misiones | |
| Seaweed | Algas | |

## Descripciones de la Pokédex

- Los gritos escritos de los Pokémon se conservan como en el original; no se adaptan fonéticamente al castellano. Por ejemplo: «¡Beeb Beehoo!».
- Castellano de España, con voz enciclopédica clara y natural. Conservar los datos, matices, relaciones causales y cantidades del texto que muestra el juego.
- Las entradas de fusiones son textos propios: no sustituirlas por descripciones oficiales de otras especies o versiones.
- `POKENAME` se conserva literalmente hasta que el juego lo sustituye. Pokémon es invariable en plural.
- Bulbo vegetal → **bulbo**; seed → **semilla**; flower bud → **capullo floral**; vine → **liana**; hive mind → **mente colectiva**. Light bulb → **bombilla**, según el contexto.
- Los nombres oficiales de movimientos, habilidades, objetos y tipos se aplican solo cuando el texto se refiere a ellos. Una palabra común que coincida con un nombre inglés no se convierte automáticamente en una habilidad.
- «Entrenador» y «baya» como nombres comunes se escriben en minúsculas. Los nombres propios de objetos conservan la grafía del diccionario.
- Mantener autores y referencias a sprites. Encajar las descripciones por páginas medidas con la fuente del juego, sin suprimir frases ni detalles.

## Fuentes de nombres oficiales

- Lugares: `referencias/lugares_wikidex.json` (WikiDex, nombres actuales; leído con el navegador del usuario, despacio) > PokeAPI > `referencias/lugares_rojo_fuego.json` (ROM oficial de Rojo Fuego). Herramienta: `tools/lugares.py`.
- Clases de entrenador: `referencias/clases_rojo_fuego.json` (ROM, 3.ª gen.) como respaldo; comprobar los actuales en WikiDex.
- Plurales de objetos: `tools/plurales.py` (reglas + propuesta de ClinePass verificada contra el singular) y `traduccion/bd/_plurales_manuales.json`.

## Pendiente de verificar

- Lugares con nombre dudoso (en `traduccion/lugares/_manuales.json`): Hall of Origin → "Sala Origen", Stern's Shipyard → "Astillero de Babor".
- Wonder Trade: oficial "Intercambio Prodigioso"; la base usa a veces "Intercambio Mágico".
- La base usa a veces nombres de Hispanoamérica (Ciudad Violeta → Ciudad Malva) o acortados ("Azafrán"): ver `tools/terminos.py`.

- Personajes de Hoenn (Steven → Máximo…), líderes, Alto Mando, Equipo Magma/Aqua.
- Clases de entrenador actuales (Camper, Picnicker, Beauty…): la base mezcla nombres antiguos y nuevos.
