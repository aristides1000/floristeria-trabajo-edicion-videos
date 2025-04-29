import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry  # Para manejar fechas
from datetime import datetime

# Función para conectar a la base de datos
def conectar_db():
    conn = sqlite3.connect("floristeria.db")
    cursor = conn.cursor()

    # Crear tabla de inventario si no existe
    cursor.execute('''CREATE TABLE IF NOT EXISTS inventario (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nombre TEXT NOT NULL,
                        tipo TEXT NOT NULL,  -- 'Rosa', 'Flor', 'Extra'
                        cantidad INTEGER NOT NULL,
                        unidad TEXT NOT NULL,  -- 'Docena' o 'Unidad'
                        fecha_carga TEXT NOT NULL,  -- Fecha y hora de carga
                        precio_costo REAL NOT NULL,  -- Precio de costo\
                        descripcion TEXT
                    )''')

    conn.commit()
    conn.close()

# Función para mostrar el inventario en la tabla principal
def mostrar_inventario():
    for row in tree_inventario.get_children():
        tree_inventario.delete(row)

    conn = sqlite3.connect("floristeria.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM inventario")
    for row in cursor.fetchall():
        tree_inventario.insert("", tk.END, values=row)
    conn.close()

    # Actualizar el inventario acumulado
    actualizar_inventario_acumulado()

# Función para agregar un ítem al inventario
def agregar_inventario():
    nombre = entry_nombre.get().strip()
    tipo = tipo_var.get()
    cantidad = entry_cantidad.get().strip()
    unidad = unidad_var.get()
    precio_costo = entry_precio_costo.get().strip()
    descripcion = entry_descripcion.get().strip()

    # Validar campos obligatorios
    if not (nombre and tipo and cantidad and unidad and precio_costo):
        messagebox.showerror("Error", "Todos los campos son obligatorios.")
        return

    try:
        cantidad = int(cantidad)  # Convertir la cantidad a entero
        if cantidad <= 0:
            raise ValueError
        precio_costo = float(precio_costo)  # Convertir el precio de costo a float
        if precio_costo <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Error", "La cantidad y el precio de costo deben ser números positivos.")
        return

    # Obtener la fecha y hora actual para la fecha de carga
    fecha_carga = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = sqlite3.connect("floristeria.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO inventario (nombre, tipo, cantidad, unidad, fecha_carga, precio_costo, descripcion) VALUES (?, ?, ?, ?, ?, ?, ?)",
                   (nombre, tipo, cantidad, unidad, fecha_carga, precio_costo, descripcion))
    conn.commit()
    conn.close()

    limpiar_campos_inventario()
    mostrar_inventario()
    messagebox.showinfo("Éxito", "Ítem agregado correctamente.")

# Función para modificar un ítem del inventario
def modificar_inventario():
    selected_item = tree_inventario.focus()
    if not selected_item:
        messagebox.showerror("Error", "Seleccione un ítem para modificar.")
        return

    nombre = entry_nombre.get().strip()
    tipo = tipo_var.get()
    cantidad = entry_cantidad.get().strip()
    unidad = unidad_var.get()
    precio_costo = entry_precio_costo.get().strip()
    descripcion = entry_descripcion.get().strip()

    # Validar campos obligatorios
    if not (nombre and tipo and cantidad and unidad and precio_costo):
        messagebox.showerror("Error", "Todos los campos son obligatorios.")
        return

    try:
        cantidad = int(cantidad)  # Convertir la cantidad a entero
        if cantidad <= 0:
            raise ValueError
        precio_costo = float(precio_costo)  # Convertir el precio de costo a float
        if precio_costo <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Error", "La cantidad y el precio de costo deben ser números positivos.")
        return

    # Obtener la fecha y hora actual para la fecha de carga
    fecha_carga = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = sqlite3.connect("floristeria.db")
    cursor = conn.cursor()
    item_id = tree_inventario.item(selected_item)['values'][0]
    cursor.execute("UPDATE inventario SET nombre=?, tipo=?, cantidad=?, unidad=?, fecha_carga=?precio_costo=?, descripcion=? WHERE id=?",
                   (nombre, tipo, cantidad, unidad, fecha_carga, precio_costo, descripcion, item_id))
    conn.commit()
    conn.close()

    limpiar_campos_inventario()
    mostrar_inventario()
    messagebox.showinfo("Éxito", "Ítem modificado correctamente.")

