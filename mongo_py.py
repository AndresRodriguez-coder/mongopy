from pymongo import MongoClient
from bson import ObjectId
import time

def imprimir_separador(titulo):
    print("\n" + "="*50)
    print(titulo)
    print("="*50)


try:
    cliente=MongoClient("mongodb://localhost:27017/")
    db=cliente["uno"]
    print("Conexion exitosa a mongo :)")
except Exception as e:
    print(f"Error al conectarse: {e}")
    exit(1)

productos=db["productos"]
pedidos=db["pedidos"]
detalles_pedido=db["detalles_pedido"]

productos.delete_many({})
pedidos.delete_many({})
detalles_pedido.delete_many({})

imprimir_separador("1.Insertar un documento")
doc={
    "nombre":"Regadera",
    "precio":"12000",
    "stock":10
}
resultado=productos.insert_one(doc)
print(f"ID del documento insertado: {resultado.inserted_id}")

imprimir_separador("2. Insertar multiples documentos")
nuevos_productos=[
    {"nombre":"Tijera","precio":8000,"stock":15},
    {"nombre":"Maceta","precio":15000,"stock":20}
]

resultado=productos.insert_many(nuevos_productos)
print(f"IDs de documentos insertados {resultado.inserted_ids}")

imprimir_separador("3. Consultar todos los documentos")
for producto in productos.find():
    print(producto)

imprimir_separador("4. Consultar productos con precio mayor a 10000")
for producto in productos.find({"precio": {"$gt":10000}}):
    print(producto)

imprimir_separador("5. Consultar un documento especifico")
producto= productos.find_one({"nombre":"Maceta"})
print(producto)

imprimir_separador("6. Actualizar un documento")
productos.update_one(
    {"nombre":"Tijera"},
    {"$set":{"precio":8000}}
)
print("Producto Actualizado")
print(productos.find_one({"nombre":"Tijera"}))

imprimir_separador("7. Actualizar varios documentos")
resultado=productos.update_many(
    {},
    {"$set":{"disponible":True}}
)
print(f"Cantidad de documentos actualizados: {resultado.modified_count}")

imprimir_separador("8. Contar documentos")
total=productos.count_documents({})
print(f"Total de productos en la base de datos: {total}")

imprimir_separador("9. Ordenar resultados por precio descendente")
for producto in productos.find().sort("precio", -1):
    print(producto)

imprimir_separador("10. Primeros 2 productos")
for producto in productos.find().limit(2):
    print(producto)

imprimir_separador("11. Crear indice")
indice=productos.create_index("nombre")
print(f"indice creado: {indice}")

imprimir_separador("12. Agregacion - Productos por rango de precio")
pipeline = [
    {
        "$group": {
            "_id": {
                "$switch": {
                    "branches": [
                        {"case": {"$lt": ["$precio", 10000]}, "then": "Económico"},
                        {"case": {"$lt": ["$precio", 15000]}, "then": "Medio"},
                    ],
                    "default": "Premium"
                }
            },
            "cantidad": {"$sum": 1},
            "precio_promedio": {"$avg": "$precio"}
        }
    }
]
for resultado in productos.aggregate(pipeline):
    print(resultado)


imprimir_separador("13. Ejemplo de $lookup (unión de colecciones)")
pedido_id = pedidos.insert_one({
    "fecha": "2024-01-20",
    "cliente": "Cliente Ejemplo"
}).inserted_id

detalles_pedido.insert_many([
    {"pedidoId": pedido_id, "producto": "Regadera", "cantidad": 1},
    {"pedidoId": pedido_id, "producto": "Maceta", "cantidad": 2}
])

pipeline = [
    {
        "$lookup": {
            "from": "detalles_pedido",
            "localField": "_id",
            "foreignField": "pedidoId",
            "as": "detalles"
        }
    }
]
for pedido in pedidos.aggregate(pipeline):
    print("Pedido completo con sus detalles:")
    print(pedido)

# 14. Eliminar un documento
imprimir_separador("14. Eliminar un documento")
resultado = productos.delete_one({"nombre": "Tijera"})
print(f"Cantidad de documentos eliminados: {resultado.deleted_count}")

# Cerrar conexión
cliente.close()
print("\nDemostración completada. Conexión cerrada.")