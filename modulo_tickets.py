import tkinter as tk
from tkinter import ttk, messagebox, simpledialog  # Importar simpledialog para solicitar entrada
import sqlite3
from fpdf import FPDF  # Para generar PDFs
import os  # Para abrir el archivo PDF

# Crear la base de datos SQLite
def crear_base_datos():
    conn = sqlite3.connect('floristeria.db')
    cursor = conn.cursor()

    # Tabla de pedidos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha_hora TEXT,
            cliente TEXT,
            telefono TEXT,
            direccion TEXT,
            modelo_ramo TEXT,
            costo_dolares REAL,
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

# Función para cargar los pedidos con estado "En Proceso"
def cargar_pedidos():
    tree_pedidos.delete(*tree_pedidos.get_children())
    conn = sqlite3.connect('floristeria.db')
    cursor = conn.cursor()

    # Consulta SQL: Asegurarse de que el orden de las columnas coincida con el de la tabla Treeview
    cursor.execute('''
        SELECT id, cliente, telefono, direccion, delivery_persona, enviado_a, tipo_entrega, descripcion, estado
        FROM pedidos
        WHERE estado = "En Proceso"
    ''')
    rows = cursor.fetchall()
    for row in rows:
        tree_pedidos.insert("", "end", values=row)
    conn.close()

