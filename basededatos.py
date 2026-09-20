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
