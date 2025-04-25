import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from tkcalendar import DateEntry

# Crear la base de datos SQLite y la tabla inventario2
def crear_base_datos():
    conn = sqlite3.connect('floristeria.db')
    cursor = conn.cursor()
    # Tabla de inventario2 con descripción
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventario2 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT NOT NULL,
            descripcion TEXT,  -- Nueva columna para la descripción
            cantidad INTEGER NOT NULL,
            costo REAL NOT NULL,
            fecha TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Función para cargar el consolidado
def cargar_consolidado():
    tree_consolidado.delete(*tree_consolidado.get_children())
    conn = sqlite3.connect('floristeria.db')
    cursor = conn.cursor()
    # Consulta para sumar por tipo
    cursor.execute('''
        SELECT tipo, SUM(cantidad) 
        FROM inventario2 
        GROUP BY tipo
    ''')
    rows = cursor.fetchall()
    for row in rows:
        tree_consolidado.insert("", "end", values=row)
    conn.close()

# Función para actualizar el inventario desde los pedidos enviados
def actualizar_inventario():
    try:
        conn = sqlite3.connect('floristeria.db')
        cursor = conn.cursor()
        # Buscar pedidos con estado "Enviado"
        cursor.execute('SELECT modelo_ramo FROM pedidos WHERE estado = "Enviado"')
        pedidos_enviados = cursor.fetchall()
        for pedido in pedidos_enviados:
            modelo_ramo = pedido[0]
            # Obtener detalles del modelo de ramo
            cursor.execute('''
                SELECT cantidad_rosas, cantidad_flores, cantidad_extras 
                FROM modelos_ramos 
                WHERE nombre_arreglo = ?
            ''', (modelo_ramo,))
            detalles_ramo = cursor.fetchone()
            if detalles_ramo:
                cantidad_rosas, cantidad_flores, cantidad_extras = detalles_ramo
                # Actualizar inventario2
                cursor.execute('UPDATE inventario2 SET cantidad = cantidad - ? WHERE tipo = "Rosas"', (cantidad_rosas,))
                cursor.execute('UPDATE inventario2 SET cantidad = cantidad - ? WHERE tipo = "Flores"', (cantidad_flores,))
                cursor.execute('UPDATE inventario2 SET cantidad = cantidad - ? WHERE tipo = "Extras"', (cantidad_extras,))
                # Eliminar el pedido enviado
                cursor.execute('DELETE FROM pedidos WHERE modelo_ramo = ?', (modelo_ramo,))
        conn.commit()
        conn.close()
        messagebox.showinfo("Éxito", "Inventario actualizado correctamente.")
        cargar_inventario()
        cargar_consolidado()  # Actualizar consolidado
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error al actualizar el inventario: {e}")

# Función para cargar el inventario en la tabla
def cargar_inventario():
    tree_inventario.delete(*tree_inventario.get_children())
    conn = sqlite3.connect('floristeria.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id,tipo, descripcion, cantidad, costo, fecha FROM inventario2')
    rows = cursor.fetchall()
    for row in rows:
        tree_inventario.insert("", "end", values=row)
    conn.close()

