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
