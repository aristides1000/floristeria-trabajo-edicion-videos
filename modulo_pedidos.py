import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
from datetime import datetime
import csv
import subprocess  # Para ejecutar el módulo externo
from dotenv import load_dotenv # para ejecutar las variables de ambiente
import os # Para manejar rutas de archivos

load_dotenv() # Carga las variables desde .env

# Acceder a las variables .env
python_command = os.getenv("PYTHON_COMMAND")

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
                        costo_adicional_dolares REAL,
                        costo_adicional_bolivares REAL,
                        costo_adicional_por_cobrar REAL,
                        costo_total_dolares REAL,
                        costo_total_bolivares REAL,
                        costo_total_por_cobrar REAL,
                        numero_factura INTEGER NOT NULL,
                        estado TEXT)''')
    # Crear tabla de modelos de ramos si no existe
    cursor.execute('''CREATE TABLE IF NOT EXISTS modelos_ramos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nombre_arreglo TEXT NOT NULL,
                        cantidad_rosas INTEGER NOT NULL,
                        cantidad_flores INTEGER NOT NULL,
                        cantidad_extras INTEGER NOT NULL,
                        imagen TEXT,
                        precio_venta REAL NOT NULL)''')
    conn.commit()
    conn.close()

# Función para cargar los modelos de ramos en el Combobox
def cargar_modelos_ramos():
    try:
        conn = sqlite3.connect("floristeria.db")
        cursor = conn.cursor()
        cursor.execute("SELECT nombre_arreglo FROM modelos_ramos")
        modelos = [row[0] for row in cursor.fetchall()]
        modelo_ramo_combobox['values'] = modelos
        if modelos:
            modelo_ramo_combobox.current(0)
    except sqlite3.Error as e:
        messagebox.showerror("Error", f"Ocurrió un error al cargar los modelos: {e}")
    finally:
        conn.close()

# Función para actualizar el costo en dolares cuando se selecciona un modelo
def actualizar_costo_dolares(event):
    modelo_seleccionado = modelo_ramo_var.get()
    if modelo_seleccionado:
        try:
            conn = sqlite3.connect("floristeria.db")
            cursor = conn.cursor()
            cursor.execute("SELECT precio_venta FROM modelos_ramos WHERE nombre_arreglo=?", (modelo_seleccionado,))
            resultado = cursor.fetchone()
            if resultado:
                entry_costo_dolares.delete(0, tk.END)
                entry_costo_dolares.insert(0, resultado[0])
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Ocurrió un error al obtener el precio: {e}")
        finally:
            conn.close()

# Función para calcular el costo en dolares acumulado
def calcular_costo_dolares_acumulado():
    try:
        conn = sqlite3.connect("floristeria.db")
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(costo_dolares + costo_adicional_dolares) FROM pedidos")
        resultado = cursor.fetchone()[0]
        costo_dolares_acumulado = resultado if resultado else 0.0  # Si no hay pedidos, el costo es 0.0
        costo_dolares_acumulado_var.set(round(costo_dolares_acumulado, 2))  # Actualizar la variable con el costo en dolares acumulado
    except sqlite3.Error as e:
        messagebox.showerror("Error", f"Ocurrió un error al calcular el costo en dolares acumulado: {e}")
    finally:
        conn.close()

# Función para calcular el costo en bolivares acumulado
def calcular_costo_bolivares_acumulado():
    try:
        conn = sqlite3.connect("floristeria.db")
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(costo_bolivares + costo_adicional_bolivares) FROM pedidos")
        resultado = cursor.fetchone()[0]
        costo_bolivares_acumulado = resultado if resultado else 0.0  # Si no hay pedidos, el costo es 0.0
        costo_bolivares_acumulado_var.set(round(costo_bolivares_acumulado, 2))  # Actualizar la variable con el costo en bolivares acumulado
    except sqlite3.Error as e:
        messagebox.showerror("Error", f"Ocurrió un error al calcular el costo en bolivares acumulado: {e}")
    finally:
        conn.close()

# Función para calcular el costo por cobrar acumulado
def calcular_costo_por_cobrar_acumulado():
    try:
        conn = sqlite3.connect("floristeria.db")
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(costo_por_cobrar + costo_adicional_por_cobrar) FROM pedidos")
        resultado = cursor.fetchone()[0]
        costo_por_cobrar_acumulado = resultado if resultado else 0.0  # Si no hay pedidos, el costo es 0.0
        costo_por_cobrar_acumulado_var.set(round(costo_por_cobrar_acumulado, 2))  # Actualizar la variable con el costo por cobrar acumulado
    except sqlite3.Error as e:
        messagebox.showerror("Error", f"Ocurrió un error al calcular el costo por cobrar acumulado: {e}")
    finally:
        conn.close()

# Función para agregar un pedido
def agregar_pedido():
    telefono_completo = entry_telefono.get() # Combinar "+" y número de teléfono
    fecha_hora = f"{entry_fecha.get()} {hora_var.get()}"
    fecha_hora_entrega = f"{entry_entrega.get()} {hora_entrega_var.get()}"
    enviado_a = entry_enviado_a.get()
    telefono_receptor = entry_telefono_receptor.get()
    descripcion = entry_descripcion.get()
    estado = estado_var.get()
    modelo_ramo = modelo_ramo_var.get()  # Obtener el modelo seleccionado
    # Validar campos obligatorios
    if not (entry_cliente.get() and entry_direccion.get() and modelo_ramo and (entry_costo_dolares.get() or entry_costo_bolivares.get() or entry_costo_por_cobrar.get())):
        messagebox.showerror("Error", "Todos los campos son obligatorios.")
        return
    try:
        # Convertir el costo en dolares a float
        costo_dolares = float(0 if (entry_costo_dolares.get() == "") else entry_costo_dolares.get())
    except ValueError:
        messagebox.showerror("Error", "El costo en dolares debe ser un número válido.")
        return
    try:
        # Convertir el costo en bolivares a float
        costo_bolivares = float(0 if (entry_costo_bolivares.get() == "") else entry_costo_bolivares.get())
    except ValueError:
        messagebox.showerror("Error", "El costo en bolivares debe ser un número válido.")
        return
    try:
        # Convertir el costo por cobrar a float
        costo_por_cobrar = float(0 if (entry_costo_por_cobrar.get() == "") else entry_costo_por_cobrar.get())
    except ValueError:
        messagebox.showerror("Error", "El costo por cobrar debe ser un número válido.")
        return
    try:
        # Convertir el costo_adicional_dolares a float
        costo_adicional_dolares = float(0 if (entry_costo_adicional_dolares.get() == "") else entry_costo_adicional_dolares.get())
    except ValueError:
        messagebox.showerror("Error", "El costo adicional en dolares debe ser un número válido.")
        return
    try:
        # Convertir el costo_adicional_bolivares a float
        costo_adicional_bolivares = float(0 if (entry_costo_adicional_bolivares.get() == "") else entry_costo_adicional_bolivares.get())
    except ValueError:
        messagebox.showerror("Error", "El costo adicional en bolivares debe ser un número válido.")
        return
    try:
        # Convertir el costo_adicional_por_cobrar a float
        costo_adicional_por_cobrar = float(0 if (entry_costo_adicional_por_cobrar.get() == "") else entry_costo_adicional_por_cobrar.get())
    except ValueError:
        messagebox.showerror("Error", "El costo adicional por cobrar debe ser un número válido.")
        return
    try:
        numero_factura = int(entry_numero_factura.get())
    except:
        messagebox.showerror("Error", "El numero de factura debe ser un número válido.")
        return
    try:
        # Convertir el costo total en dolares a float
        costo_total_dolares = float(costo_dolares + costo_adicional_dolares)
    except ValueError:
        messagebox.showerror("Error", "El costo total en dolares debe ser un número válido.")
        return
    try:
        # Convertir el costo total en bolivares a float
        costo_total_bolivares = float(costo_bolivares + costo_adicional_bolivares)
    except ValueError:
        messagebox.showerror("Error", "El costo total en bolivares debe ser un número válido.")
        return
    try:
        # Convertir el costo total por cobrar a float
        costo_total_por_cobrar = float(costo_por_cobrar + costo_adicional_por_cobrar)
    except ValueError:
        messagebox.showerror("Error", "El costo total por cobrar debe ser un número válido.")
        return
    try:
        conn = sqlite3.connect("floristeria.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO pedidos (fecha_hora, cliente, telefono, direccion, modelo_ramo, costo_dolares, costo_bolivares, costo_por_cobrar, fecha_hora_entrega, enviado_a, telefono_receptor, descripcion, costo_adicional_dolares, costo_adicional_bolivares, costo_adicional_por_cobrar, numero_factura, costo_total_dolares, costo_total_bolivares, costo_total_por_cobrar, estado) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (fecha_hora, entry_cliente.get(), telefono_completo, entry_direccion.get(), modelo_ramo, costo_dolares, costo_bolivares, costo_por_cobrar, fecha_hora_entrega, enviado_a, telefono_receptor, descripcion, costo_adicional_dolares, costo_adicional_bolivares, costo_adicional_por_cobrar, numero_factura, costo_total_dolares, costo_total_bolivares, costo_total_por_cobrar, estado))
        conn.commit()
    except sqlite3.Error as e:
        messagebox.showerror("Error", f"Ocurrió un error al agregar el pedido: {e}")
    finally:
        conn.close()
    limpiar_campos()
    mostrar_pedidos()
    calcular_costo_dolares_acumulado() # Calcular el costo en dolares acumulado después de agregar un pedido
    calcular_costo_bolivares_acumulado() # Calcular el costo en bolivares acumulado después de agregar un pedido
    calcular_costo_por_cobrar_acumulado() # Calcular el costo por cobrar acumulado después de agregar un pedido
    messagebox.showinfo("Éxito", "Pedido agregado correctamente.")

# Función para modificar un pedido
def modificar_pedido():
    selected_item = tree.focus()
    if not selected_item:
        messagebox.showerror("Error", "Seleccione un pedido para modificar.")
        return
    telefono_completo = entry_telefono.get()  # Combinar prefijo y número de teléfono
    fecha_hora = f"{entry_fecha.get()} {hora_var.get()}"
    fecha_hora_entrega = f"{entry_entrega.get()} {hora_entrega_var.get()}"
    enviado_a = entry_enviado_a.get()
    telefono_receptor = entry_telefono_receptor.get()
    descripcion = entry_descripcion.get()
    estado = estado_var.get()
    modelo_ramo = modelo_ramo_var.get()  # Obtener el modelo seleccionado
    # Validar campos obligatorios
    if not (entry_cliente.get() and entry_direccion.get() and modelo_ramo and (entry_costo_dolares.get() or entry_costo_bolivares.get() or entry_costo_por_cobrar.get())):
        messagebox.showerror("Error", "Todos los campos son obligatorios.")
        return
    try:
        # Convertir el costo en dolares a float
        costo_dolares = float(0 if (entry_costo_dolares.get() == "") else entry_costo_dolares.get())
    except ValueError:
        messagebox.showerror("Error", "El costo en dolares debe ser un número válido.")
        return
    try:
        # Convertir el costo en bolivares a float
        costo_bolivares = float(0 if (entry_costo_bolivares.get() == "") else entry_costo_bolivares.get())
    except ValueError:
        messagebox.showerror("Error", "El costo en bolivares debe ser un número válido.")
        return
    try:
        # Convertir el costo por cobrar a float
        costo_por_cobrar = float(0 if (entry_costo_por_cobrar.get() == "") else entry_costo_por_cobrar.get())
    except ValueError:
        messagebox.showerror("Error", "El costo por cobrar debe ser un número válido.")
        return
    try:
        # Convertir el costo_adicional_dolares a float
        costo_adicional_dolares = float(0 if (entry_costo_adicional_dolares.get() == "") else entry_costo_adicional_dolares.get())
    except ValueError:
        messagebox.showerror("Error", "El costo adicional en dolares debe ser un número válido.")
        return
    try:
        # Convertir el costo_adicional_bolivares a float
        costo_adicional_bolivares = float(0 if (entry_costo_adicional_bolivares.get() == "") else entry_costo_adicional_bolivares.get())
    except ValueError:
        messagebox.showerror("Error", "El costo adicional en bolivares debe ser un número válido.")
        return
    try:
        # Convertir el costo_adicional_por_cobrar a float
        costo_adicional_por_cobrar = float(0 if (entry_costo_adicional_por_cobrar.get() == "") else entry_costo_adicional_por_cobrar.get())
    except ValueError:
        messagebox.showerror("Error", "El costo adicional por cobrar debe ser un número válido.")
        return
    try:
        numero_factura = int(entry_numero_factura.get())
    except:
        messagebox.showerror("Error", "El numero de factura debe ser un número válido.")
        return
    try:
        # Convertir el costo_total_dolares a float
        costo_total_dolares = float(costo_dolares + costo_adicional_dolares)
    except ValueError:
        messagebox.showerror("Error", "El costo total en dolares debe ser un número válido.")
        return
    try:
        # Convertir el costo_total_bolivares a float
        costo_total_bolivares = float(costo_bolivares + costo_adicional_bolivares)
    except ValueError:
        messagebox.showerror("Error", "El costo total en bolivares debe ser un número válido.")
        return
    try:
        # Convertir el costo_total_por_cobrar a float
        costo_total_por_cobrar = float(costo_por_cobrar + costo_adicional_por_cobrar)
    except ValueError:
        messagebox.showerror("Error", "El costo total por cobrar debe ser un número válido.")
        return
    try:
        conn = sqlite3.connect("floristeria.db")
        cursor = conn.cursor()
        pedido_id = tree.item(selected_item)['values'][0]
        cursor.execute("UPDATE pedidos SET fecha_hora=?, cliente=?, telefono=?, direccion=?, modelo_ramo=?, costo_dolares=?, costo_bolivares=?, costo_por_cobrar=?, fecha_hora_entrega=?, enviado_a=?, telefono_receptor=?, descripcion=?, costo_adicional_dolares=?, costo_adicional_bolivares=?, costo_adicional_por_cobrar=?, numero_factura=?, costo_total_dolares=?, costo_total_bolivares=?, costo_total_por_cobrar=?, estado=? WHERE id=?",
                        (fecha_hora, entry_cliente.get(), telefono_completo, entry_direccion.get(), modelo_ramo, costo_dolares, costo_bolivares, costo_por_cobrar, fecha_hora_entrega, enviado_a, telefono_receptor, descripcion, costo_adicional_dolares, costo_adicional_bolivares, costo_adicional_por_cobrar, numero_factura, costo_total_dolares, costo_total_bolivares, costo_total_por_cobrar, estado, pedido_id))
        conn.commit()
    except sqlite3.Error as e:
        messagebox.showerror("Error", f"Ocurrió un error al modificar el pedido: {e}")
    finally:
        conn.close()
    limpiar_campos()
    mostrar_pedidos()
    calcular_costo_dolares_acumulado()  # Calcular el costo acumulado en dolares después de modificar un pedido
    calcular_costo_bolivares_acumulado()  # Calcular el costo acumulado en bolivares después de modificar un pedido
    calcular_costo_por_cobrar_acumulado()  # Calcular el costo acumulado por cobrar después de modificar un pedido

    messagebox.showinfo("Éxito", "Pedido modificado correctamente.")

# Función para eliminar un pedido
def eliminar_pedido():
    selected_item = tree.focus()
    if not selected_item:
        messagebox.showerror("Error", "Seleccione un pedido para eliminar.")
        return
    try:
        conn = sqlite3.connect("floristeria.db")
        cursor = conn.cursor()
        pedido_id = tree.item(selected_item)['values'][0]
        cursor.execute("DELETE FROM pedidos WHERE id=?", (pedido_id,))
        conn.commit()
    except sqlite3.Error as e:
        messagebox.showerror("Error", f"Ocurrió un error al eliminar el pedido: {e}")
    finally:
        conn.close()
    limpiar_campos()
    mostrar_pedidos()
    calcular_costo_dolares_acumulado()  # Calcular el costo en dolares acumulado después de eliminar un pedido
    calcular_costo_bolivares_acumulado()  # Calcular el costo en bolivares acumulado después de eliminar un pedido
    calcular_costo_por_cobrar_acumulado()  # Calcular el costo por cobrar acumulado después de eliminar un pedido

    messagebox.showinfo("Éxito", "Pedido eliminado correctamente.")

# Función para mostrar los pedidos en la tabla
def mostrar_pedidos():
    # Limpiar la tabla antes de cargar los datos
    for row in tree.get_children():
        tree.delete(row)
    try:
        conn = sqlite3.connect("floristeria.db")
        cursor = conn.cursor()
        """ cursor.execute("SELECT * FROM pedidos") """
        cursor.execute("SELECT id, fecha_hora, cliente, telefono, direccion, modelo_ramo, costo_dolares, costo_bolivares, costo_por_cobrar, fecha_hora_entrega, enviado_a, telefono_receptor, descripcion, costo_adicional_dolares, costo_adicional_bolivares, costo_adicional_por_cobrar, numero_factura, costo_total_dolares, costo_total_bolivares, costo_total_por_cobrar, estado FROM pedidos;")
        rows = cursor.fetchall()
        # Definir tags para los colores de fondo
        tree.tag_configure("en_proceso", background="#33f6ff")  # azul claro
        tree.tag_configure("enviado", background="#90EE90")     # Verde claro
        tree.tag_configure("armado", background="#f5ef42")      # amarillo
        for row in rows:
            # Determinar el tag según el estado del pedido
            estado = row[20]  # Última columna: estado
            if (estado == "En Proceso"):
                tag = "en_proceso"
            elif (estado == "Enviado"):
                tag = "enviado"
            else:
                tag = "armado"
            # Insertar la fila con el tag correspondiente
            tree.insert("", tk.END, values=row, tags=(tag,))
    except sqlite3.Error as e:
        messagebox.showerror("Error", f"Ocurrió un error al cargar los pedidos: {e}")
    finally:
        conn.close()

# Función para cargar los datos de un pedido seleccionado en los campos de entrada
def cargar_pedido(event):
    selected_item = tree.focus()
    if selected_item:
        pedido = tree.item(selected_item)['values']
        try:
            # Cargar datos en los campos del formulario SIN VALIDACIONES
            entry_fecha.set_date(datetime.strptime(pedido[1].split()[0], "%Y-%m-%d").date())  # Fecha del pedido
            hora_var.set(pedido[1].split()[1])  # Hora del pedido
            entry_cliente.delete(0, tk.END)
            entry_cliente.insert(0, pedido[2])  # Cliente
            # Manejar el número de teléfono
            telefono_completo = f"+{pedido[3]}"  # Agregar el "+" al principio de la cadena
            entry_telefono.delete(0, tk.END)
            entry_telefono.insert(0, telefono_completo)  # Mostrar el teléfono tal como está
            entry_direccion.delete(0, tk.END)
            entry_direccion.insert(0, pedido[4])  # Dirección
            modelo_ramo_var.set(pedido[5])  # Modelo del ramo
            entry_costo_dolares.delete(0, tk.END)
            entry_costo_dolares.insert(0, pedido[6])  # Costo en Dolares
            entry_costo_bolivares.delete(0, tk.END)
            entry_costo_bolivares.insert(0, pedido[7])  # Costo en Bolivares
            entry_costo_por_cobrar.delete(0, tk.END)
            entry_costo_por_cobrar.insert(0, pedido[8])  # Costo por Cobrar
            entry_entrega.set_date(datetime.strptime(pedido[9].split()[0], "%Y-%m-%d").date())  # Fecha de entrega
            hora_entrega_var.set(pedido[9].split()[1])  # Hora de entrega
            entry_enviado_a.delete(0, tk.END)
            entry_enviado_a.insert(0, pedido[10])  # Enviado a
            entry_telefono_receptor.delete(0, tk.END)
            entry_telefono_receptor.insert(0, f"+{pedido[11]}")
            entry_descripcion.delete(0, tk.END)
            entry_descripcion.insert(0, pedido[12])
            entry_costo_adicional_dolares.delete(0, tk.END)
            entry_costo_adicional_dolares.insert(0, pedido[13])  # Costo Adicional en Dolares
            entry_costo_adicional_bolivares.delete(0, tk.END)
            entry_costo_adicional_bolivares.insert(0, pedido[14])  # Costo Adicional en Bolivares
            entry_costo_adicional_por_cobrar.delete(0, tk.END)
            entry_costo_adicional_por_cobrar.insert(0, pedido[15])  # Costo Adicional por Cobrar
            entry_numero_factura.delete(0, tk.END)
            entry_numero_factura.insert(0, pedido[16])  # Numero Factura
            entry_costo_total_dolares.delete(0, tk.END)
            entry_costo_total_dolares.insert(0, pedido[17])  # Costo Total en Dolares
            entry_costo_total_bolivares.delete(0, tk.END)
            entry_costo_total_bolivares.insert(0, pedido[18])  # Costo Total en Bolivares
            entry_costo_total_por_cobrar.delete(0, tk.END)
            entry_costo_total_por_cobrar.insert(0, pedido[19])  # Costo Total por Cobrar
            estado_var.set(pedido[20])  # Estado del pedido
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al cargar los datos: {e}")

# Función para limpiar los campos de entrada
def limpiar_campos():
    entry_fecha.set_date(datetime.now().date())  # Establecer la fecha actual
    hora_var.set("08:00")  # Establecer una hora predeterminada
    entry_cliente.delete(0, tk.END)
    entry_telefono.delete(0, tk.END)
    entry_direccion.delete(0, tk.END)
    modelo_ramo_var.set("")
    entry_costo_dolares.delete(0, tk.END)
    entry_costo_bolivares.delete(0, tk.END)
    entry_costo_por_cobrar.delete(0, tk.END)
    entry_entrega.set_date(datetime.now().date())  # Establecer la fecha actual
    hora_entrega_var.set("08:00")  # Establecer una hora predeterminada
    entry_enviado_a.delete(0, tk.END)
    entry_telefono_receptor.delete(0, tk.END)
    entry_descripcion.delete(0, tk.END)
    entry_costo_adicional_dolares.delete(0, tk.END)
    entry_costo_adicional_bolivares.delete(0, tk.END)
    entry_costo_adicional_por_cobrar.delete(0, tk.END)
    entry_numero_factura.delete(0, tk.END)
    entry_costo_total_dolares.delete(0, tk.END)
    entry_costo_total_bolivares.delete(0, tk.END)
    entry_costo_total_por_cobrar.delete(0, tk.END)
    estado_var.set("En Proceso")  # Estado predeterminado

# Función para exportar datos a CSV
def exportar_a_csv():
    try:
        with open("pedidos.csv", mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["ID", "Fecha y Hora", "Cliente", "Teléfono", "Dirección", "Modelo del Ramo", "Costo en Dolares", "Costo en Bolivares", "Costo por Cobrar", "Fecha y Hora Entrega", "Enviado a", "Descripcion", "Costo Adicional en Dolares", "Costo Adicional en Bolivares", "Costo Adicional por Cobrar", "Numero de Factura", "Costo Total en Dolares", "Costo Total en Bolivares", "Costo Total por Cobrar", "Estado"])
            for row in tree.get_children():
                writer.writerow(tree.item(row)['values'])
        messagebox.showinfo("Éxito", "Datos exportados correctamente a pedidos.csv")
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error al exportar los datos: {e}")

# Función para buscar pedidos
def buscar_pedidos():
    filtro = entry_busqueda.get().lower()
    for row in tree.get_children():
        tree.delete(row)
    try:
        conn = sqlite3.connect("floristeria.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pedidos WHERE cliente LIKE ? OR estado LIKE ?", (f"%{filtro}%", f"%{filtro}%"))
        for row in cursor.fetchall():
            tree.insert("", tk.END, values=row)
    except sqlite3.Error as e:
        messagebox.showerror("Error", f"Ocurrió un error al buscar los pedidos: {e}")
    finally:
        conn.close()

# Función para abrir la ventana de gestión de modelos de ramos
def abrir_gestion_modelos():
    def agregar_modelo():
        # Validar campos obligatorios
        if not (entry_nombre.get() and entry_rosas.get() and entry_flores.get() and entry_extras.get()):
            messagebox.showerror("Error", "Todos los campos son obligatorios.")
            return
        try:
            cantidad_rosas = int(entry_rosas.get())
            cantidad_flores = int(entry_flores.get())
            cantidad_extras = int(entry_extras.get())
            precio_venta = float(entry_precio.get())
        except ValueError:
            messagebox.showerror("Error", "Las cantidades y el precio deben ser números válidos.")
            return
        if cantidad_rosas < 0 or cantidad_flores < 0 or cantidad_extras < 0 or precio_venta <= 0:
            messagebox.showerror("Error", "Las cantidades deben ser números positivos y el precio debe ser mayor a cero.")
            return
        try:
            conn = sqlite3.connect("floristeria.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO modelos_ramos (nombre_arreglo, cantidad_rosas, cantidad_flores, cantidad_extras, imagen, precio_venta) VALUES (?, ?, ?, ?, ?, ?)",
                            (entry_nombre.get(), cantidad_rosas, cantidad_flores, cantidad_extras, "", precio_venta))
            conn.commit()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Ocurrió un error al agregar el modelo: {e}")
        finally:
            conn.close()
        limpiar_campos_modelos()
        mostrar_modelos()
        messagebox.showinfo("Éxito", "Modelo agregado correctamente.")

    def modificar_modelo():
        selected_item = tree_modelos.focus()
        if not selected_item:
            messagebox.showerror("Error", "Seleccione un modelo para modificar.")
            return
        modelo_id = tree_modelos.item(selected_item)['values'][0]
        # Validar campos obligatorios
        if not (entry_nombre.get() and entry_rosas.get() and entry_flores.get() and entry_extras.get() and entry_precio.get()):
            messagebox.showerror("Error", "Todos los campos son obligatorios.")
            return
        try:
            cantidad_rosas = int(entry_rosas.get())
            cantidad_flores = int(entry_flores.get())
            cantidad_extras = int(entry_extras.get())
            precio_venta = float(entry_precio.get())
        except ValueError:
            messagebox.showerror("Error", "Las cantidades y el precio deben ser números válidos.")
            return
        if cantidad_rosas < 0 or cantidad_flores < 0 or cantidad_extras < 0 or precio_venta <= 0:
            messagebox.showerror("Error", "Las cantidades deben ser números positivos y el precio debe ser mayor a cero.")
            return
        try:
            conn = sqlite3.connect("floristeria.db")
            cursor = conn.cursor()
            cursor.execute("UPDATE modelos_ramos SET nombre_arreglo=?, cantidad_rosas=?, cantidad_flores=?, cantidad_extras=?, precio_venta=? WHERE id=?",
                            (entry_nombre.get(), cantidad_rosas, cantidad_flores, cantidad_extras, precio_venta, modelo_id))
            conn.commit()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Ocurrió un error al modificar el modelo: {e}")
        finally:
            conn.close()
        limpiar_campos_modelos()
        mostrar_modelos()
        messagebox.showinfo("Éxito", "Modelo modificado correctamente.")

    def eliminar_modelo():
        selected_item = tree_modelos.focus()
        if not selected_item:
            messagebox.showerror("Error", "Seleccione un modelo para eliminar.")
            return
        modelo_id = tree_modelos.item(selected_item)['values'][0]
        try:
            conn = sqlite3.connect("floristeria.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM modelos_ramos WHERE id=?", (modelo_id,))
            conn.commit()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Ocurrió un error al eliminar el modelo: {e}")
        finally:
            conn.close()
        limpiar_campos_modelos()
        mostrar_modelos()
        messagebox.showinfo("Éxito", "Modelo eliminado correctamente.")

    def mostrar_modelos():
        for row in tree_modelos.get_children():
            tree_modelos.delete(row)
        try:
            conn = sqlite3.connect("floristeria.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM modelos_ramos")
            for row in cursor.fetchall():
                tree_modelos.insert("", tk.END, values=row)
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Ocurrió un error al cargar los modelos: {e}")
        finally:
            conn.close()

    def cargar_modelo(event):
        selected_item = tree_modelos.focus()
        if selected_item:
            modelo = tree_modelos.item(selected_item)['values']
            entry_nombre.delete(0, tk.END)
            entry_nombre.insert(0, modelo[1])
            entry_rosas.delete(0, tk.END)
            entry_rosas.insert(0, modelo[2])
            entry_flores.delete(0, tk.END)
            entry_flores.insert(0, modelo[3])
            entry_extras.delete(0, tk.END)
            entry_extras.insert(0, modelo[4])
            entry_precio.delete(0, tk.END)
            entry_precio.insert(0, modelo[6])

    def limpiar_campos_modelos():
        entry_nombre.delete(0, tk.END)
        entry_rosas.delete(0, tk.END)
        entry_flores.delete(0, tk.END)
        entry_extras.delete(0, tk.END)
        entry_precio.delete(0, tk.END)

    # Ventana de gestión de modelos
    gestion_modelos_window = tk.Toplevel(root)
    gestion_modelos_window.title("Gestión de Modelos de Ramos")
    gestion_modelos_window.geometry("800x600")
    # Marco principal
    main_frame_modelos = ttk.Frame(gestion_modelos_window, padding=10)
    main_frame_modelos.pack(fill="both", expand=True)
    # Sección de entrada de datos
    form_frame_modelos = ttk.LabelFrame(main_frame_modelos, text="Datos del Modelo", padding=10)
    form_frame_modelos.pack(fill="x", padx=10, pady=10)
    # Variables para los widgets
    entry_nombre = ttk.Entry(form_frame_modelos, width=40)
    entry_rosas = ttk.Entry(form_frame_modelos, width=10)
    entry_flores = ttk.Entry(form_frame_modelos, width=10)
    entry_extras = ttk.Entry(form_frame_modelos, width=10)
    entry_precio = ttk.Entry(form_frame_modelos, width=10)
    # Bucle para crear los campos del formulario
    labels_modelos = [
        "Nombre del Arreglo", "Cantidad de Rosas", "Cantidad de Flores", "Cantidad de Extras", "Precio de Venta"
    ]
    row_index = 0
    for i, text in enumerate(labels_modelos):
        ttk.Label(form_frame_modelos, text=text, anchor="w").grid(row=row_index, column=0, padx=5, pady=5, sticky="w")
        if text == "Nombre del Arreglo":
            entry_nombre.grid(row=row_index, column=1, padx=5, pady=5, sticky="w")
        elif text == "Cantidad de Rosas":
            entry_rosas.grid(row=row_index, column=1, padx=5, pady=5, sticky="w")
        elif text == "Cantidad de Flores":
            entry_flores.grid(row=row_index, column=1, padx=5, pady=5, sticky="w")
        elif text == "Cantidad de Extras":
            entry_extras.grid(row=row_index, column=1, padx=5, pady=5, sticky="w")
        elif text == "Precio de Venta":
            entry_precio.grid(row=row_index, column=1, padx=5, pady=5, sticky="w")
        row_index += 1
    # Botones
    btn_frame_modelos = ttk.Frame(main_frame_modelos)
    btn_frame_modelos.pack(fill="x", pady=10)
    ttk.Button(btn_frame_modelos, text="Agregar Modelo", command=agregar_modelo).pack(side="left", padx=5)
    ttk.Button(btn_frame_modelos, text="Modificar Modelo", command=modificar_modelo).pack(side="left", padx=5)
    ttk.Button(btn_frame_modelos, text="Eliminar Modelo", command=eliminar_modelo).pack(side="left", padx=5)
    # Tabla de modelos
    tree_frame_modelos = ttk.Frame(main_frame_modelos)
    tree_frame_modelos.pack(fill="both", expand=True, pady=10)
    tree_modelos = ttk.Treeview(tree_frame_modelos, columns=("ID", "Nombre", "Rosas", "Flores", "Extras", "Imagen", "Precio"), show="headings")
    for col in tree_modelos['columns']:
        tree_modelos.heading(col, text=col)
        tree_modelos.column(col, width=100, anchor="center")
    tree_modelos.pack(fill="both", expand=True)
    # Asociar la función de carga de datos al hacer clic en un elemento de la tabla
    tree_modelos.bind("<<TreeviewSelect>>", cargar_modelo)
    # Mostrar los modelos iniciales
    mostrar_modelos()

# Función para abrir el módulo de tickets
def abrir_modulo_tickets():
    try:
        # Ejecutar el script Modulo_tickets.py
        subprocess.run([f"{python_command}", "./modulo_tickets.py"], check=True)
    except FileNotFoundError:
        messagebox.showerror("Error", "No se encontró el archivo modulo_tickets.py.")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Ocurrió un error al ejecutar modulo_tickets.py: {e}")

# Conectar a la base de datos
conectar_db()

# Configuración de la ventana principal
root = tk.Tk()
root.title("Gestión de Pedidos - Floristería")
root.geometry("1750x1000")  # Tamaño inicial de la ventana
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

# Barras de desplazamiento para el formulario
scroll_y = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
scroll_y.pack(side="right", fill="y")
scroll_x = ttk.Scrollbar(root, orient="horizontal", command=canvas.xview)
scroll_x.pack(side="bottom", fill="x")

# Configurar el canvas
canvas.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
canvas.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

# Frame interno para el formulario
main_frame = ttk.Frame(canvas, padding=10)
canvas.create_window((0, 0), window=main_frame, anchor="nw")

# Sección de entrada de datos
form_frame = ttk.LabelFrame(main_frame, text="Datos del Pedido", padding=10)
form_frame.pack(fill="x", padx=10, pady=10)

# Variables para los widgets
entry_fecha = DateEntry(form_frame, date_pattern='yyyy-MM-dd')
hora_var = tk.StringVar()
entry_cliente = ttk.Entry(form_frame, width=40)
entry_telefono = ttk.Entry(form_frame, width=20)
entry_direccion = ttk.Entry(form_frame, width=60)
modelo_ramo_var = tk.StringVar()  # Variable para el Combobox de modelos de ramos
entry_costo_dolares = ttk.Entry(form_frame, width=20)
entry_costo_bolivares = ttk.Entry(form_frame, width=20)
entry_costo_por_cobrar = ttk.Entry(form_frame, width=20)
entry_entrega = DateEntry(form_frame, date_pattern='yyyy-MM-dd')
hora_entrega_var = tk.StringVar()
entry_enviado_a = ttk.Entry(form_frame, width=40)
entry_telefono_receptor = ttk.Entry(form_frame, width=20)
entry_descripcion = ttk.Entry(form_frame, width=60)
entry_costo_adicional_dolares = ttk.Entry(form_frame, width=20)
entry_costo_adicional_bolivares = ttk.Entry(form_frame, width=20)
entry_costo_adicional_por_cobrar = ttk.Entry(form_frame, width=20)
entry_numero_factura = ttk.Entry(form_frame, width=10)
entry_costo_total_dolares = ttk.Entry(form_frame, width=20, state="disabled")
entry_costo_total_bolivares = ttk.Entry(form_frame, width=20, state="disabled")
entry_costo_total_por_cobrar = ttk.Entry(form_frame, width=20, state="disabled")
estado_var = tk.StringVar()

# Bucle para crear los campos del formulario
labels = [
    "Fecha del Pedido", "Hora del Pedido (HH:MM)", "Cliente",
    "Teléfono", "Modelo del Ramo",
    "Costo en Dolares", "Costo en Bolivares", "Costo por Cobrar", "Fecha de Entrega", "Hora de Entrega (HH:MM)", "Enviado a", "Teléfono Receptor", "Descripcion", "Costo Adicional en Dolares", "Costo Adicional en Bolivares", "Costo Adicional por Cobrar", "Numero de Factura"
]
row_index = 0  # Índice para controlar las filas
for i, text in enumerate(labels):
    if text == "Teléfono":
        # Etiqueta y entrada para los dígitos del teléfono
        ttk.Label(form_frame, text="Teléfono de quien envía", anchor="w").grid(row=row_index, column=0, padx=5, pady=5, sticky="w")
        entry_telefono.grid(row=row_index, column=1, padx=5, pady=5, sticky="w")
        row_index += 1  # Incrementar fila para la siguiente entrada
        # Etiqueta y entrada para la dirección (debajo del teléfono)
        ttk.Label(form_frame, text="Dirección", anchor="w").grid(row=row_index, column=0, padx=5, pady=5, sticky="w")
        entry_direccion.grid(row=row_index, column=1, columnspan=3, padx=5, pady=5, sticky="ew")  # Expandir horizontalmente
        row_index += 1  # Incrementar fila para la siguiente entrada
    elif text == "Modelo del Ramo":
        # Combobox para seleccionar el modelo del ramo
        ttk.Label(form_frame, text=text, anchor="w").grid(row=row_index, column=0, padx=5, pady=5, sticky="w")
        modelo_ramo_combobox = ttk.Combobox(form_frame, textvariable=modelo_ramo_var, state="readonly", width=40)
        modelo_ramo_combobox.grid(row=row_index, column=1, padx=5, pady=5, sticky="w")
        modelo_ramo_combobox.bind("<<ComboboxSelected>>", actualizar_costo_dolares)  # Actualizar costo en dolares al seleccionar un modelo
        row_index += 1
    elif "Fecha" in text:
        # Entradas para fechas
        ttk.Label(form_frame, text=text, anchor="w").grid(row=row_index, column=0, padx=5, pady=5, sticky="w")
        if text == "Fecha del Pedido":
            entry_fecha.grid(row=row_index, column=1, padx=5, pady=5, sticky="w")
        elif text == "Fecha de Entrega":
            entry_entrega.grid(row=row_index, column=1, padx=5, pady=5, sticky="w")
        row_index += 1
    elif "Hora" in text:
        # Combobox para seleccionar la hora
        ttk.Label(form_frame, text=text, anchor="w").grid(row=row_index, column=0, padx=5, pady=5, sticky="w")
        if text == "Hora del Pedido (HH:MM)":
            hora_combobox = ttk.Combobox(form_frame, textvariable=hora_var, values=[f"{h:02d}:00" for h in range(0, 24)], state="readonly", width=10)
            hora_combobox.grid(row=row_index, column=1, padx=5, pady=5, sticky="w")
            hora_combobox.current(0)
        elif text == "Hora de Entrega (HH:MM)":
            hora_entrega_combobox = ttk.Combobox(form_frame, textvariable=hora_entrega_var, values=[f"{h:02d}:00" for h in range(0, 24)], state="readonly", width=10)
            hora_entrega_combobox.grid(row=row_index, column=1, padx=5, pady=5, sticky="w")
            hora_entrega_combobox.current(0)
        row_index += 1
    elif text == "Enviado a":
        # Entrada para "Enviado a"
        ttk.Label(form_frame, text=text, anchor="w").grid(row=row_index, column=0, padx=5, pady=5, sticky="w")
        entry_enviado_a.grid(row=row_index, column=1, padx=5, pady=5, sticky="w")
        row_index += 1
    elif text == "Teléfono Receptor":
        # Entrada para ""Teléfono Receptor""
        ttk.Label(form_frame, text=text, anchor="w").grid(row=row_index, column=0, padx=5, pady=5, sticky="w")
        entry_telefono_receptor.grid(row=row_index, column=1, padx=5, pady=5, sticky="w")
        row_index += 1
    elif text == "Descripcion":
        # Entrada para "Descripcion"
        ttk.Label(form_frame, text="Descripcion", anchor="w").grid(row=row_index, column=0, padx=5, pady=5, sticky="w")
        entry_descripcion.grid(row=row_index, column=1, columnspan=3, padx=5, pady=5, sticky="ew")  # Expandir horizontalmente
        row_index += 1
    else:
        # Entradas generales
        ttk.Label(form_frame, text=text, anchor="w").grid(row=row_index, column=0, padx=5, pady=5, sticky="w")
        if text == "Cliente":
            entry_cliente.grid(row=row_index, column=1, padx=5, pady=5, sticky="w")
        elif text == "Costo en Dolares":
            entry_costo_dolares.grid(row=row_index, column=1, padx=5, pady=5, sticky="w")
        elif text == "Costo en Bolivares":
            entry_costo_bolivares.grid(row=row_index, column=1, padx=5, pady=5, sticky="w")
        elif text == "Costo por Cobrar":
            entry_costo_por_cobrar.grid(row=row_index, column=1, padx=5, pady=5, sticky="w")
        elif text == "Costo Adicional en Dolares":
            entry_costo_adicional_dolares.grid(row=row_index, column=1, padx=5, pady=5, sticky="w")
        elif text == "Costo Adicional en Bolivares":
            entry_costo_adicional_bolivares.grid(row=row_index, column=1, padx=5, pady=5, sticky="w")
        elif text == "Costo Adicional por Cobrar":
            entry_costo_adicional_por_cobrar.grid(row=row_index, column=1, padx=5, pady=5, sticky="w")
        elif text == "Numero de Factura":
            entry_numero_factura.grid(row=row_index, column=1, padx=5, pady=5, sticky="w")
        """ elif text == "Costo Total en Dolares":
            entry_costo_total_dolares.grid(row=row_index, column=1, padx=5, pady=5, sticky="w") """
        """ elif text == "Costo Total en Bolivares":
            entry_costo_total_bolivares.grid(row=row_index, column=1, padx=5, pady=5, sticky="w") """
        """ elif text == "Costo Total por Cobrar":
            entry_costo_total_por_cobrar.grid(row=row_index, column=1, padx=5, pady=5, sticky="w") """
        row_index += 1

# Campo de estado
ttk.Label(form_frame, text="Estado", anchor="w").grid(row=row_index, column=0, padx=5, pady=5, sticky="w")
estado_combobox = ttk.Combobox(form_frame, textvariable=estado_var, values=["En Proceso", "Enviado", "Armado"], state="readonly", width=20)
estado_combobox.grid(row=row_index, column=1, padx=5, pady=5, sticky="w")
estado_combobox.current(0)
row_index += 1

# Campo para el costo en dolares acumulado
costo_dolares_acumulado_var = tk.DoubleVar(value=0.0)
ttk.Label(form_frame, text="Costo en Dolares Acumulado:", anchor="w").grid(row=row_index, column=0, padx=5, pady=5, sticky="w")
ttk.Label(form_frame, textvariable=costo_dolares_acumulado_var, anchor="w").grid(row=row_index, column=1, padx=5, pady=5, sticky="w")
row_index += 1

# Campo para el costo en bolivares acumulado
costo_bolivares_acumulado_var = tk.DoubleVar(value=0.0)
ttk.Label(form_frame, text="Costo en Bolivares Acumulado:", anchor="w").grid(row=row_index - 1, column=2, padx=5, pady=5, sticky="w")
ttk.Label(form_frame, textvariable=costo_bolivares_acumulado_var, anchor="w").grid(row=row_index - 1, column=3, padx=5, pady=5, sticky="w")
row_index += 1

# Campo para el costo saldo por cobrar
costo_por_cobrar_acumulado_var = tk.DoubleVar(value=0.0)
ttk.Label(form_frame, text="Costo por cobrar en dolares:", anchor="w").grid(row=row_index - 2, column=4, padx=5, pady=5, sticky="w")
ttk.Label(form_frame, textvariable=costo_por_cobrar_acumulado_var, anchor="w").grid(row=row_index - 2, column=5, padx=5, pady=5, sticky="w")
row_index += 1

# Botones
btn_frame = ttk.Frame(main_frame)
btn_frame.pack(fill="x", pady=10)
ttk.Button(btn_frame, text="Agregar Pedido", command=agregar_pedido).pack(side="left", padx=5)
ttk.Button(btn_frame, text="Modificar Pedido", command=modificar_pedido).pack(side="left", padx=5)
ttk.Button(btn_frame, text="Eliminar Pedido", command=eliminar_pedido).pack(side="left", padx=5)
ttk.Button(btn_frame, text="Exportar a CSV", command=exportar_a_csv).pack(side="left", padx=5)
ttk.Button(btn_frame, text="Gestionar Modelos", command=abrir_gestion_modelos).pack(side="left", padx=5)
ttk.Button(btn_frame, text="Refrescar Modelos", command=cargar_modelos_ramos).pack(side="left", padx=5)
ttk.Button(btn_frame, text="Abrir Tickets", command=abrir_modulo_tickets).pack(side="left", padx=5)

# Campo de búsqueda
search_frame = ttk.Frame(main_frame)
search_frame.pack(fill="x", pady=5)
ttk.Label(search_frame, text="Buscar:", anchor="w").pack(side="left", padx=5, pady=5)
entry_busqueda = ttk.Entry(search_frame, width=30)
entry_busqueda.pack(side="left", padx=5, pady=5)
ttk.Button(search_frame, text="Buscar", command=buscar_pedidos).pack(side="left", padx=5)

# Tabla de pedidos
tree_frame = ttk.Frame(main_frame)
tree_frame.pack(fill="both", expand=True, pady=10)
tree = ttk.Treeview(tree_frame, columns=("ID", "Fecha y Hora", "Cliente", "Teléfono Remitente", "Dirección", "Modelo del Ramo", "Costo en Dolares", "Costo en Bolivares", "Costo por Cobrar", "Fecha y Hora Entrega", "Enviado a", "Teléfono Receptor", "Descripcion", "Costo Adicional en Dolares", "Costo Adicional en Bolivares", "Costo Adicional por Cobrar", "Numero de Factura", "Costo Total en Dolares", "Costo Total en Bolivares", "Costo Total por Cobrar", "Estado"), show="headings")
for col in tree['columns']:
    tree.heading(col, text=col)
    tree.column(col, width=120, anchor="center")
tree.pack(fill="both", expand=True)

# Asociar la función de carga de datos al hacer clic en un elemento de la tabla
tree.bind("<<TreeviewSelect>>", cargar_pedido)

# Mostrar los pedidos iniciales
mostrar_pedidos()

# Cargar los modelos de ramos en el Combobox
cargar_modelos_ramos()

# Calcular el costo en dolares acumulado inicial
calcular_costo_dolares_acumulado()

# Calcular el costo en bolivares acumulado inicial
calcular_costo_bolivares_acumulado()

# Calcular el costo por cobrar acumulado inicial
calcular_costo_por_cobrar_acumulado()

# Ejecutar la aplicación
root.mainloop()