# Función para agregar un ítem al inventario
def agregar_item():
    tipo = combo_tipo.get()
    descripcion = entry_descripcion.get()  # Obtener descripción
    cantidad = entry_cantidad.get()
    costo = entry_costo.get()
    fecha = entry_fecha.get_date().strftime("%Y-%m-%d")
    if not tipo or not cantidad or not costo:
        messagebox.showwarning("Advertencia", "Todos los campos son obligatorios.")
        return
    try:
        cantidad = int(cantidad)
        costo = float(costo)
        conn = sqlite3.connect('floristeria.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO inventario2 (tipo, descripcion, cantidad, costo, fecha) 
            VALUES (?, ?, ?, ?, ?)
        ''', (tipo, descripcion, cantidad, costo, fecha))  # Incluir descripción
        conn.commit()
        conn.close()
        cargar_inventario()
        cargar_consolidado()  # Actualizar consolidado
        limpiar_campos()
        messagebox.showinfo("Éxito", "Ítem agregado correctamente.")
    except ValueError:
        messagebox.showerror("Error", "Cantidad y costo deben ser números válidos.")

# Función para modificar un ítem del inventario
def modificar_item():
    seleccion = tree_inventario.selection()
    if not seleccion:
        messagebox.showwarning("Advertencia", "Seleccione un ítem para modificar.")
        return
    item_id = tree_inventario.item(seleccion)["values"][0]
    tipo = combo_tipo.get()
    descripcion = entry_descripcion.get()  # Obtener descripción
    cantidad = entry_cantidad.get()
    costo = entry_costo.get()
    fecha = entry_fecha.get_date().strftime("%Y-%m-%d")
    if not tipo or not cantidad or not costo:
        messagebox.showwarning("Advertencia", "Todos los campos son obligatorios.")
        return
    try:
        cantidad = int(cantidad)
        costo = float(costo)
        conn = sqlite3.connect('floristeria.db')
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE inventario2 
            SET tipo = ?, descripcion = ?, cantidad = ?, costo = ?, fecha = ? 
            WHERE id = ?
        ''', (tipo, descripcion, cantidad, costo, fecha, item_id))  # Incluir descripción
        conn.commit()
        conn.close()
        cargar_inventario()
        cargar_consolidado()  # Actualizar consolidado
        limpiar_campos()
        messagebox.showinfo("Éxito", "Ítem modificado correctamente.")
    except ValueError:
        messagebox.showerror("Error", "Cantidad y costo deben ser números válidos.")

# Función para eliminar un ítem del inventario
def eliminar_item():
    seleccion = tree_inventario.selection()
    if not seleccion:
        messagebox.showwarning("Advertencia", "Seleccione un ítem para eliminar.")
        return
    item_id = tree_inventario.item(seleccion)["values"][0]
    respuesta = messagebox.askyesno("Confirmar", "¿Está seguro de eliminar este ítem?")
    if respuesta:
        conn = sqlite3.connect('floristeria.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM inventario2 WHERE id = ?', (item_id,))
        conn.commit()
        conn.close()
        cargar_inventario()
        cargar_consolidado()  # Actualizar consolidado
        limpiar_campos()
        messagebox.showinfo("Éxito", "Ítem eliminado correctamente.")

# Función para limpiar los campos de entrada
def limpiar_campos():
    combo_tipo.set("")
    entry_descripcion.delete(0, tk.END)  # Limpiar descripción
    entry_cantidad.delete(0, tk.END)
    entry_costo.delete(0, tk.END)

# Configuración de la interfaz gráfica
root = tk.Tk()
root.title("Control de Inventario - Floristería")
root.geometry("1200x800")
root.configure(bg="#f0f0f0")

# Estilo para los widgets
style = ttk.Style()
style.theme_use("clam")
style.configure("TLabel", background="#f0f0f0", font=("Arial", 10))
style.configure("TButton", background="#d3d3d3", foreground="black", font=("Arial", 10, "bold"))
style.map("TButton", background=[("active", "#c0c0c0")])
style.configure("Treeview", background="white", fieldbackground="white", font=("Arial", 10))
style.configure("Treeview.Heading", font=("Arial", 10, "bold"))

# Crear la base de datos
crear_base_datos()

# Etiquetas y campos de entrada
tk.Label(root, text="Tipo:", bg="#f0f0f0", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=10, pady=5, sticky="w")
combo_tipo = ttk.Combobox(root, values=["Rosas", "Flores", "Extras"], state="readonly", width=20)
combo_tipo.grid(row=0, column=1, padx=10, pady=5, sticky="w")

