import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import subprocess  # Para ejecutar scripts externos
import os  # Para manejar rutas de archivos

# Crear la base de datos SQLite
def crear_base_datos():
    conn = sqlite3.connect('usuarios.db')
    cursor = conn.cursor()

    # Tabla de usuarios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            rol TEXT NOT NULL,  -- "admin" o "usuario"
            acceso_floristeria INTEGER DEFAULT 0, -- 1 = acceso permitido, 0 = acceso denegado
            acceso_inventario INTEGER DEFAULT 0,
            acceso_pedidos INTEGER DEFAULT 0,
            acceso_saldo INTEGER DEFAULT 0,
            acceso_status INTEGER DEFAULT 0,
            acceso_tickets INTEGER DEFAULT 0
        )
    ''')

    # Crear usuario administrador por defecto si no existe
    cursor.execute('SELECT * FROM usuarios WHERE usuario = "admin"')
    if not cursor.fetchone():
        cursor.execute('''
            INSERT INTO usuarios (usuario, password, rol, acceso_floristeria, acceso_inventario, acceso_pedidos, acceso_saldo, acceso_status, acceso_tickets)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', ("admin", "admin123", "admin", 1, 1, 1, 1, 1, 1))

    conn.commit()
    conn.close()

# Función para iniciar sesión
def iniciar_sesion():
    usuario = entry_usuario.get()
    password = entry_password.get()

    if not usuario or not password:
        messagebox.showwarning("Advertencia", "Ingrese su usuario y contraseña.")
        return

    conn = sqlite3.connect('usuarios.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM usuarios WHERE usuario = ? AND password = ?', (usuario, password))
    usuario_logueado = cursor.fetchone()
    conn.close()

    if not usuario_logueado:
        messagebox.showerror("Error", "Usuario o contraseña incorrectos.")
        return

    # Mostrar la pantalla de acceso a módulos
    mostrar_menu_principal(usuario_logueado)

# Función para mostrar la pantalla de acceso a módulos
def mostrar_menu_principal(usuario_logueado):
    id_usuario, usuario, password, rol, acceso_floristeria,  acceso_inventario, acceso_pedidos, acceso_saldo, acceso_status, acceso_tickets = usuario_logueado

    # Ocultar la pantalla de inicio de sesión
    login_window.withdraw()

    # Crear la pantalla de acceso a módulos
    menu_window = tk.Toplevel(root)
    menu_window.title("Menú Principal")
    menu_window.geometry("400x300")
    menu_window.configure(bg="#f0f0f0")

    # Manejar el cierre de la ventana de menú
    def cerrar_menu():
        menu_window.destroy()
        login_window.deiconify()  # Mostrar la pantalla de inicio de sesión nuevamente

    menu_window.protocol("WM_DELETE_WINDOW", cerrar_menu)  # Asociar el evento de cierre

    tk.Label(menu_window, text=f"Bienvenido, {usuario} ({rol})", bg="#f0f0f0", font=("Arial", 12, "bold")).pack(pady=10)

    if acceso_floristeria:
        tk.Button(menu_window, text="Floristeria", command=lambda: abrir_modulo("floristeria.py"), width=20).pack(pady=5)
    if acceso_inventario:
        tk.Button(menu_window, text="Módulo de Inventario", command=lambda: abrir_modulo("modulo_inventario.py"), width=20).pack(pady=5)
    if acceso_pedidos:
        tk.Button(menu_window, text="Módulo de Pedidos", command=lambda: abrir_modulo("modulo_pedidos.py"), width=20).pack(pady=5)
    if acceso_saldo:
        tk.Button(menu_window, text="Módulo de Saldo", command=lambda: abrir_modulo("modulo_saldo.py"), width=20).pack(pady=5)
    if acceso_status:
        tk.Button(menu_window, text="Módulo de Status", command=lambda: abrir_modulo("modulo_status.py"), width=20).pack(pady=5)
    if acceso_tickets:
        tk.Button(menu_window, text="Módulo de Tickets", command=lambda: abrir_modulo("modulo_tickets.py"), width=20).pack(pady=5)

    tk.Button(menu_window, text="Cerrar Sesión", command=cerrar_menu, width=20).pack(pady=20)

# Función para abrir un módulo externo
def abrir_modulo(modulo):
    try:
        # Verificar si el archivo existe
        if not os.path.isfile(modulo):
            messagebox.showerror("Error", f"No se encontró el archivo '{modulo}'.")
            return

        # Ejecutar el script externo usando subprocess
        subprocess.Popen(["python", modulo])
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error al abrir el módulo: {e}")

# Función para cerrar la aplicación completamente
def cerrar_aplicacion():
    root.destroy()  # Cerrar la ventana principal y terminar el programa

# Configuración de la interfaz gráfica
root = tk.Tk()
root.withdraw()  # Ocultar la ventana principal

# Crear la base de datos
crear_base_datos()

# Pantalla de inicio de sesión
login_window = tk.Toplevel(root)
login_window.title("Inicio de Sesión")
login_window.geometry("300x200")
login_window.configure(bg="#f0f0f0")

# Manejar el cierre de la ventana de inicio de sesión
def cerrar_login():
    cerrar_aplicacion()  # Cerrar la aplicación completamente

login_window.protocol("WM_DELETE_WINDOW", cerrar_login)  # Asociar el evento de cierre

tk.Label(login_window, text="Inicio de Sesión", bg="#f0f0f0", font=("Arial", 12, "bold")).pack(pady=10)

tk.Label(login_window, text="Usuario:", bg="#f0f0f0", font=("Arial", 10)).pack(pady=5)
entry_usuario = tk.Entry(login_window, width=20, font=("Arial", 10))
entry_usuario.pack()

tk.Label(login_window, text="Contraseña:", bg="#f0f0f0", font=("Arial", 10)).pack(pady=5)
entry_password = tk.Entry(login_window, width=20, font=("Arial", 10), show="*")
entry_password.pack()

tk.Button(login_window, text="Iniciar Sesión", command=iniciar_sesion, width=15).pack(pady=10)

# Ejecutar la aplicación
root.mainloop()