# Función para eliminar un ítem del inventario
def eliminar_inventario():
    selected_item = tree_inventario.focus()
    if not selected_item:
        messagebox.showerror("Error", "Seleccione un ítem para eliminar.")
        return

    conn = sqlite3.connect("floristeria.db")
    cursor = conn.cursor()
    item_id = tree_inventario.item(selected_item)['values'][0]
    cursor.execute("DELETE FROM inventario WHERE id=?", (item_id,))
    conn.commit()
    conn.close()

    limpiar_campos_inventario()
    mostrar_inventario()
    messagebox.showinfo("Éxito", "Ítem eliminado correctamente.")

# Función para cargar los datos de un ítem seleccionado en los campos de entrada
def cargar_inventario(event):
    selected_item = tree_inventario.focus()
    if selected_item:
        item = tree_inventario.item(selected_item)['values']
        entry_nombre.delete(0, tk.END)
        entry_nombre.insert(0, item[1])  # Nombre
        tipo_var.set(item[2])  # Tipo
        entry_cantidad.delete(0, tk.END)
        entry_cantidad.insert(0, item[3])  # Cantidad
        unidad_var.set(item[4])  # Unidad
        entry_precio_costo.delete(0, tk.END)
        entry_precio_costo.insert(0, item[6])  # Precio de costo
        entry_descripcion.delete(0, tk.END)
        entry_descripcion.insert(0, item[7])  # Descripcion

        # Mostrar la fecha de carga
        fecha_carga = item[5]  # Fecha de carga
        entry_fecha_carga.set_date(datetime.strptime(fecha_carga.split()[0], "%Y-%m-%d").date())

# Función para limpiar los campos de entrada del inventario
def limpiar_campos_inventario():
    entry_nombre.delete(0, tk.END)
    tipo_var.set("")
    entry_cantidad.delete(0, tk.END)
    unidad_var.set("")
    entry_fecha_carga.set_date(datetime.now().date())  # Establecer la fecha actual
    entry_precio_costo.delete(0, tk.END)
    entry_descripcion.delete(0, tk.END)

# Función para actualizar el inventario acumulado
def actualizar_inventario_acumulado():
    # Limpiar la tabla de inventario acumulado
    for row in tree_acumulado.get_children():
        tree_acumulado.delete(row)

    # Consultar el inventario acumulado agrupado por nombre
    conn = sqlite3.connect("floristeria.db")
    cursor = conn.cursor()
    cursor.execute('''SELECT nombre, SUM(cantidad) AS total, unidad, AVG(precio_costo) AS promedio_costo 
                      FROM inventario 
                      GROUP BY nombre, unidad''')
    for row in cursor.fetchall():
        tree_acumulado.insert("", tk.END, values=row)
    conn.close()

# Conectar a la base de datos
conectar_db()

# Configuración de la ventana principal
root = tk.Tk()
root.title("Gestión de Inventario - Floristería")
root.geometry("800x600")  # Tamaño inicial de la ventana
root.resizable(True, True)

# Marco principal
main_frame = ttk.Frame(root, padding=10)
main_frame.pack(fill="both", expand=True)

# Sección de inventario
inventario_frame = ttk.LabelFrame(main_frame, text="Inventario", padding=10)
inventario_frame.pack(fill="x", padx=10, pady=10)

# Variables para los widgets del inventario
entry_nombre = ttk.Entry(inventario_frame, width=40)
tipo_var = tk.StringVar()
entry_cantidad = ttk.Entry(inventario_frame, width=10)
unidad_var = tk.StringVar()
entry_fecha_carga = DateEntry(inventario_frame, date_pattern='yyyy-MM-dd', state="readonly")  # Fecha de carga
entry_precio_costo = ttk.Entry(inventario_frame, width=10)
entry_descripcion = ttk.Entry(inventario_frame, width=60)

