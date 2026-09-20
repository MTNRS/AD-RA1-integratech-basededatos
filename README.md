# Integra Tech | basededatos

Proyecto práctico del RA1 de **0486 - Acceso a datos**. La aplicación gestiona
información mediante carpetas y ficheros CSV. Parte de la clase `JocarsaBBDD`
utilizada como ejemplo en la unidad y aplica lo aprendido a un producto propio
de **Integra Tech Consulting**.

## Objetivo

Crear una base de datos sencilla en la que:

- cada base de datos sea una carpeta;
- cada tabla sea un fichero CSV;
- la primera fila guarde los nombres de los campos;
- los registros puedan insertarse, listarse y buscarse;
- toda la base de datos pueda convertirse a JSON y recuperarse después.

El producto permite mantener un pequeño registro local de clientes y proyectos
ficticios de **Integra Tech Consulting**. No contiene datos internos ni datos de
clientes reales.

## Estructura

```text
.
├── app.py                    Aplicación de consola
├── basededatos.py            Clase IntegraBaseDatos
├── demo.py                   Demostración automática
├── tests/
│   └── test_basededatos.py   Pruebas de ficheros, datos, JSON y errores
└── README.md
```

Las carpetas `datos/` y `exportaciones/` se crean al ejecutar la aplicación y
no se guardan en Git.

## Ejecución

Se necesita Python 3. No hay dependencias externas.

```bash
python app.py
```

Para ejecutar una demostración con datos ficticios:

```bash
python demo.py
```

Para ejecutar las pruebas:

```bash
python -m unittest discover -v
```

## Relación con los criterios de evaluación

| Criterio | Evidencia en el proyecto |
|---|---|
| a | `pathlib.Path` crea y comprueba carpetas, bases de datos y tablas. |
| b | Se utiliza acceso secuencial para listar y buscar; es sencillo y adecuado para pocos registros, pero menos eficiente que un índice para grandes cantidades de datos. |
| c | `leer_campos`, `listar` y `buscar` recuperan información de CSV. |
| d | `crear_tabla` e `insertar` almacenan cabeceras y registros. |
| e | `exportar_json` e `importar_json` convierten entre CSV y JSON. |
| f | La clase valida nombres y lanza excepciones claras; `app.py` las captura y muestra mensajes comprensibles. |
| g | El proyecto incluye instrucciones, demostración y pruebas automáticas. |

## Decisiones técnicas

CSV permite abrir los datos con un editor de texto o una hoja de cálculo y es
adecuado para practicar flujos de lectura y escritura. Su inconveniente es que
las búsquedas recorren el fichero completo y no ofrece relaciones, bloqueos ni
consultas complejas. Por ello este proyecto es educativo y no sustituye la base
de datos de producción de Integra Tech Consulting.

La aplicación empresarial propuesta es una herramienta local de importación,
exportación y consulta de conjuntos pequeños de datos. Puede servir para crear
copias portables o preparar datos antes de incorporarlos a la plataforma. Antes
de integrarla hay que adaptarla a los modelos, permisos y validaciones del
sistema real y probarla en un entorno aislado.

## Uso de IA

Se ha utilizado IA como apoyo para ordenar los requisitos del RA, preparar una
primera implementación, revisar casos de error y proponer pruebas. El proyecto
mantiene las técnicas vistas en clase y evita frameworks o dependencias que no
forman parte de la unidad.

Antes de entregar, el alumno debe ejecutar el programa, leer cada método,
realizar al menos una modificación propia y ser capaz de explicar:

1. por qué cada tabla es un CSV;
2. cómo se calcula el siguiente identificador;
3. por qué una búsqueda secuencial se vuelve lenta al crecer el fichero;
4. cómo se realiza la conversión entre CSV y JSON;
5. qué excepciones pueden producirse y dónde se gestionan.

## Informe final

La entrega incluye [`INFORME.md`](INFORME.md), generado con la herramienta
`jocarsa | documentación` incluida en los materiales del curso. Para evitar
contenido innecesario, se ha generado desde una copia limpia de los archivos
versionados, sin `.git`, cachés, datos temporales ni librerías externas.
