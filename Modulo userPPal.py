import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

# Crear la base de datos SQLite
def crear_base_datos():
    conn = sqlite3.connect('Usuarios.db')
    cursor = conn.cursor()
    
    # Tabla de usuarios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            rol TEXT NOT NULL,  -- "admin" o "usuario"
            acceso_pedidos INTEGER DEFAULT 0,  -- 1 = acceso permitido, 0 = acceso denegado
            acceso_inventario INTEGER DEFAULT 0,
            acceso_tickets INTEGER DEFAULT 0
        )
    ''')
    
    # Crear usuario administrador por defecto si no existe
    cursor.execute('SELECT * FROM usuarios WHERE usuario = "admin"')
    if not cursor.fetchone():
        cursor.execute('''
            INSERT INTO usuarios (usuario, password, rol, acceso_pedidos, acceso_inventario, acceso_tickets)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ("admin", "admin123", "admin", 1, 1, 1))
    
    conn.commit()
    conn.close()

# Función para cargar usuarios en la tabla
def cargar_usuarios():
    tree_usuarios.delete(*tree_usuarios.get_children())
    conn = sqlite3.connect('Usuarios.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM usuarios')
    rows = cursor.fetchall()
    for row in rows:
        tree_usuarios.insert("", "end", values=row)
    conn.close()

# Función para registrar un nuevo usuario
def registrar_usuario():
    usuario = entry_usuario.get()
    password = entry_password.get()
    rol = combo_rol.get()
    acceso_pedidos = var_acceso_pedidos.get()
    acceso_inventario = var_acceso_inventario.get()
    acceso_tickets = var_acceso_tickets.get()
    
    if not usuario or not password or not rol:
        messagebox.showwarning("Advertencia", "Todos los campos son obligatorios.")
        return
    
    try:
        conn = sqlite3.connect('Usuarios.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO usuarios (usuario, password, rol, acceso_pedidos, acceso_inventario, acceso_tickets)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (usuario, password, rol, acceso_pedidos, acceso_inventario, acceso_tickets))
        conn.commit()
        conn.close()
        cargar_usuarios()
        limpiar_campos()
        messagebox.showinfo("Éxito", "Usuario registrado correctamente.")
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "El nombre de usuario ya está registrado.")

