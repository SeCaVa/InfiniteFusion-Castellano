# Lanzador de Infinite Fusion en castellano

Abre `installation/PokemonInfiniteFusion-Launcher_1.1-Castellano.exe`, situado un nivel por encima de esta carpeta. El lanzador original se conserva intacto.

Elige Kanto o Hoenn y la carpeta de instalación. **Instalar** descarga el juego oficial y aplica la traducción. **Actualizar** actualiza la base oficial y vuelve a aplicar el castellano. Dentro del juego, selecciona **Español** si no está seleccionado.

La traducción se descarga de [SeCaVa/InfiniteFusion-Castellano, rama traduccion](https://github.com/SeCaVa/InfiniteFusion-Castellano/tree/traduccion). En cada instalación o actualización, el lanzador consulta la última revisión publicada y descarga su paquete exacto, evitando reutilizar un ZIP antiguo de la rama. El fork contiene los archivos de idioma, por lo que la base del juego se obtiene primero de los repositorios oficiales. Los cambios que solo estén en tu carpeta local aún no se incluyen.

El paquete de idioma se descarga y comprueba antes de modificar la instalación. Si su descarga falla, la operación se detiene. Solo se aplican `Data/spanish.dat`, scripts Ruby de `Data/Scripts/`, gráficos PNG de `Graphics/Localized/es/` y los dos archivos de la presentación de SeCaVa: `Graphics/Titles/SeCaVa/logo.png` y `Audio/ME/SeCaVa_intro.wav`, del juego elegido. Si falla una escritura del idioma, se restauran los archivos que esa aplicación de idioma haya tocado. Esa restauración no deshace una actualización previa de la base oficial.

## Archivos para continuar el trabajo

- `es.json`: textos traducidos de la interfaz y mensajes del instalador.
- `launcher_es.py`: descarga del fork, aplicación del idioma, botones con texto español y diagnóstico.
- `build_castellano.py`: genera el ejecutable conservando el runtime del original; requiere Python 3.12.
- `original/`: fuentes del [lanzador oficial](https://github.com/infinitefusion/PIFInstallerGUI) usadas como punto de partida.
- `src/`: fuentes finales generadas; revisar aquí, pero editar los archivos anteriores para conservar los cambios al recompilar.
- `test_launcher.py`: pruebas aisladas. No usa instalaciones reales ni ejecuta Git.
- `build-info.json`: procedencia y hashes de ambos ejecutables.
- `startup-test.json`: resultado del diagnóstico del ejecutable final.
- `buttons-preview.html`: vista local de los seis botones, en estado normal y seleccionado. `preview_buttons.py` la regenera sin modificar los sprites.

Desde la raíz del proyecto, con Python 3.12:

```text
python launcher/build_castellano.py
python launcher/test_launcher.py
```

Para recompilar en otro equipo, coloca el lanzador **oficial original 1.1** en `installation/PokemonInfiniteFusion-Launcher_1.1.exe` e instala Pillow para ese Python (esta entrega se comprobó con Pillow 12.3.0). No uses el ejecutable traducido como original del constructor. Las fuentes finales `src/` y las fuentes oficiales `original/` se incluyen para revisión. El ZIP de prueba y la carpeta `runtime/` son auxiliares locales y no se distribuyen en Git; la prueba del ZIP se omite si no existe. Para ejecutarla, guarda el [ZIP de la rama de traducción](https://codeload.github.com/SeCaVa/InfiniteFusion-Castellano/zip/refs/heads/traduccion) como `launcher/translation-sample.zip`. La vista HTML ya incluye sus imágenes; regenerarla requiere los recursos originales extraídos en `runtime/resources/`.

El diagnóstico del ejecutable admite `--verificar "ruta absoluta al informe.json"`. Usa datos de prueba, sin acceder a partidas, configuración personal ni red. Puede fallar en un entorno de ejecución restringido aunque funcione al abrirlo normalmente.

Se comprobaron el arranque del ejecutable, ambos temas, botones y estados de interfaz, descarga real de ambos paquetes del fork y aplicación/restauración en carpetas temporales. No se hizo una instalación completa ni se actualizó el juego real.

Los botones conservan ahora los sprites originales, incluidos sus iconos y marcas de selección. La interfaz cubre únicamente el rótulo inglés recuperando sus franjas de fondo y dibuja el rótulo español con la fuente original **Power Clear**. No se sustituyen por botones básicos. Para rasterizar esta fuente, el constructor incluye los módulos y extensiones de Pillow de la misma versión disponible en el Python 3.12 usado para compilar (12.3.0 en esta sesión).
