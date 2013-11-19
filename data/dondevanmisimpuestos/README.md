## Importación de datos a python-cubes, para su visualización con CubesViewer

### Datos procesados

Se procesan los datos de PGE y CCAA. Por defecto, se genera una base de datos SQLite.

    $ python dvmi-import.py

La base de datos se encuentra en el proyecto (`dvmi-cubes.sqlite`). Si sólo quieres visualizar los datos,
puedes  el procesado.

### Arranque de python-cubes server

Cubes es un servidor OLAP ligero en python: http://cubes.databrewery.org/ . Es necesario tener python-cubes 0.10.2 o posterior.

Con él instalado, podemos inicializar el servidor OLAP usando la configuración proporcionada:

    $ slicer serve slicer.ini

Por defecto, el servidor arrancará escuchando en "localhost:5000"

### Exploración con CubesViewer

CubesViewer es una herramienta visual para explorar y analizar bases de datos
servidas por python-cubes. Es HTML5 así que no es necesario instalarla.

Basta descargar el proyecto y abrir el visor de Cubes en el navegador:

    cubesviewer/src/htmlviews/gui.html 

Esto nos permitirá conectarnos al servidor cubes en "localhost:5000" y visualizar
y explorar los datos.


    