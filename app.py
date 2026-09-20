"""Aplicación de consola para gestionar datos ficticios de Integra Tech."""

from basededatos import JocarsaBaseDatos


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
    conexion = JocarsaBaseDatos()
    preparar_basededatos(conexion)

    while True:
        print("\nJOCARSA | BASEDEDATOS · INTEGRA TECH")
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