# Función para modificar un usuario existente
def modificar_usuario():
    seleccion = tree_usuarios.selection()
    if not seleccion:
        messagebox.showwarning("Advertencia", "Seleccione un usuario para modificar.")
        return
    
    item_id = tree_usuarios.item(seleccion)["values"][0]
    usuario = entry_usuario.get()
    password = entry_password.get()
    rol = combo_rol.get()
    acceso_pedidos = var_acceso_pedidos.get()
    acceso_inventario = var_acceso_inventario.get()
    acceso_tickets = var_acceso_tickets.get()
    
    if not usuario or not password or not rol:
        messagebox.showwarning("Advertencia", "Todos los campos son obligatorios.")
        return
    
    try:
        conn = sqlite3.connect('Usuarios.db')
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE usuarios 
            SET usuario = ?, password = ?, rol = ?, acceso_pedidos = ?, acceso_inventario = ?, acceso_tickets = ?
            WHERE id = ?
        ''', (usuario, password, rol, acceso_pedidos, acceso_inventario, acceso_tickets, item_id))
        conn.commit()
        conn.close()
        cargar_usuarios()
        limpiar_campos()
        messagebox.showinfo("Éxito", "Usuario modificado correctamente.")
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error: {e}")

# Función para eliminar un usuario
def eliminar_usuario():
    seleccion = tree_usuarios.selection()
    if not seleccion:
        messagebox.showwarning("Advertencia", "Seleccione un usuario para eliminar.")
        return
    
    item_id = tree_usuarios.item(seleccion)["values"][0]
    
    respuesta = messagebox.askyesno("Confirmar", "¿Está seguro de eliminar este usuario?")
    if respuesta:
        conn = sqlite3.connect('Usuarios.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM usuarios WHERE id = ?', (item_id,))
        conn.commit()
        conn.close()
        cargar_usuarios()
        limpiar_campos()
        messagebox.showinfo("Éxito", "Usuario eliminado correctamente.")

# Función para cargar los datos de un usuario seleccionado en la forma
def cargar_datos_usuario(event):
    seleccion = tree_usuarios.selection()
    if not seleccion:
        return
    
    # Obtener los datos del usuario seleccionado
    datos_usuario = tree_usuarios.item(seleccion)["values"]
    id_usuario, usuario, password, rol, acceso_pedidos, acceso_inventario, acceso_tickets = datos_usuario
    
    # Limpiar los campos antes de cargar los datos
    limpiar_campos()
    
    # Cargar los datos en los campos correspondientes
    entry_usuario.insert(0, usuario)
    entry_password.insert(0, password)
    combo_rol.set(rol)
    var_acceso_pedidos.set(acceso_pedidos)
    var_acceso_inventario.set(acceso_inventario)
    var_acceso_tickets.set(acceso_tickets)

# Función para limpiar los campos de entrada
def limpiar_campos():
    entry_usuario.delete(0, tk.END)
    entry_password.delete(0, tk.END)
    combo_rol.set("")
    var_acceso_pedidos.set(0)
    var_acceso_inventario.set(0)
    var_acceso_tickets.set(0)

# Configuración de la interfaz gráfica
root = tk.Tk()
root.title("Administración de Usuarios - Floristería")
root.geometry("900x600")
root.configure(bg="#f0f0f0")  # Fondo claro

# Crear la base de datos
crear_base_datos()

# Etiquetas y campos de entrada para el registro/modificación de usuarios
tk.Label(root, text="Usuario:", bg="#f0f0f0", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=10, pady=5, sticky="w")
entry_usuario = tk.Entry(root, width=20, font=("Arial", 10))
entry_usuario.grid(row=0, column=1, padx=10, pady=5, sticky="w")

tk.Label(root, text="Contraseña:", bg="#f0f0f0", font=("Arial", 10, "bold")).grid(row=1, column=0, padx=10, pady=5, sticky="w")
entry_password = tk.Entry(root, width=20, font=("Arial", 10), show="*")
entry_password.grid(row=1, column=1, padx=10, pady=5, sticky="w")

tk.Label(root, text="Rol:", bg="#f0f0f0", font=("Arial", 10, "bold")).grid(row=2, column=0, padx=10, pady=5, sticky="w")
combo_rol = ttk.Combobox(root, values=["admin", "usuario"], state="readonly", width=20)
combo_rol.grid(row=2, column=1, padx=10, pady=5, sticky="w")

tk.Label(root, text="Acceso a Módulos:", bg="#f0f0f0", font=("Arial", 10, "bold")).grid(row=3, column=0, padx=10, pady=5, sticky="w")
var_acceso_pedidos = tk.IntVar()
var_acceso_inventario = tk.IntVar()
var_acceso_tickets = tk.IntVar()
tk.Checkbutton(root, text="Pedidos", variable=var_acceso_pedidos, bg="#f0f0f0").grid(row=3, column=1, sticky="w")
tk.Checkbutton(root, text="Inventario", variable=var_acceso_inventario, bg="#f0f0f0").grid(row=4, column=1, sticky="w")
tk.Checkbutton(root, text="Tickets", variable=var_acceso_tickets, bg="#f0f0f0").grid(row=5, column=1, sticky="w")

# Botones para gestionar usuarios
frame_botones = tk.Frame(root, bg="#f0f0f0")
frame_botones.grid(row=6, column=0, columnspan=2, pady=10)

btn_registrar = ttk.Button(frame_botones, text="Registrar Usuario", command=registrar_usuario)
btn_registrar.grid(row=0, column=0, padx=5)

btn_modificar = ttk.Button(frame_botones, text="Modificar Usuario", command=modificar_usuario)
btn_modificar.grid(row=0, column=1, padx=5)

btn_eliminar = ttk.Button(frame_botones, text="Eliminar Usuario", command=eliminar_usuario)
btn_eliminar.grid(row=0, column=2, padx=5)

# Tabla de usuarios
columns = ("ID", "Usuario", "Contraseña", "Rol", "Acceso Pedidos", "Acceso Inventario", "Acceso Tickets")
tree_usuarios = ttk.Treeview(root, columns=columns, show="headings", height=10)
for col in columns:
    tree_usuarios.heading(col, text=col)
    tree_usuarios.column(col, width=120, anchor="center")
tree_usuarios.grid(row=7, column=0, columnspan=2, padx=10, pady=10)

# Scrollbar para la tabla
scrollbar = ttk.Scrollbar(root, orient="vertical", command=tree_usuarios.yview)
scrollbar.grid(row=7, column=2, sticky="ns")
tree_usuarios.configure(yscrollcommand=scrollbar.set)

# Asociar el evento de selección de usuario con la función `cargar_datos_usuario`
tree_usuarios.bind("<<TreeviewSelect>>", cargar_datos_usuario)

# Cargar usuarios iniciales
cargar_usuarios()

# Ejecutar la aplicación
root.mainloop()