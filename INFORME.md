# Informe del proyecto: Integra Tech | basededatos

**Módulo:** 0486 - Acceso a datos  
**Resultado de aprendizaje:** RA1  
**Proyecto:** Base de datos personalizada aplicada a Integra Tech Consulting

## Resultado de aprendizaje

Desarrolla aplicaciones que gestionan información almacenada en ficheros,
identificando su campo de aplicación y utilizando clases específicas.

## Descripción

La aplicación administra pequeñas colecciones de clientes y proyectos ficticios
de Integra Tech Consulting. Cada base de datos se representa mediante una carpeta
y cada tabla mediante un fichero CSV. También permite convertir la información a
JSON y recuperarla posteriormente.

Este informe se ha generado con la herramienta **jocarsa | documentación** incluida
en los materiales del curso. La generación se realiza desde una copia limpia de
los archivos versionados; se excluyen repositorios internos, cachés, datos creados
durante las pruebas y librerías externas. La documentación automática mediante IA
del generador está desactivada.

## Árbol del proyecto

```text
proyecto
   +- tests
   |  +- __init__.py
   |  \- test_basededatos.py
   +- app.py
   +- basededatos.py
   +- demo.py
   \- README.md
```

## Archivos del proyecto

### proyecto
#### app.py

```python
"""Aplicación de consola para gestionar datos ficticios de Integra Tech."""

from basededatos import IntegraBaseDatos


def preparar_basededatos(conexion):
    try:
        conexion.usar_basededatos("integratech")
    except FileNotFoundError:
        conexion.crear_basededatos("integratech")
        conexion.crear_tabla(
            "clientes", ["nombre", "sector", "correo", "estado"]
        )
        conexion.crear_tabla(
            "proyectos", ["cliente", "nombre", "servicio", "estado"]
        )


def mostrar(registros):
    if not registros:
        print("No hay resultados.")
    for registro in registros:
        print(" | ".join(f"{campo}: {valor}" for campo, valor in registro.items()))


def insertar_cliente(conexion):
    print("\nNuevo cliente ficticio")
    datos = {
        "nombre": input("Nombre: ").strip(),
        "sector": input("Sector: ").strip(),
        "correo": input("Correo: ").strip(),
        "estado": input("Estado: ").strip(),
    }
    if not all(datos.values()):
        raise ValueError("Todos los campos son obligatorios.")
    registro = conexion.insertar("clientes", datos)
    print(f"Cliente guardado con id {registro['id']}.")


def buscar_cliente(conexion):
    nombre = input("Nombre exacto que quieres buscar: ").strip()
    mostrar(conexion.buscar("clientes", "nombre", nombre))


def menu():
    conexion = IntegraBaseDatos()
    preparar_basededatos(conexion)

    while True:
        print("\nINTEGRA TECH | BASEDEDATOS")
        print("1. Listar clientes")
        print("2. Añadir cliente")
        print("3. Buscar cliente")
        print("4. Exportar la base de datos a JSON")
        print("0. Salir")
        opcion = input("Opción: ").strip()

        try:
            if opcion == "1":
                mostrar(conexion.listar("clientes"))
            elif opcion == "2":
                insertar_cliente(conexion)
            elif opcion == "3":
                buscar_cliente(conexion)
            elif opcion == "4":
                ruta = conexion.exportar_json("exportaciones/integratech.json")
                print(f"Exportación creada en {ruta}.")
            elif opcion == "0":
                print("Hasta pronto.")
                break
            else:
                print("La opción no es válida.")
        except (FileNotFoundError, FileExistsError, ValueError, RuntimeError) as error:
            print(f"No se pudo completar la operación: {error}")


if __name__ == "__main__":
    menu()

```
#### basededatos.py