# Campos del formulario de inventario
ttk.Label(inventario_frame, text="Nombre", anchor="w").grid(row=0, column=0, padx=5, pady=5, sticky="w")
entry_nombre.grid(row=0, column=1, padx=5, pady=5, sticky="w")

ttk.Label(inventario_frame, text="Tipo", anchor="w").grid(row=0, column=2, padx=5, pady=5, sticky="w")
tipo_combobox = ttk.Combobox(inventario_frame, textvariable=tipo_var, values=["Rosa", "Flor", "Extra"], state="readonly")
tipo_combobox.grid(row=0, column=3, padx=5, pady=5, sticky="w")

ttk.Label(inventario_frame, text="Cantidad", anchor="w").grid(row=0, column=4, padx=5, pady=5, sticky="w")
entry_cantidad.grid(row=0, column=5, padx=5, pady=5, sticky="w")

ttk.Label(inventario_frame, text="Unidad", anchor="w").grid(row=0, column=6, padx=5, pady=5, sticky="w")
unidad_combobox = ttk.Combobox(inventario_frame, textvariable=unidad_var, values=["Docena", "Unidad"], state="readonly")
unidad_combobox.grid(row=0, column=7, padx=5, pady=5, sticky="w")

ttk.Label(inventario_frame, text="Fecha de Carga", anchor="w").grid(row=1, column=2, padx=5, pady=5, sticky="w")
entry_fecha_carga.grid(row=1, column=3, padx=5, pady=5, sticky="w")

ttk.Label(inventario_frame, text="Precio de Costo", anchor="w").grid(row=1, column=0, padx=5, pady=5, sticky="w")
entry_precio_costo.grid(row=1, column=1, padx=5, pady=5, sticky="w")

ttk.Label(inventario_frame, text="Descripcion", anchor="w").grid(row=0, column=0, padx=5, pady=5, sticky="w")
entry_descripcion.grid(row=0, column=1, padx=5, pady=5, sticky="w")

# Botones del inventario
btn_frame_inventario = ttk.Frame(inventario_frame)
btn_frame_inventario.grid(row=2, column=0, columnspan=8, pady=10)
ttk.Button(btn_frame_inventario, text="Agregar", command=agregar_inventario).pack(side="left", padx=5)
ttk.Button(btn_frame_inventario, text="Modificar", command=modificar_inventario).pack(side="left", padx=5)
ttk.Button(btn_frame_inventario, text="Eliminar", command=eliminar_inventario).pack(side="left", padx=5)

# Tabla de inventario principal
tree_inventario = ttk.Treeview(inventario_frame, columns=("ID", "Nombre", "Tipo", "Cantidad", "Unidad", "Fecha Carga", "O"), show="headings")
for col in tree_inventario['columns']:
    tree_inventario.heading(col, text=col)
    tree_inventario.column(col, width=120, anchor="center")
tree_inventario.grid(row=3, column=0, columnspan=8, pady=10)
tree_inventario.bind("<<TreeviewSelect>>", cargar_inventario)

# Sección de inventario acumulado
acumulado_frame = ttk.LabelFrame(main_frame, text="Inventario Acumulado", padding=10)
acumulado_frame.pack(fill="x", padx=10, pady=10)

# Tabla de inventario acumulado
tree_acumulado = ttk.Treeview(acumulado_frame, columns=("Nombre", "Total", "Unidad", "Promedio de Costo"), show="headings")
for col in tree_acumulado['columns']:
    tree_acumulado.heading(col, text=col)
    tree_acumulado.column(col, width=120, anchor="center")
tree_acumulado.pack(fill="both", expand=True)

# Mostrar el inventario inicial
mostrar_inventario()

# Ejecutar la aplicación
root.mainloop()