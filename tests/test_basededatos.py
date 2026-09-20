import json
import tempfile
import unittest
from pathlib import Path

from basededatos import JocarsaBaseDatos


class PruebasJocarsaBaseDatos(unittest.TestCase):
    def setUp(self):
        self.temporal = tempfile.TemporaryDirectory()
        self.ruta = Path(self.temporal.name)
        self.conexion = JocarsaBaseDatos(self.ruta / "datos")
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

        otra = JocarsaBaseDatos(self.ruta / "importadas")
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

