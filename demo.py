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
    conexion.crear_tabla(
        "clientes",
        ["nombre", "contacto", "correo", "telefono", "sector", "estado"],
    )
    conexion.crear_tabla(
        "proyectos",
        ["cliente_id", "nombre", "descripcion", "estado", "prioridad", "valor"],
    )

    conexion.insertar(
        "clientes",
        {
            "nombre": "Taller Mediterráneo",
            "contacto": "Ana Pérez",
            "correo": "contacto@example.com",
            "telefono": "600000001",
            "sector": "Automoción",
            "estado": "Activo",
        },
    )
    conexion.insertar(
        "clientes",
        {
            "nombre": "Estudio Turia",
            "contacto": "Luis Serra",
            "correo": "hola@example.com",
            "telefono": "600000002",
            "sector": "Fotografía",
            "estado": "Potencial",
        },
    )
    conexion.insertar(
        "proyectos",
        {
            "cliente_id": "1",
            "nombre": "Portal de citas",
            "descripcion": "Prototipo web para organizar reservas",
            "estado": "Pendiente",
            "prioridad": "Media",
            "valor": "1200",
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