```python
"""Base de datos sencilla que guarda cada tabla en un fichero CSV."""

import csv
import json
import re
from pathlib import Path


class IntegraBaseDatos:
    """Gestiona bases de datos formadas por carpetas y ficheros CSV."""

    def __init__(self, instalacion="datos"):
        self.instalacion = Path(instalacion)
        self.instalacion.mkdir(parents=True, exist_ok=True)
        self.basededatos = None

    def validar_nombre(self, nombre):
        """Evita nombres vacíos y rutas que salgan de la instalación."""
        if not re.fullmatch(r"[A-Za-z0-9_-]+", nombre):
            raise ValueError(
                "El nombre solo puede contener letras, números, guiones y guiones bajos."
            )

    def crear_basededatos(self, nombre):
        self.validar_nombre(nombre)
        ruta = self.instalacion / nombre
        ruta.mkdir()
        self.basededatos = nombre

    def usar_basededatos(self, nombre):
        self.validar_nombre(nombre)
        ruta = self.instalacion / nombre
        if not ruta.is_dir():
            raise FileNotFoundError(f"No existe la base de datos: {nombre}")
        self.basededatos = nombre

    def ruta_tabla(self, tabla):
        if self.basededatos is None:
            raise RuntimeError("Primero debes seleccionar una base de datos.")
        self.validar_nombre(tabla)
        return self.instalacion / self.basededatos / f"{tabla}.csv"

    def crear_tabla(self, nombre, campos):
        ruta = self.ruta_tabla(nombre)
        if ruta.exists():
            raise FileExistsError(f"La tabla ya existe: {nombre}")
        if not campos:
            raise ValueError("La tabla debe tener al menos un campo.")
        for campo in campos:
            self.validar_nombre(campo)
        if "id" in campos:
            raise ValueError("El campo id se crea automáticamente.")

        with ruta.open("w", newline="", encoding="utf-8") as archivo:
            escritor = csv.writer(archivo)
            escritor.writerow(["id"] + campos)

    def leer_campos(self, tabla):
        ruta = self.ruta_tabla(tabla)
        if not ruta.is_file():
            raise FileNotFoundError(f"No existe la tabla: {tabla}")
        with ruta.open("r", newline="", encoding="utf-8") as archivo:
            lector = csv.reader(archivo)
            campos = next(lector, None)
        if not campos:
            raise ValueError(f"La tabla {tabla} no contiene cabeceras.")
        return campos

    def listar(self, tabla):
        ruta = self.ruta_tabla(tabla)
        if not ruta.is_file():
            raise FileNotFoundError(f"No existe la tabla: {tabla}")
        with ruta.open("r", newline="", encoding="utf-8") as archivo:
            return list(csv.DictReader(archivo))

    def siguiente_id(self, tabla):
        registros = self.listar(tabla)
        if not registros:
            return 1
        return max(int(registro["id"]) for registro in registros) + 1

    def insertar(self, tabla, datos):
        campos = self.leer_campos(tabla)
        campos_sin_id = campos[1:]
        if set(datos) != set(campos_sin_id):
            raise ValueError(
                "Los datos deben contener estos campos: " + ", ".join(campos_sin_id)
            )

        registro = {"id": str(self.siguiente_id(tabla))}
        for campo in campos_sin_id:
            registro[campo] = str(datos[campo])

        ruta = self.ruta_tabla(tabla)
        with ruta.open("a", newline="", encoding="utf-8") as archivo:
            escritor = csv.DictWriter(archivo, fieldnames=campos)
            escritor.writerow(registro)
        return registro

    def buscar(self, tabla, columna, valor):
        campos = self.leer_campos(tabla)
        if columna not in campos:
            raise ValueError(f"No existe la columna: {columna}")
        return [
            registro
            for registro in self.listar(tabla)
            if registro[columna].lower() == str(valor).lower()
        ]

    def exportar_json(self, archivo_destino):
        if self.basededatos is None:
            raise RuntimeError("Primero debes seleccionar una base de datos.")

        ruta_basededatos = self.instalacion / self.basededatos
        contenido = {"basededatos": self.basededatos, "tablas": {}}
        for ruta_csv in sorted(ruta_basededatos.glob("*.csv")):
            contenido["tablas"][ruta_csv.stem] = self.listar(ruta_csv.stem)

        destino = Path(archivo_destino)
        destino.parent.mkdir(parents=True, exist_ok=True)
        with destino.open("w", encoding="utf-8") as archivo:
            json.dump(contenido, archivo, ensure_ascii=False, indent=2)
        return destino

    def importar_json(self, archivo_origen, nombre_basededatos):
        origen = Path(archivo_origen)
        if not origen.is_file():
            raise FileNotFoundError(f"No existe el fichero: {origen}")
        with origen.open("r", encoding="utf-8") as archivo:
            contenido = json.load(archivo)

        tablas = contenido.get("tablas")
        if not isinstance(tablas, dict):
            raise ValueError("El JSON no contiene una colección de tablas válida.")

        self.crear_basededatos(nombre_basededatos)
        for nombre_tabla, registros in tablas.items():
            if not isinstance(registros, list):
                raise ValueError(f"La tabla {nombre_tabla} no contiene una lista.")
            campos = []
            if registros:
                campos = [campo for campo in registros[0] if campo != "id"]
            if not campos:
                raise ValueError(f"No se pueden deducir los campos de {nombre_tabla}.")
            self.crear_tabla(nombre_tabla, campos)
            for registro in registros:
                datos = {campo: registro.get(campo, "") for campo in campos}
                self.insertar(nombre_tabla, datos)

```
#### demo.py

