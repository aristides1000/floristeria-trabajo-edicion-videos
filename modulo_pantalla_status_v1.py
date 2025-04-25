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
                        forma_pago TEXT,
                        modelo_ramo TEXT,
                        costo REAL,
                        fecha_hora_entrega TEXT,
                        enviado_a TEXT,
                        estado TEXT)''')
    conn.commit()
    conn.close()

# Función para obtener los pedidos pendientes ordenados por fecha y hora de entrega
def obtener_pedidos_pendientes():
    conn = sqlite3.connect("floristeria.db")
    cursor = conn.cursor()
    # Filtrar pedidos con estado "En Proceso" y ordenar por fecha y hora de entrega
    cursor.execute("SELECT fecha_hora_entrega, cliente, telefono, enviado_a, estado FROM pedidos WHERE estado = 'En Proceso' ORDER BY fecha_hora_entrega ASC")
    pedidos = cursor.fetchall()
    conn.close()
    return pedidos

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
root.geometry("800x400")  # Tamaño inicial de la ventana
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
tree = ttk.Treeview(tree_frame, columns=("Fecha y Hora Entrega", "Cliente", "Teléfono", "Enviado a", "Estado"), show="headings")
tree.heading("Fecha y Hora Entrega", text="Fecha y Hora Entrega")
tree.heading("Cliente", text="Cliente")
tree.heading("Teléfono", text="Teléfono")
tree.heading("Enviado a", text="Enviado a")
tree.heading("Estado", text="Estado")

# Configurar el ancho de las columnas
tree.column("Fecha y Hora Entrega", width=150, anchor="center")
tree.column("Cliente", width=150, anchor="w")
tree.column("Teléfono", width=100, anchor="center")
tree.column("Enviado a", width=150, anchor="w")
tree.column("Estado", width=100, anchor="center")

tree.pack(fill="both", expand=True)

# Conectar a la base de datos
conectar_db()

# Iniciar la actualización automática
actualizar_tabla()

# Ejecutar la aplicación
root.mainloop()