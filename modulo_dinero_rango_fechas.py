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
                      nota TEXT,
                      costo_adicional REAL,
                      costo_total REAL,
                      estado TEXT)''')
  conn.commit()
  conn.close()

def calcular_costo_acumulado():
  try:
    conn = sqlite3.connect("floristeria.db")
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(costo + costo_adicional) FROM pedidos")
    resultado = cursor.fetchone()[0]
    costo_acumulado = resultado if resultado else 0.0  # Si no hay pedidos, el costo es 0.0
    costo_acumulado_var.set(round(costo_acumulado, 2))  # Actualizar la variable con el costo acumulado
  except sqlite3.Error as e:
    messagebox.showerror("Error", f"Ocurrió un error al calcular el costo acumulado: {e}")
  finally:
    conn.close()