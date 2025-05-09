import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess  # Para ejecutar el módulo externo
from dotenv import load_dotenv # para ejecutar las variables de ambiente
import os

load_dotenv()  # Carga las variables desde .env

# Acceder a las variables .env
python_command = os.getenv("PYTHON_COMMAND")

# Configuración de la ventana principal
root = tk.Tk()
root.title("Menu - Floristería")
root.geometry("250x210")  # Tamaño inicial de la ventana
root.resizable(True, True)

# Estilo personalizado
style = ttk.Style()
style.theme_use("clam")  # Tema moderno
style.configure("TLabel", font=("Arial", 10), padding=5)
style.configure("TButton", font=("Arial", 10), padding=5)
style.configure("Treeview", font=("Arial", 10), rowheight=25)
style.configure("Treeview.Heading", font=("Arial", 10, "bold"))

# Marco principal con scroll
canvas = tk.Canvas(root)
canvas.pack(side="left", fill="both", expand=True)

# Configurar el canvas
canvas.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

# Frame interno para el formulario
main_frame = ttk.Frame(canvas, padding=10)
canvas.create_window((0, 0), window=main_frame, anchor="nw")

# Función para abrir la floristeria
def abrir_floristeria():
  try:
    # Ejecutar el script floristeria.py
    subprocess.run([f"{python_command}", "./floristeria.py"], check=True)
  except FileNotFoundError:
    messagebox.showerror("Error", "No se encontró el archivo floristeria.py.")
  except subprocess.CalledProcessError as e:
    messagebox.showerror("Error", f"Ocurrió un error al ejecutar floristeria.py: {e}")

# Función para abrir el modulo_inventario.py
def abrir_modulo_inventario():
  try:
    # Ejecutar el script modulo_inventario.py
    subprocess.run([f"{python_command}", "./modulo_inventario.py"], check=True)
  except FileNotFoundError:
    messagebox.showerror("Error", "No se encontró el archivo modulo_inventario.py.")
  except subprocess.CalledProcessError as e:
    messagebox.showerror("Error", f"Ocurrió un error al ejecutar modulo_inventario.py: {e}")

# Función para abrir el modulo_pedidos.py
def abrir_modulo_pedidos():
  try:
    # Ejecutar el script modulo_status.py
    subprocess.run([f"{python_command}", "./modulo_pedidos.py"], check=True)
  except FileNotFoundError:
    messagebox.showerror("Error", "No se encontró el archivo modulo_pedidos.py.")
  except subprocess.CalledProcessError as e:
    messagebox.showerror("Error", f"Ocurrió un error al ejecutar modulo_pedidos.py: {e}")

# Función para abrir el modulo_saldo.py
def abrir_modulo_saldo():
  try:
    # Ejecutar el script modulo_saldo.py
    subprocess.run([f"{python_command}", "./modulo_saldo.py"], check=True)
  except FileNotFoundError:
    messagebox.showerror("Error", "No se encontró el archivo modulo_saldo.py.")
  except subprocess.CalledProcessError as e:
    messagebox.showerror("Error", f"Ocurrió un error al ejecutar modulo_saldo.py: {e}")

# Función para abrir el modulo_status.py
def abrir_modulo_status():
  try:
    # Ejecutar el script modulo_status.py
    subprocess.run([f"{python_command}", "./modulo_status.py"], check=True)
  except FileNotFoundError:
    messagebox.showerror("Error", "No se encontró el archivo modulo_status.py.")
  except subprocess.CalledProcessError as e:
    messagebox.showerror("Error", f"Ocurrió un error al ejecutar modulo_status.py: {e}")

# Función para abrir el módulo de tickets
def abrir_modulo_tickets():
  try:
    # Ejecutar el script Modulo_tickets.py
    subprocess.run([f"{python_command}", "./modulo_tickets.py"], check=True)
  except FileNotFoundError:
    messagebox.showerror("Error", "No se encontró el archivo modulo_tickets.py.")
  except subprocess.CalledProcessError as e:
    messagebox.showerror("Error", f"Ocurrió un error al ejecutar modulo_tickets.py: {e}")

# Botones
btn_frame = ttk.Frame(main_frame)
btn_frame.pack(fill="x", pady=10)
ttk.Label(btn_frame, text="Menu de la Floristeria", font=("Arial", 15, "bold")).grid(row=0, column=0, padx=5, pady=5, sticky="w", columnspan=2)
ttk.Button(btn_frame, text="Abrir Floristeria", command=abrir_floristeria).grid(row=1, column=0, padx=5, pady=5, sticky="w")
ttk.Button(btn_frame, text="Abrir Inventario", command=abrir_modulo_inventario).grid(row=2, column=0, padx=5, pady=5, sticky="w")
ttk.Button(btn_frame, text="Abrir Pedidos", command=abrir_modulo_pedidos).grid(row=3, column=0, padx=5, pady=5, sticky="w")
ttk.Button(btn_frame, text="Abrir Saldo", command=abrir_modulo_saldo).grid(row=1, column=1, padx=5, pady=5, sticky="w")
ttk.Button(btn_frame, text="Abrir Status", command=abrir_modulo_status).grid(row=2, column=1, padx=5, pady=5, sticky="w")
ttk.Button(btn_frame, text="Abrir Tickets", command=abrir_modulo_tickets).grid(row=3, column=1, padx=5, pady=5, sticky="w")

# Ejecutar la aplicación
root.mainloop()