# Función para actualizar el tipo de entrega (Recoger / Delivery)
def actualizar_tipo_entrega():
    seleccion = tree_pedidos.selection()
    if not seleccion:
        messagebox.showwarning("Advertencia", "Seleccione un pedido para actualizar.")
        return

    item_id = tree_pedidos.item(seleccion)["values"][0]
    tipo_entrega = combo_tipo_entrega.get()
    delivery_persona = entry_delivery_persona.get() if tipo_entrega == "Delivery" else "Retiran en Floristería"

    try:
        conn = sqlite3.connect('floristeria.db')
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE pedidos
            SET tipo_entrega = ?, delivery_persona = ?
            WHERE id = ?
        ''', (tipo_entrega, delivery_persona, item_id))
        conn.commit()
        conn.close()

        # Actualizar la tabla de pedidos inmediatamente
        cargar_pedidos()
        limpiar_campos()

        # Generar ticket automáticamente si el tipo de entrega es "Delivery"
        if tipo_entrega == "Delivery":
            generar_ticket_seleccionado(item_id)

        messagebox.showinfo("Éxito", "Tipo de entrega actualizado correctamente.")
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error: {e}")

# Función para generar un ticket en PDF para delivery
def generar_ticket_seleccionado(item_id):
    try:
        conn = sqlite3.connect('floristeria.db')
        cursor = conn.cursor()

        # Consulta SQL: Asegurarse de que el orden de las columnas coincida con el de la tabla Treeview
        cursor.execute('''
            SELECT id, cliente, telefono, direccion, delivery_persona, enviado_a, tipo_entrega, descripcion, estado
            FROM pedidos
            WHERE id = ?
        ''', (item_id,))
        pedido = cursor.fetchone()
        conn.close()

        if not pedido:
            messagebox.showerror("Error", "No se encontró el pedido seleccionado.")
            return

        # Asignar los datos correctamente según el orden de la consulta SQL
        id_pedido, cliente, telefono, direccion, delivery_persona, enviado_a, tipo_entrega, descripcion, estado = pedido

        # Solicitar el nombre del archivo PDF al usuario
        nombre_archivo = simpledialog.askstring(
            "Nombre del Ticket",
            "Ingrese el nombre del ticket (sin extensión):",
            parent=root
        )

        # Validar que el usuario haya ingresado un nombre
        if not nombre_archivo:
            messagebox.showwarning("Advertencia", "No se ingresó un nombre para el ticket. Usando nombre predeterminado.")
            nombre_archivo = "ticket_default"

        # Asegurarse de que el nombre termine con .pdf
        if not nombre_archivo.endswith(".pdf"):
            nombre_archivo += ".pdf"

        # Generar PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("Arial", size=12)

        pdf.cell(200, 10, txt="Ticket de Entrega", ln=True, align="C")
        pdf.ln(10)

        pdf.cell(200, 10, txt=f"ID Pedido: {id_pedido}", ln=True)
        pdf.cell(200, 10, txt=f"Cliente: {cliente}", ln=True)
        pdf.cell(200, 10, txt=f"Teléfono: {telefono}", ln=True)
        pdf.cell(200, 10, txt=f"Dirección: {direccion}", ln=True)
        pdf.cell(200, 10, txt=f"Persona que realiza el Delivery: {delivery_persona}", ln=True)
        pdf.cell(200, 10, txt=f"Enviado a: {enviado_a}", ln=True)
        pdf.cell(200, 10, txt=f"Tipo de Entrega: {tipo_entrega}", ln=True),
        pdf.cell(200, 10, txt=f"Descripcion: {descripcion}", ln=True),
        pdf.cell(200, 10, txt=f"Estado: {estado}", ln=True)

        # Guardar y abrir el PDF
        pdf_path = nombre_archivo
        pdf.output(pdf_path)

        # Abrir el archivo PDF automáticamente
        if os.name == 'nt':  # Windows
            os.startfile(pdf_path)
        elif os.name == 'posix':  # macOS o Linux
            os.system(f"open {pdf_path}" if os.uname().sysname == "Darwin" else f"xdg-open {pdf_path}")

        messagebox.showinfo("Éxito", f"Ticket generado correctamente como '{nombre_archivo}' y abierto para impresión.")
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error al generar el ticket: {e}")

# Función para limpiar los campos de entrada
def limpiar_campos():
    combo_tipo_entrega.set("")
    entry_delivery_persona.delete(0, tk.END)

# Función para actualizar el campo "Persona que realiza el Delivery" según el tipo de entrega
def actualizar_delivery_persona(event):
    tipo_entrega = combo_tipo_entrega.get()
    if tipo_entrega == "Recoger":
        entry_delivery_persona.delete(0, tk.END)
        entry_delivery_persona.insert(0, "Retiran en Floristería")
        entry_delivery_persona.config(state="disabled")  # Deshabilitar edición
    else:
        entry_delivery_persona.config(state="normal")  # Habilitar edición
        entry_delivery_persona.delete(0, tk.END)

# Configuración de la interfaz gráfica
root = tk.Tk()
root.title("Gestión de Pedidos - Floristería")
root.geometry("1150x600")
root.configure(bg="#f0f0f0")  # Fondo claro

# Estilo para los widgets
style = ttk.Style()
style.theme_use("clam")  # Tema moderno
style.configure("TLabel", background="#f0f0f0", font=("Arial", 10))
style.configure("TButton", background="#d3d3d3", foreground="black", font=("Arial", 10, "bold"))
style.map("TButton", background=[("active", "#c0c0c0")])  # Cambio de color al pasar el cursor
style.configure("Treeview", background="white", fieldbackground="white", font=("Arial", 10))
style.configure("Treeview.Heading", font=("Arial", 10, "bold"))

# Crear la base de datos
crear_base_datos()

# Etiquetas y campos de entrada
tk.Label(root, text="Tipo de Entrega:", bg="#f0f0f0", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=10, pady=5, sticky="w")
combo_tipo_entrega = ttk.Combobox(root, values=["Recoger", "Delivery"], state="readonly", width=20)
combo_tipo_entrega.grid(row=0, column=1, padx=10, pady=5, sticky="w")
combo_tipo_entrega.bind("<<ComboboxSelected>>", actualizar_delivery_persona)  # Evento para actualizar el campo

tk.Label(root, text="Persona que realiza el Delivery:", bg="#f0f0f0", font=("Arial", 10, "bold")).grid(row=1, column=0, padx=10, pady=5, sticky="w")
entry_delivery_persona = tk.Entry(root, width=20, font=("Arial", 10))
entry_delivery_persona.grid(row=1, column=1, padx=10, pady=5, sticky="w")

# Botones
frame_botones = tk.Frame(root, bg="#f0f0f0")
frame_botones.grid(row=2, column=0, columnspan=2, pady=10)

btn_actualizar = ttk.Button(frame_botones, text="Actualizar Tipo de Entrega", command=actualizar_tipo_entrega)
btn_actualizar.grid(row=0, column=0, padx=5)

# Tabla de pedidos
columns = ("ID", "Cliente", "Teléfono", "Dirección", "Persona que realiza el Delivery", "Enviado a", "Tipo de Entrega", "Descripcion", "Estado")
tree_pedidos = ttk.Treeview(root, columns=columns, show="headings", height=10)
for col in columns:
    tree_pedidos.heading(col, text=col)
    tree_pedidos.column(col, width=120, anchor="center")
tree_pedidos.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

# Scrollbar para la tabla
scrollbar = ttk.Scrollbar(root, orient="vertical", command=tree_pedidos.yview)
scrollbar.grid(row=3, column=2, sticky="ns")
tree_pedidos.configure(yscrollcommand=scrollbar.set)

# Cargar pedidos iniciales
cargar_pedidos()

# Ejecutar la aplicación
root.mainloop()