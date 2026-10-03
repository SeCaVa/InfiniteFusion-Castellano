#!/bin/sh
# Regenera la traducción completa desde los diccionarios de traduccion/.
#   1. extraer.py         añade a los diccionarios las cadenas nuevas del juego
#   2. nombres_oficiales  nombres oficiales actuales (PokeAPI) en bd/
#      lugares.py         nombres de mapas y lugares (WikiDex, PokeAPI, Rojo Fuego)
#      plurales.py        plurales de objetos
#      genero.py          marcas [[o|a]] en patrones claros de los diálogos
#   3. generar_dat.py     repos/kanto y repos/hoenn: Data/spanish.dat
#   4. revisar.py         comprobaciones (traduccion/_informes/revision.txt)
# Uso (Git Bash): sh aplicar.sh
set -e
cd "$(dirname "$0")"
export PYTHONIOENCODING=utf-8
python tools/extraer.py
python tools/nombres_oficiales.py
python tools/lugares.py
python tools/plurales.py
python tools/genero.py
python tools/sustituir.py
python tools/corregir_incidencias_20261001.py
python tools/aplicar_pokedex_fusiones.py
python tools/concordancia_objetos.py
python tools/ajustar_descripciones_mochila.py
python tools/corregir_incidencias_20261003.py
python tools/generar_dat.py
python tools/revisar.py
