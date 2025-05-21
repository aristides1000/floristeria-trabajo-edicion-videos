import sqlite3
import tkinter as tk
from tkinter import ttk
from datetime import datetime

# Función para conectar a la base de datos
def conectar_db():
    conn = sqlite3.connect("floristeria.db")
    cursor = conn.cursor()
    # Crear la tabla si no existe
    cursor.execute('''CREATE TABLE IF NOT EXISTS pedidos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fecha_hora TEXT,
                    cliente TEXT,
                    telefono TEXT,
                    direccion TEXT,
                    modelo_ramo TEXT,
                    costo_dolares REAL,
                    costo_bolivares REAL,
                    costo_por_cobrar REAL,
                    fecha_hora_entrega TEXT,
                    enviado_a TEXT,
                    telefono_receptor TEXT,
                    descripcion TEXT,
                    tipo_entrega TEXT,
                    delivery_persona TEXT,
                    costo_adicional REAL,
                    costo_total REAL,
                    numero_factura INTEGER NOT NULL,
                    estado TEXT)''')
    conn.commit()
    conn.close()

# Función para obtener los pedidos pendientes ordenados por fecha y hora de entrega
def obtener_pedidos_pendientes():
    conn = sqlite3.connect("floristeria.db")
    cursor = conn.cursor()
    # Filtrar pedidos con estado "En Proceso" y ordenar por fecha y hora de entrega
    cursor.execute("SELECT id, fecha_hora_entrega AS dia, fecha_hora_entrega, modelo_ramo, descripcion FROM pedidos WHERE estado = 'En Proceso' ORDER BY fecha_hora_entrega ASC")
    pedidos = cursor.fetchall()
    conn.close()

    days = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado", "Domingo"]

    pedidos_modified = []

    for pedido in pedidos:
        pedido_list = list(pedido)
        d = datetime.strptime(pedido_list[1], "%Y-%m-%d %H:%M")
        pedido_list[1] = days[d.weekday()]
        pedido = tuple(pedido_list)
        pedidos_modified.append(pedido)

    return pedidos_modified

# Función para actualizar la tabla de pedidos pendientes
def actualizar_tabla():
    # Limpiar la tabla antes de actualizar
    for row in tree.get_children():
        tree.delete(row)

    # Obtener los pedidos pendientes
    pedidos = obtener_pedidos_pendientes()

    # Insertar los datos en la tabla
    for pedido in pedidos:
        tree.insert("", tk.END, values=pedido)

    # Programar la próxima actualización
    root.after(5000, actualizar_tabla)  # Actualizar cada 5 segundos (5000 ms)

# Configuración de la ventana principal
root = tk.Tk()
root.title("Pedidos Pendientes - Floristería")
root.geometry("1000x800")  # Tamaño inicial de la ventana
root.resizable(True, True)

# Estilo personalizado
style = ttk.Style()
style.theme_use("clam")  # Tema moderno
style.configure("TLabel", font=("Arial", 10), padding=5)
style.configure("TButton", font=("Arial", 10), padding=5)
style.configure("Treeview", font=("Arial", 10), rowheight=25)
style.configure("Treeview.Heading", font=("Arial", 10, "bold"))

# Marco principal
main_frame = ttk.Frame(root, padding=10)
main_frame.pack(fill="both", expand=True)

# Etiqueta de título
titulo_label = ttk.Label(main_frame, text="Pedidos Pendientes", font=("Arial", 14, "bold"))
titulo_label.pack(pady=10)

# Tabla de pedidos pendientes
tree_frame = ttk.Frame(main_frame)
tree_frame.pack(fill="both", expand=True, pady=10)

# Crear la tabla
tree = ttk.Treeview(tree_frame, columns=("Id", "Dia", "Fecha y Hora Entrega", "Modelo de Ramo", "Descripcion"), show="headings")
tree.heading("Id", text="Id")
tree.heading("Dia", text="Dia")
tree.heading("Fecha y Hora Entrega", text="Fecha y Hora Entrega")
tree.heading("Modelo de Ramo", text="Modelo de Ramo")
tree.heading("Descripcion", text="Descripcion")

# Configurar el ancho de las columnas
tree.column("Id", width=1, anchor="w")
tree.column("Dia", width=10, anchor="center")
tree.column("Fecha y Hora Entrega", width=10, anchor="center")
tree.column("Modelo de Ramo", width=10, anchor="center")
tree.column("Descripcion", width=200, anchor="w")

tree.pack(fill="both", expand=True)

# Conectar a la base de datos
conectar_db()

# Iniciar la actualización automática
actualizar_tabla()

# Ejecutar la aplicación
root.mainloop()