```python
"""Crea una demostración reproducible con información ficticia."""

import shutil
from pathlib import Path

from basededatos import IntegraBaseDatos


def ejecutar_demo():
    ruta_datos = Path("datos_demo")
    ruta_exportacion = Path("exportaciones_demo")
    if ruta_datos.exists():
        shutil.rmtree(ruta_datos)
    if ruta_exportacion.exists():
        shutil.rmtree(ruta_exportacion)

    conexion = IntegraBaseDatos(ruta_datos)
    conexion.crear_basededatos("integratech")
    conexion.crear_tabla("clientes", ["nombre", "sector", "correo", "estado"])

    conexion.insertar(
        "clientes",
        {
            "nombre": "Taller Mediterráneo",
            "sector": "Automoción",
            "correo": "contacto@example.com",
            "estado": "activo",
        },
    )
    conexion.insertar(
        "clientes",
        {
            "nombre": "Estudio Turia",
            "sector": "Fotografía",
            "correo": "hola@example.com",
            "estado": "potencial",
        },
    )

    print("Todos los clientes:")
    for cliente in conexion.listar("clientes"):
        print(cliente)

    print("\nBúsqueda por estado:")
    for cliente in conexion.buscar("clientes", "estado", "activo"):
        print(cliente)

    destino = conexion.exportar_json(ruta_exportacion / "integratech.json")
    print(f"\nJSON creado en: {destino}")


if __name__ == "__main__":
    ejecutar_demo()

```
#### README.md

~~~markdown
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

~~~
#### tests
##### \_\_init\_\_.py

```python


```
##### test\_basededatos.py

```python
import json
import tempfile
import unittest
from pathlib import Path

from basededatos import IntegraBaseDatos


class PruebasIntegraBaseDatos(unittest.TestCase):
    def setUp(self):
        self.temporal = tempfile.TemporaryDirectory()
        self.ruta = Path(self.temporal.name)
        self.conexion = IntegraBaseDatos(self.ruta / "datos")
        self.conexion.crear_basededatos("empresa")
        self.conexion.crear_tabla("clientes", ["nombre", "estado"])

    def tearDown(self):
        self.temporal.cleanup()

    def test_crea_carpetas_y_tabla_csv(self):
        self.assertTrue((self.ruta / "datos" / "empresa").is_dir())
        self.assertTrue((self.ruta / "datos" / "empresa" / "clientes.csv").is_file())
        self.assertEqual(
            self.conexion.leer_campos("clientes"), ["id", "nombre", "estado"]
        )

    def test_inserta_lista_y_busca_registros(self):
        primero = self.conexion.insertar(
            "clientes", {"nombre": "Cliente Uno", "estado": "activo"}
        )
        segundo = self.conexion.insertar(
            "clientes", {"nombre": "Cliente Dos", "estado": "potencial"}
        )

        self.assertEqual(primero["id"], "1")
        self.assertEqual(segundo["id"], "2")
        self.assertEqual(len(self.conexion.listar("clientes")), 2)
        self.assertEqual(
            self.conexion.buscar("clientes", "estado", "ACTIVO")[0]["nombre"],
            "Cliente Uno",
        )

    def test_exporta_e_importa_json(self):
        self.conexion.insertar(
            "clientes", {"nombre": "Cliente Uno", "estado": "activo"}
        )
        destino = self.conexion.exportar_json(self.ruta / "copias" / "empresa.json")
        contenido = json.loads(destino.read_text(encoding="utf-8"))
        self.assertEqual(contenido["tablas"]["clientes"][0]["nombre"], "Cliente Uno")

        otra = IntegraBaseDatos(self.ruta / "importadas")
        otra.importar_json(destino, "empresa_copia")
        self.assertEqual(otra.listar("clientes")[0]["estado"], "activo")

    def test_gestiona_errores_de_nombres_y_campos(self):
        with self.assertRaises(ValueError):
            self.conexion.crear_tabla("../privada", ["nombre"])
        with self.assertRaises(ValueError):
            self.conexion.insertar("clientes", {"nombre": "Incompleto"})
        with self.assertRaises(FileNotFoundError):
            self.conexion.listar("proyectos")


if __name__ == "__main__":
    unittest.main()

```
