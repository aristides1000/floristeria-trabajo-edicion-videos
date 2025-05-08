import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
from datetime import datetime
import subprocess  # Para ejecutar el módulo externo

# Función para conectar a la base de datos
def conectar_db():
  conn = sqlite3.connect("floristeria.db")
  cursor = conn.cursor()
  # Crear tabla de pedidos si no existe
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
                      descripcion TEXT,
                      costo_adicional REAL,
                      costo_total REAL,
                      estado TEXT)''')
  conn.commit()
  conn.close()

def calcular_saldo_transferencia():
  try:
    conn = sqlite3.connect("floristeria.db")
    cursor = conn.cursor()
    fecha_hora_inicial = f"{entry_fecha_inicial.get()} {hora_inicial_var.get()}"
    fecha_hora_final = f"{entry_fecha_final.get()} {hora_inicial_var.get()}"
    cursor.execute("SELECT SUM(costo_total) FROM pedidos WHERE (fecha_hora BETWEEN ? AND ?) AND forma_pago = 'Transferencia'", (fecha_hora_inicial, fecha_hora_final))
    resultado = cursor.fetchone()[0]
    saldo_transferencia = resultado if resultado else 0.0  # Si no hay pedidos, el costo es 0.0
    saldo_transferencia_var.set(round(saldo_transferencia, 2))  # Actualizar la variable con el costo acumulado
  except sqlite3.Error as e:
    messagebox.showerror("Error", f"Ocurrió un error al calcular el costo acumulado: {fecha_hora_inicial} {fecha_hora_final} {e}")
  finally:
    conn.close()

def calcular_saldo_pago_movil():
  try:
    conn = sqlite3.connect("floristeria.db")
    cursor = conn.cursor()
    fecha_hora_inicial = f"{entry_fecha_inicial.get()} {hora_inicial_var.get()}"
    fecha_hora_final = f"{entry_fecha_final.get()} {hora_inicial_var.get()}"
    cursor.execute("SELECT SUM(costo_total) FROM pedidos WHERE (fecha_hora BETWEEN ? AND ?) AND forma_pago = 'PagoMóvil'", (fecha_hora_inicial, fecha_hora_final))
    resultado = cursor.fetchone()[0]
    saldo_pago_movil = resultado if resultado else 0.0  # Si no hay pedidos, el costo es 0.0
    saldo_pago_movil_var.set(round(saldo_pago_movil, 2))  # Actualizar la variable con el costo acumulado
  except sqlite3.Error as e:
    messagebox.showerror("Error", f"Ocurrió un error al calcular el costo acumulado: {fecha_hora_inicial} {fecha_hora_final} {e}")
  finally:
    conn.close()

def calcular_saldo_efectivo():
  try:
    conn = sqlite3.connect("floristeria.db")
    cursor = conn.cursor()
    fecha_hora_inicial = f"{entry_fecha_inicial.get()} {hora_inicial_var.get()}"
    fecha_hora_final = f"{entry_fecha_final.get()} {hora_inicial_var.get()}"
    cursor.execute("SELECT SUM(costo_total) FROM pedidos WHERE (fecha_hora BETWEEN ? AND ?) AND forma_pago = 'Efectivo'", (fecha_hora_inicial, fecha_hora_final))
    resultado = cursor.fetchone()[0]
    saldo_efectivo = resultado if resultado else 0.0  # Si no hay pedidos, el costo es 0.0
    saldo_efectivo_var.set(round(saldo_efectivo, 2))  # Actualizar la variable con el costo acumulado
  except sqlite3.Error as e:
    messagebox.showerror("Error", f"Ocurrió un error al calcular el costo acumulado: {fecha_hora_inicial} {fecha_hora_final} {e}")
  finally:
    conn.close()

def calcular_saldo_zelle():
  try:
    conn = sqlite3.connect("floristeria.db")
    cursor = conn.cursor()
    fecha_hora_inicial = f"{entry_fecha_inicial.get()} {hora_inicial_var.get()}"
    fecha_hora_final = f"{entry_fecha_final.get()} {hora_inicial_var.get()}"
    cursor.execute("SELECT SUM(costo_total) FROM pedidos WHERE (fecha_hora BETWEEN ? AND ?) AND forma_pago = 'Zelle'", (fecha_hora_inicial, fecha_hora_final))
    resultado = cursor.fetchone()[0]
    saldo_zelle = resultado if resultado else 0.0  # Si no hay pedidos, el costo es 0.0
    saldo_zelle_var.set(round(saldo_zelle, 2))  # Actualizar la variable con el costo acumulado
  except sqlite3.Error as e:
    messagebox.showerror("Error", f"Ocurrió un error al calcular el costo acumulado: {fecha_hora_inicial} {fecha_hora_final} {e}")
  finally:
    conn.close()

def calcular_saldo_por_cobrar():
  try:
    conn = sqlite3.connect("floristeria.db")
    cursor = conn.cursor()
    fecha_hora_inicial = f"{entry_fecha_inicial.get()} {hora_inicial_var.get()}"
    fecha_hora_final = f"{entry_fecha_final.get()} {hora_inicial_var.get()}"
    cursor.execute("SELECT SUM(costo_total) FROM pedidos WHERE (fecha_hora BETWEEN ? AND ?) AND forma_pago = 'Por Cobrar'", (fecha_hora_inicial, fecha_hora_final))
    resultado = cursor.fetchone()[0]
    saldo_por_cobrar = resultado if resultado else 0.0  # Si no hay pedidos, el costo es 0.0
    saldo_por_cobrar_var.set(round(saldo_por_cobrar, 2))  # Actualizar la variable con el costo acumulado
  except sqlite3.Error as e:
    messagebox.showerror("Error", f"Ocurrió un error al calcular el costo acumulado: {fecha_hora_inicial} {fecha_hora_final} {e}")
  finally:
    conn.close()

def calcular_saldo_total_menos_por_cobrar():
  try:
    conn = sqlite3.connect("floristeria.db")
    cursor = conn.cursor()
    fecha_hora_inicial = f"{entry_fecha_inicial.get()} {hora_inicial_var.get()}"
    fecha_hora_final = f"{entry_fecha_final.get()} {hora_inicial_var.get()}"
    cursor.execute("SELECT SUM(costo_total) FROM pedidos WHERE (fecha_hora BETWEEN ? AND ?) AND forma_pago <> 'Por Cobrar'", (fecha_hora_inicial, fecha_hora_final))
    resultado = cursor.fetchone()[0]
    saldo_total_menos_por_cobrar = resultado if resultado else 0.0  # Si no hay pedidos, el costo es 0.0
    saldo_total_menos_por_cobrar_var.set(round(saldo_total_menos_por_cobrar, 2))  # Actualizar la variable con el costo acumulado
  except sqlite3.Error as e:
    messagebox.showerror("Error", f"Ocurrió un error al calcular el costo acumulado: {fecha_hora_inicial} {fecha_hora_final} {e}")
  finally:
    conn.close()

def calcular_costo_acumulado_rango_fechas():
  try:
    conn = sqlite3.connect("floristeria.db")
    cursor = conn.cursor()
    fecha_hora_inicial = f"{entry_fecha_inicial.get()} {hora_inicial_var.get()}"
    fecha_hora_final = f"{entry_fecha_final.get()} {hora_inicial_var.get()}"
    cursor.execute("SELECT SUM(costo_total) FROM pedidos WHERE fecha_hora BETWEEN ? AND ?", (fecha_hora_inicial, fecha_hora_final))
    resultado = cursor.fetchone()[0]
    costo_acumulado = resultado if resultado else 0.0  # Si no hay pedidos, el costo es 0.0
    costo_acumulado_var.set(round(costo_acumulado, 2))  # Actualizar la variable con el costo acumulado

    # Calculo de otros saldos
    calcular_saldo_transferencia()
    calcular_saldo_pago_movil()
    calcular_saldo_efectivo()
    calcular_saldo_zelle()
    calcular_saldo_por_cobrar()
    calcular_saldo_total_menos_por_cobrar()

  except sqlite3.Error as e:
    messagebox.showerror("Error", f"Ocurrió un error al calcular el costo acumulado: {fecha_hora_inicial} {fecha_hora_final} {e}")
  finally:
    conn.close()

# Función para limpiar los campos de entrada
def limpiar_campos():
  entry_fecha_inicial.set_date(datetime.now().date())
  hora_inicial_var.set("08:00")
  entry_fecha_final.set_date(datetime.now().date())
  hora_final_var.set("08:00")
  costo_acumulado_var.set(0.0)
  saldo_transferencia_var.set(0.0)
  saldo_pago_movil_var.set(0.0)
  saldo_efectivo_var.set(0.0)
  saldo_zelle_var.set(0.0)
  saldo_por_cobrar_var.set(0.0)
  saldo_total_menos_por_cobrar_var.set(0.0)

# Configuración de la ventana principal
root = tk.Tk()
root.title("Calculo de Costos por rango - Floristería")
root.geometry("341x550")  # Tamaño inicial de la ventana
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

# Sección de entrada de datos
form_frame = ttk.LabelFrame(main_frame, text="Datos del Pedido", padding=10)
form_frame.pack(fill="x", padx=10, pady=10)

entry_fecha_inicial = DateEntry(form_frame, date_pattern='yyyy-MM-dd')
hora_inicial_var = tk.StringVar()
entry_fecha_final = DateEntry(form_frame, date_pattern='yyyy-MM-dd')
hora_final_var = tk.StringVar()

# Botones
btn_frame = ttk.Frame(main_frame)
btn_frame.pack(fill="x", pady=10)
ttk.Button(btn_frame, text="Ver Costo Total", command=calcular_costo_acumulado_rango_fechas).pack(side="left", padx=5)
ttk.Button(btn_frame, text="Limpiar Campos", command=limpiar_campos).pack(side="left", padx=5)

# Bucle para crear los campos del formulario
labels = [
    "Fecha Inicial", "Hora Inicial (HH:MM)", "Fecha Final",
    "Hora Final (HH:MM)", "Saldo Transferencia", "Saldo Pago Movil",
    "Saldo Efectivo", "Saldo Zelle", "Saldo Por Cobrar",
    "Saldo Total Menos Por Cobrar", "Costo Total"
]

row_index = 0

for i, text in enumerate(labels):
  if text == "Fecha Inicial":
    ttk.Label(form_frame, text=text, anchor="w").grid(row=row_index, column=0, padx=5, pady=5, sticky="w")
    entry_fecha_inicial.grid(row=row_index, column=1, padx=5, pady=5, sticky="w")
    row_index += 1
  elif text == "Hora Inicial (HH:MM)":
    ttk.Label(form_frame, text=text, anchor="w").grid(row=row_index, column=0, padx=5, pady=5, sticky="w")
    hora_inicial_var = ttk.Combobox(form_frame, textvariable=hora_inicial_var, values=[f"{h:02d}:00" for h in range(0, 24)], state="readonly", width=10)
    hora_inicial_var.grid(row=row_index, column=1, padx=5, pady=5, sticky="w")
    hora_inicial_var.current(0)
    row_index += 1
  elif text == "Fecha Final":
    ttk.Label(form_frame, text=text, anchor="w").grid(row=row_index, column=0, padx=5, pady=5, sticky="w")
    entry_fecha_final.grid(row=row_index, column=1, padx=5, pady=5, sticky="w")
    row_index += 1
  elif text == "Hora Final (HH:MM)":
    ttk.Label(form_frame, text=text, anchor="w").grid(row=row_index, column=0, padx=5, pady=5, sticky="w")
    hora_final_var = ttk.Combobox(form_frame, textvariable=hora_final_var, values=[f"{h:02d}:00" for h in range(0, 24)], state="readonly", width=10)
    hora_final_var.grid(row=row_index, column=1, padx=5, pady=5, sticky="w")
    hora_final_var.current(0)
    row_index += 1
  elif text == "Saldo Transferencia":
    # Campo para el costo acumulado
    saldo_transferencia_var = tk.DoubleVar(value=0.0)
    ttk.Label(form_frame, text="Saldo Transferencia:", anchor="w").grid(row=row_index, column=0, padx=5, pady=5, sticky="w")
    ttk.Label(form_frame, textvariable=saldo_transferencia_var, anchor="w").grid(row=row_index, column=1, padx=5, pady=5, sticky="w")
    row_index += 1
  elif text == "Saldo Pago Movil":
    # Campo para el costo acumulado
    saldo_pago_movil_var = tk.DoubleVar(value=0.0)
    ttk.Label(form_frame, text="Saldo Pago Movil:", anchor="w").grid(row=row_index, column=0, padx=5, pady=5, sticky="w")
    ttk.Label(form_frame, textvariable=saldo_pago_movil_var, anchor="w").grid(row=row_index, column=1, padx=5, pady=5, sticky="w")
    row_index += 1
  elif text == "Saldo Efectivo":
    # Campo para el costo acumulado
    saldo_efectivo_var = tk.DoubleVar(value=0.0)
    ttk.Label(form_frame, text="Saldo Efectivo:", anchor="w").grid(row=row_index, column=0, padx=5, pady=5, sticky="w")
    ttk.Label(form_frame, textvariable=saldo_efectivo_var, anchor="w").grid(row=row_index, column=1, padx=5, pady=5, sticky="w")
    row_index += 1
  elif text == "Saldo Zelle":
    # Campo para el costo acumulado
    saldo_zelle_var = tk.DoubleVar(value=0.0)
    ttk.Label(form_frame, text="Saldo Zelle:", anchor="w").grid(row=row_index, column=0, padx=5, pady=5, sticky="w")
    ttk.Label(form_frame, textvariable=saldo_zelle_var, anchor="w").grid(row=row_index, column=1, padx=5, pady=5, sticky="w")
    row_index += 1
  elif text == "Saldo Por Cobrar":
    # Campo para el costo acumulado
    saldo_por_cobrar_var = tk.DoubleVar(value=0.0)
    ttk.Label(form_frame, text="Saldo Por Cobrar:", anchor="w").grid(row=row_index, column=0, padx=5, pady=5, sticky="w")
    ttk.Label(form_frame, textvariable=saldo_por_cobrar_var, anchor="w").grid(row=row_index, column=1, padx=5, pady=5, sticky="w")
    row_index += 1
  elif text == "Saldo Total Menos Por Cobrar":
    # Campo para el costo acumulado
    saldo_total_menos_por_cobrar_var = tk.DoubleVar(value=0.0)
    ttk.Label(form_frame, text="Saldo Total Menos Por Cobrar:", anchor="w").grid(row=row_index, column=0, padx=5, pady=5, sticky="w")
    ttk.Label(form_frame, textvariable=saldo_total_menos_por_cobrar_var, anchor="w").grid(row=row_index, column=1, padx=5, pady=5, sticky="w")
    row_index += 1
  elif text == "Costo Total":
    # Campo para el costo acumulado
    costo_acumulado_var = tk.DoubleVar(value=0.0)
    ttk.Label(form_frame, text="Costo Total:", anchor="w").grid(row=row_index, column=0, padx=5, pady=5, sticky="w")
    ttk.Label(form_frame, textvariable=costo_acumulado_var, anchor="w").grid(row=row_index, column=1, padx=5, pady=5, sticky="w")
    row_index += 1

# Ejecutar la aplicación
root.mainloop()