tk.Label(root, text="Descripción:", bg="#f0f0f0", font=("Arial", 10, "bold")).grid(row=1, column=0, padx=10, pady=5, sticky="w")
entry_descripcion = tk.Entry(root, width=60, font=("Arial", 10))  # Nuevo campo para descripción
entry_descripcion.grid(row=1, column=1, padx=10, pady=5, sticky="w")

tk.Label(root, text="Cantidad:", bg="#f0f0f0", font=("Arial", 10, "bold")).grid(row=2, column=0, padx=10, pady=5, sticky="w")
entry_cantidad = tk.Entry(root, width=20, font=("Arial", 10))
entry_cantidad.grid(row=2, column=1, padx=10, pady=5, sticky="w")

tk.Label(root, text="Costo:", bg="#f0f0f0", font=("Arial", 10, "bold")).grid(row=3, column=0, padx=10, pady=5, sticky="w")
entry_costo = tk.Entry(root, width=20, font=("Arial", 10))
entry_costo.grid(row=3, column=1, padx=10, pady=5, sticky="w")

tk.Label(root, text="Fecha:", bg="#f0f0f0", font=("Arial", 10, "bold")).grid(row=4, column=0, padx=10, pady=5, sticky="w")
entry_fecha = DateEntry(root, date_pattern="yyyy-mm-dd", width=18, font=("Arial", 10))
entry_fecha.grid(row=4, column=1, padx=10, pady=5, sticky="w")

# Botones
frame_botones = tk.Frame(root, bg="#f0f0f0")
frame_botones.grid(row=5, column=0, columnspan=2, pady=10)
btn_agregar = ttk.Button(frame_botones, text="Agregar", command=agregar_item)
btn_agregar.grid(row=0, column=0, padx=5)
btn_modificar = ttk.Button(frame_botones, text="Modificar", command=modificar_item)
btn_modificar.grid(row=0, column=1, padx=5)
btn_eliminar = ttk.Button(frame_botones, text="Eliminar", command=eliminar_item)
btn_eliminar.grid(row=0, column=2, padx=5)
btn_actualizar = ttk.Button(root, text="Actualizar Inventario", command=actualizar_inventario)
btn_actualizar.grid(row=6, column=0, columnspan=2, pady=10)

# Tabla de inventario
columns = ("ID", "Tipo", "Descripción", "Cantidad", "Costo", "Fecha")
tree_inventario = ttk.Treeview(root, columns=columns, show="headings", height=10)
for col in columns:
    tree_inventario.heading(col, text=col)
    tree_inventario.column(col, width=150, anchor="center")
tree_inventario.grid(row=7, column=0, columnspan=3, padx=10, pady=10)

# Scrollbar para la tabla
scrollbar_inv = ttk.Scrollbar(root, orient="vertical", command=tree_inventario.yview)
scrollbar_inv.grid(row=7, column=3, sticky="ns")
tree_inventario.configure(yscrollcommand=scrollbar_inv.set)

# Consolidado
tk.Label(root, text="Consolidado por Tipo", bg="#f0f0f0", font=("Arial", 12, "bold")).grid(row=8, column=0, columnspan=3, pady=10)
columns_con = ("Tipo", "Total")
tree_consolidado = ttk.Treeview(root, columns=columns_con, show="headings", height=5)
tree_consolidado.heading("Tipo", text="Tipo")
tree_consolidado.heading("Total", text="Total Disponible")
tree_consolidado.column("Tipo", width=200)
tree_consolidado.column("Total", width=200)
tree_consolidado.grid(row=9, column=0, columnspan=3, padx=10, pady=5)

# Botón refrescar consolidado
btn_refrescar = ttk.Button(root, text="Refrescar Consolidado", command=cargar_consolidado)
btn_refrescar.grid(row=10, column=0, columnspan=3, pady=10)

# Cargar datos iniciales
cargar_inventario()
cargar_consolidado()

# Ejecutar la aplicación
root.mainloop()