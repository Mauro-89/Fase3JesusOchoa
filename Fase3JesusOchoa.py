from collections import deque
from datetime import datetime
import re
import sys
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Deque, List, Optional, Tuple

# Definicion de la clase

class AffiliateData:
  """Clase para modelar la información de cada afiliado que se registra"""

  def __init__(
      self,
      doc_type: str,
      doc_num: str,
      full_name: str,
      income: float,
      emp_mode: str,
      service: str,
      fee: float,
      aff_date: str,
  ) -> None:
    
    # Guardo todos los datos personales, económicos y del servicio seleccionado
    
    self.doc_type: str = doc_type
    self.doc_num: str = doc_num
    self.full_name: str = full_name
    self.income: float = income
    self.emp_mode: str = emp_mode
    self.service: str = service
    self.fee: float = fee
    self.aff_date: str = aff_date

  @classmethod
  def calculate_affiliation_fee(
      cls, income: float, emp_mode: str, service: str
  ) -> float:
    
    """Aquí calculo la tarifa de afiliación según el salario,
    si es empleado o independiente, y le sumo el recargo
    del servicio que haya elegido
    """
    # Tablas de rangos salariales para empleados y tarifas base
    
    employee_tiers: List[Tuple[float, float]] = [
        (2000000.0, 45000.0),
        (3000000.0, 60000.0),
        (4000000.0, 75000.0),
        (5000000.0, 90000.0),
        (float("inf"), 150000.0),
    ]

    # Tablas de rangos salariales para independientes y tarifas base
    independent_tiers: List[Tuple[float, float]] = [
        (2000000.0, 10000.0),
        (3000000.0, 20000.0),
        (4000000.0, 30000.0),
        (5000000.0, 40000.0),
        (float("inf"), 80000.0),
    ]

    tiers = employee_tiers if emp_mode == "Employee" else independent_tiers
    base_fee = 0.0

    # Busco en qué rango cae el salario actual para definir la tarifa base
    for limit, fee_value in tiers:
      if income <= limit:
        base_fee = fee_value
        break

    # Recargos adicionales según el servicio escogido
    surcharges = {
        "Unemployment Subsidy": 0.0,
        "Park Access": 2500.0,
        "Training Course": 7500.0,
        "Travel Package": 10000.0,
        "Preventive Medicine": income * 0.10,
    }

    return base_fee + surcharges.get(service, 0.0)


# Gestor de estructuras de datos

class AffiliationManager:
  """Este gestor controla el almacenamiento en memoria principal

  para las tres estructuras de datos lineales solicitadas (Pila, Cola y Lista)
  """

  def __init__(self) -> None:
    self.stack_data: List[AffiliateData] = []  # Pila (LIFO)
    self.queue_data: Deque[AffiliateData] = deque()  # Cola (FIFO)
    self.list_data: List[AffiliateData] = []  # Lista dinámica

  def register(self, affiliate: AffiliateData, structure_type: str) -> None:
    """Inserta el nuevo afiliado en la estructura que el usuario haya seleccionado"""
    if "Stack" in structure_type:
      self.stack_data.append(affiliate)  # Apilar
    elif "Queue" in structure_type:
      self.queue_data.append(affiliate)  # Encolar
    elif "List" in structure_type:
      self.list_data.append(affiliate)  # Agregar al final

  def get_records(self, structure_type: str) -> List[AffiliateData]:
    """Devuelve los elementos actuales de la estructura activa para mostrarlos en pantalla"""
    
    if "Stack" in structure_type:
      return self.stack_data
    elif "Queue" in structure_type:
      return list(self.queue_data)
    elif "List" in structure_type:
      return self.list_data
    return []

  def generate_report(self, structure_type: str) -> str:
    """Calcula los reportes estadísticos obligatorios según la estructura:

    - Pila: Suma total de tarifas
    - Cola: Cantidad de registros
    - Lista: Promedio de ingresos"""
    
    if "Stack" in structure_type:
      total_fees = sum(item.fee for item in self.stack_data)
      return f"Total Fees: ${total_fees:,.2f}"
    elif "Queue" in structure_type:
      return f"Total Records: {len(self.queue_data)}"
    elif "List" in structure_type:
      if self.list_data:
        avg_income = sum(item.income for item in self.list_data) / len(
            self.list_data
        )
        return f"Avg Income: ${avg_income:,.2f}"
      return "Avg Income: $0.00"
    return ""

  def remove_record(
      self, structure_type: str, doc_num: str = ""
  ) -> Tuple[bool, str]:
    """Elimina registros respetando la regla lógica de cada estructura:

    - Pila: Desapila el último elemento
    - Cola: Desencola el primer elemento
    - Lista: Busca por número de cédula y elimina el afiliado encontrado"""
    
    if "Stack" in structure_type:
      if not self.stack_data:
        return False, "The Stack is currently empty."
      removed = self.stack_data.pop()
      return True, f"Popped affiliate: {removed.full_name}"

    elif "Queue" in structure_type:
      if not self.queue_data:
        return False, "The Queue is currently empty."
      removed = self.queue_data.popleft()
      return True, f"Dequeued affiliate: {removed.full_name}"

    elif "List" in structure_type:
      if not self.list_data:
        return False, "The List is currently empty."
      if not doc_num:
        return False, "Please enter an ID Number in the form to search."

      target = next(
          (item for item in self.list_data if item.doc_num == doc_num), None
      )
      if target:
        self.list_data.remove(target)
        return True, f"Removed affiliate: {target.full_name} (ID: {doc_num})"
      return False, f"No affiliate found with ID Number: {doc_num}"

    return False, "Invalid structure type selected."


# Interfaz grafica del usuario

class CompensandoteApp(tk.Tk):
  """Interfaz gráfica principal que maneja tanto la ventana de Login
  como el panel de control de afiliados"""
  

  def __init__(self) -> None:
    super().__init__()
    self.title("Login — Compensándote")
    self.geometry("480x560")
    self.resizable(False, False)
    self.configure(bg="#9CF6EA") 
    self.manager = AffiliationManager()
    self.create_login_view()

  # Interfaz de inicio de sesión
  def create_login_view(self) -> None:
    """Diseño de la ventana de inicio de sesión con contraseña enmascarada"""
    
    menubar = tk.Menu(self)
    about_menu = tk.Menu(menubar, tearoff=0)
    about_menu.add_command(label="About", command=self.show_about_dialog)
    menubar.add_cascade(label="About", menu=about_menu)
    self.config(menu=menubar)

    # Título principal de bienvenida
    lbl_header = tk.Label(
        self,
        text="Compensándote",
        font=("Segoe UI", 30, "bold"),
        fg="#010101",
        bg="#9CF6EA",
    )
    
    lbl_header.pack(pady=(25, 2))

    lbl_sub = tk.Label(
        self,
        text="Family Compensation Fund — Affiliation Control",
        font=("Segoe UI", 9, "italic"),
        fg="#080404",
        bg="#9CF6EA",
    )
    lbl_sub.pack(pady=(0, 20))

    # Tarjeta informativa con mis datos de estudiante
    
    card = tk.Frame(self, bg="#1c313a", bd=1, relief="ridge", padx=15, pady=12)
    card.pack(fill="x", padx=35, pady=5)

    info_text = (
        "Application: Fase3JesusOchoa\n"
        "Student: Jesús Mauricio Ochoa Pinilla\n"
        "Course: Data Structures - 301305\n"
        "Date: October 2026"
    )
    
    lbl_info = tk.Label(
        card,
        text=info_text,
        font=("Segoe UI", 9, "italic", "bold"),
        fg="#e0f7fa",
        bg="#1c313a",
        justify="left",
    )
    lbl_info.pack(anchor="w")

    # Campo de contraseña
    
    lbl_pass = tk.Label(
        self,
        text="Password",
        font=("Segoe UI", 10, "bold"),
        fg="#010101",
        bg="#9CF6EA",
    )
    
    lbl_pass.pack(pady=(20, 5))

    self.ent_password = tk.Entry(
        self,
        show="*",
        font=("Segoe UI", 11),
        width=24,
        justify="center",
        bd=2,
    )
    
    self.ent_password.pack(pady=5)
    self.ent_password.bind("<Return>", lambda event: self.validate_login())

    lbl_hint = tk.Label(
        self,
        text="Password masked (****)",
        font=("Segoe UI", 8),
        fg="#010101",
        bg="#9CF6EA",
    )
    
    lbl_hint.pack()

    # Botones de acceso y salida
    
    btn_frame = tk.Frame(self, bg="#9CF6EA")
    btn_frame.pack(pady=25)

    btn_login = tk.Button(
        btn_frame,
        text="Login",
        font=("Segoe UI", 10, "bold"),
        bg="#01464f",
        fg="#ffffff",
        activebackground="#0DCA19",
        activeforeground="#ffffff",
        width=12,
        cursor="hand2",
        command=self.validate_login,
    )
    
    btn_login.pack(side="left", padx=10)
    btn_login.bind("<Return>", lambda event: self.validate_login())

    btn_exit = tk.Button(
        btn_frame,
        text="Exit",
        font=("Segoe UI", 10, "bold"),
        bg="#c62828",
        fg="#ffffff",
        activebackground="#8e0000",
        activeforeground="#ffffff",
        width=12,
        cursor="hand2",
        command=self.destroy,
    )
    btn_exit.pack(side="right", padx=10)
    btn_exit.bind("<Return>", lambda event: self.destroy())

  def show_about_dialog(self) -> None:
    """Muestra el cuadro emergente con la información detallada del autor"""
    
    about_msg = (
        "Course: Data Structures — 301305\n"
        "Student: Jesús Mauricio Ochoa Pinilla\n"
        "Collaborative Group: 301305_218\n"
        "UNAD - ECBTI - Systems Engineering\n"
        "Date: October 2026"
    )
    messagebox.showinfo("About", about_msg)

  def validate_login(self) -> None:
    """Verifico que la contraseña escrita sea exactamente 'Caja'"""
    
    if self.ent_password.get() == "Caja":
      self.withdraw()  # Oculto la ventana de login
      self.open_main_dashboard()  # Abro la interfaz principal
    else:
      messagebox.showerror(
          "Access Denied", "Invalid password. Please enter the correct password."
      )

  # Interfaz del panel de control
  
  def open_main_dashboard(self) -> None:
    """Ventana principal donde se capturan los datos y se procesan las estructuras lineales"""
    
    dash = tk.Toplevel(self)
    dash.title("Compensándote — Affiliation Control")
    dash.geometry("1180x640")
    dash.configure(bg="#1c313a")  
    dash.protocol("WM_DELETE_WINDOW", self.destroy)

    # Forzamos el foco activo en la nueva ventana inmediatamente
    dash.lift()
    dash.focus_force()

    form_frame = tk.LabelFrame(
        dash,
        text=" Affiliate Information Form ",
        font=("Segoe UI", 10, "bold"),
        fg="#010101",
        bg="#9CF6EA",
        padx=12,
        pady=10,
    )
    form_frame.pack(side="left", fill="both", padx=10, pady=10)

    # Validadores de entrada por expresiones regulares
    vcmd_digits = (self.register(self.validate_digits), "%P")
    vcmd_letters = (self.register(self.validate_letters), "%P")

    # Lista para registrar todos los elementos interactivos y permitir navegación con flechas
    self.focusable_widgets = []

    # Tipo de documento (Combobox con apertura por Barra Espaciadora y selección con Enter)
    tk.Label(
        form_frame,
        text="Document Type:",
        font=("Segoe UI", 9),
        fg="#010101",
        bg="#9CF6EA",
    ).grid(row=0, column=0, sticky="w", pady=3)
    self.cmb_doc_type = ttk.Combobox(
        form_frame, values=["CC", "CE", "NUIP", "PAS"], state="readonly", width=22
    )
    self.cmb_doc_type.current(0)
    self.cmb_doc_type.grid(row=0, column=1, pady=3)
    self.cmb_doc_type.bind(
        "<space>", lambda e: self.open_combobox_dropdown(e)
    )
    self.cmb_doc_type.bind("<Return>", lambda e: self.confirm_combobox(e))
    self.focusable_widgets.append(self.cmb_doc_type)

    # Establecemos el foco inicial directamente en este primer control
    self.cmb_doc_type.focus_set()

    # Número de documento (solo números)
    tk.Label(
        form_frame,
        text="ID Number (digits only):",
        font=("Segoe UI", 9),
        fg="#010101",
        bg="#9CF6EA",
    ).grid(row=1, column=0, sticky="w", pady=3)
    self.ent_doc_num = tk.Entry(
        form_frame, validate="key", validatecommand=vcmd_digits, width=24
    )
    self.ent_doc_num.grid(row=1, column=1, pady=3)
    self.focusable_widgets.append(self.ent_doc_num)

    # Nombre completo (con soporte para la letra ñ y mayúscula automática al salir de la casilla)
    tk.Label(
        form_frame,
        text="Full Name (letters only):",
        font=("Segoe UI", 9),
        fg="#010101",
        bg="#9CF6EA",
    ).grid(row=2, column=0, sticky="w", pady=3)
    self.ent_full_name = tk.Entry(
        form_frame, validate="key", validatecommand=vcmd_letters, width=24
    )
    self.ent_full_name.grid(row=2, column=1, pady=3)
    self.ent_full_name.bind("<FocusOut>", self.format_full_name_on_out)
    self.focusable_widgets.append(self.ent_full_name)

    # Salario actual (con formato automático de moneda pesos)
    tk.Label(
        form_frame,
        text="Current Income ($):",
        font=("Segoe UI", 9),
        fg="#010101",
        bg="#9CF6EA",
    ).grid(row=3, column=0, sticky="w", pady=3)
    self.ent_income = tk.Entry(form_frame, width=24)
    self.ent_income.grid(row=3, column=1, pady=3)
    self.ent_income.bind("<FocusOut>", self.format_currency_on_out)
    self.ent_income.bind("<FocusIn>", self.clean_currency_on_in)
    self.focusable_widgets.append(self.ent_income)

    # Modalidad de empleo (Radio buttons seleccionables con Enter)
    tk.Label(
        form_frame,
        text="Employment Mode:",
        font=("Segoe UI", 9),
        fg="#010101",
        bg="#9CF6EA",
    ).grid(row=4, column=0, sticky="w", pady=3)
    self.var_emp_mode = tk.StringVar(value="Employee")
    rad_frame = tk.Frame(form_frame, bg="#9CF6EA")
    rad_frame.grid(row=4, column=1, sticky="w")

    rad1 = tk.Radiobutton(
        rad_frame,
        text="Employee",
        variable=self.var_emp_mode,
        value="Employee",
        bg="#9CF6EA",
        fg="#010101",
        selectcolor="#ffffff",
    )
    rad1.pack(side="left")
    rad1.bind(
        "<Return>",
        lambda e, val="Employee": self.select_radio_with_enter(val),
    )
    rad1.unbind("<space>")

    rad2 = tk.Radiobutton(
        rad_frame,
        text="Independent",
        variable=self.var_emp_mode,
        value="Independent",
        bg="#9CF6EA",
        fg="#010101",
        selectcolor="#ffffff",
    )
    rad2.pack(side="left")
    rad2.bind(
        "<Return>",
        lambda e, val="Independent": self.select_radio_with_enter(val),
    )
    rad2.unbind("<space>")

    self.focusable_widgets.append(rad1)
    self.focusable_widgets.append(rad2)

    # Servicio deseado (Combobox con apertura por Barra Espaciadora y selección con Enter)
    tk.Label(
        form_frame,
        text="Desired Service:",
        font=("Segoe UI", 9),
        fg="#010101",
        bg="#9CF6EA",
    ).grid(row=5, column=0, sticky="w", pady=3)
    services = [
        "----- Select Service -----",      
        "Unemployment Subsidy",
        "Park Access",
        "Training Course",
        "Travel Package",
        "Preventive Medicine",
    ]
    self.cmb_service = ttk.Combobox(
        form_frame, values=services, state="readonly", width=22
    )
    self.cmb_service.current(0)
    self.cmb_service.grid(row=5, column=1, pady=3)
    self.cmb_service.bind(
        "<space>", lambda e: self.open_combobox_dropdown(e)
    )
    self.cmb_service.bind("<Return>", lambda e: self.confirm_combobox(e))
    self.focusable_widgets.append(self.cmb_service)

    # Tarifa calculada (Campo de solo lectura)
    tk.Label(
        form_frame,
        text="Affiliation Fee ($):",
        font=("Segoe UI", 9, "bold"),
        fg="#c5882c",
        bg="#9CF6EA",
    ).grid(row=6, column=0, sticky="w", pady=3)
    self.ent_fee = tk.Entry(
        form_frame, width=24, state="readonly", font=("Segoe UI", 9, "bold")
    )
    self.ent_fee.grid(row=6, column=1, pady=3)

    # Fecha de afiliación con casillas individuales (Día, Mes, Año)
    tk.Label(
        form_frame,
        text="Affiliation Date (dd/mm/yyyy):",
        font=("Segoe UI", 9),
        fg="#010101",
        bg="#9CF6EA",
    ).grid(row=7, column=0, sticky="w", pady=3)

    date_frame = tk.Frame(form_frame, bg="#9CF6EA")
    date_frame.grid(row=7, column=1, sticky="w", pady=3)

    now = datetime.now()
    self.spin_day = tk.Spinbox(
        date_frame, from_=1, to=31, width=3, justify="center"
    )
    self.spin_day.delete(0, "end")
    self.spin_day.insert(0, f"{now.day:02d}")
    self.spin_day.pack(side="left")
    self.focusable_widgets.append(self.spin_day)

    tk.Label(
        date_frame, text="/", fg="#010101", bg="#9CF6EA", font=("Segoe UI", 10)
    ).pack(side="left", padx=2)

    self.spin_month = tk.Spinbox(
        date_frame, from_=1, to=12, width=3, justify="center"
    )
    self.spin_month.delete(0, "end")
    self.spin_month.insert(0, f"{now.month:02d}")
    self.spin_month.pack(side="left")
    self.focusable_widgets.append(self.spin_month)

    tk.Label(
        date_frame, text="/", fg="#010101", bg="#9CF6EA", font=("Segoe UI", 10)
    ).pack(side="left", padx=2)

    self.spin_year = tk.Spinbox(
        date_frame, from_=2000, to=2100, width=5, justify="center"
    )
    self.spin_year.delete(0, "end")
    self.spin_year.insert(0, str(now.year))
    self.spin_year.pack(side="left")
    self.focusable_widgets.append(self.spin_year)

    # Selector de estructura de datos (Combobox con apertura por Barra Espaciadora y selección con Enter)
    tk.Label(
        form_frame,
        text="Target Data Structure:",
        font=("Segoe UI", 9, "bold"),
        fg="#009b39",
        bg="#9CF6EA",
    ).grid(row=8, column=0, sticky="w", pady=(10, 3))
    self.cmb_structure = ttk.Combobox(
        form_frame,
        values=["Stack (Pila)", "Queue (Cola)", "List (Lista)"],
        state="readonly",
        width=22,
    )
    self.cmb_structure.current(0)
    self.cmb_structure.grid(row=8, column=1, pady=(10, 3))
    self.cmb_structure.bind("<<ComboboxSelected>>", self.on_structure_change)
    self.cmb_structure.bind(
        "<space>", lambda e: self.open_combobox_dropdown(e)
    )
    self.cmb_structure.bind("<Return>", lambda e: self.confirm_combobox(e))
    self.focusable_widgets.append(self.cmb_structure)

    # Campo de reporte dinámico
    tk.Label(
        form_frame,
        text="Structure Report:",
        font=("Segoe UI", 9, "bold"),
        fg="#a025b5",
        bg="#9CF6EA",
    ).grid(row=9, column=0, sticky="w", pady=(10, 3))
    self.ent_report = tk.Entry(
        form_frame, width=24, state="readonly", font=("Segoe UI", 9, "bold")
    )
    self.ent_report.grid(row=9, column=1, pady=(10, 3))

    # Botón para calcular la tarifa
    btn_calc = tk.Button(
        form_frame,
        text="Calculate Fee",
        font=("Segoe UI", 9, "bold"),
        bg="#f57c00",
        fg="#ffffff",
        cursor="hand2",
        command=self.compute_fee_action,
    )
    btn_calc.grid(row=10, column=0, columnspan=2, pady=12, sticky="ew")
    btn_calc.bind("<Return>", lambda event: self.compute_fee_action())
    self.focusable_widgets.append(btn_calc)

    # Configuro la navegación bidireccional con las flechas del teclado
    for widget in self.focusable_widgets:
      if not isinstance(widget, (ttk.Combobox, tk.Spinbox)):
        widget.bind("<Down>", lambda e, w=widget: self.navigate_grid(e, w, 1))
        widget.bind("<Right>", lambda e, w=widget: self.navigate_grid(e, w, 1))
        widget.bind("<Up>", lambda e, w=widget: self.navigate_grid(e, w, -1))
        widget.bind("<Left>", lambda e, w=widget: self.navigate_grid(e, w, -1))
      else:
        widget.bind(
            "<Right>", lambda e, w=widget: self.navigate_grid(e, w, 1)
        )
        widget.bind("<Left>", lambda e, w=widget: self.navigate_grid(e, w, -1))

    # Contenedor de la tabla Treeview
    right_frame = tk.Frame(dash, bg="#0f2027")
    right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

    columns = (
        "DocType",
        "ID",
        "FullName",
        "Income",
        "Mode",
        "Service",
        "Fee",
        "Date",
    )
    
    self.tree = ttk.Treeview(
        right_frame, columns=columns, show="headings", height=18
    )

    for col in columns:
      self.tree.heading(col, text=col)
      self.tree.column(col, width=95, anchor="center")

    scrollbar = ttk.Scrollbar(
        right_frame, orient="vertical", command=self.tree.yview
    )
    self.tree.configure(yscrollcommand=scrollbar.set)
    self.tree.pack(side="top", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Barra de botones de acción
    toolbar = tk.Frame(right_frame, bg="#1c313a", pady=10)
    toolbar.pack(side="bottom", fill="x")

    btn_reg = tk.Button(
        toolbar,
        text="Register",
        bg="#00838f",
        fg="#ffffff",
        font=("Segoe UI", 9, "bold"),
        width=10,
        command=self.register_affiliate,
    )
    btn_reg.pack(side="left", padx=5)
    btn_reg.bind("<Return>", lambda event: self.register_affiliate())

    btn_clr = tk.Button(
        toolbar,
        text="Clear",
        bg="#757575",
        fg="#ffffff",
        font=("Segoe UI", 9, "bold"),
        width=10,
        command=self.clear_form,
    )
    btn_clr.pack(side="left", padx=5)
    btn_clr.bind("<Return>", lambda event: self.clear_form())

    btn_rep = tk.Button(
        toolbar,
        text="Report",
        bg="#7b1fa2",
        fg="#ffffff",
        font=("Segoe UI", 9, "bold"),
        width=10,
        command=self.update_report_field,
    )
    btn_rep.pack(side="left", padx=5)
    btn_rep.bind("<Return>", lambda event: self.update_report_field())

    btn_del = tk.Button(
        toolbar,
        text="Delete",
        bg="#d32f2f",
        fg="#ffffff",
        font=("Segoe UI", 9, "bold"),
        width=10,
        command=self.delete_affiliate,
    )
    btn_del.pack(side="left", padx=5)
    btn_del.bind("<Return>", lambda event: self.delete_affiliate())

    btn_ext = tk.Button(
        toolbar,
        text="Exit",
        bg="#37474f",
        fg="#ffffff",
        font=("Segoe UI", 9, "bold"),
        width=10,
        command=self.destroy,
    )
    btn_ext.pack(side="right", padx=5)
    btn_ext.bind("<Return>", lambda event: self.destroy())

    self.update_report_field()


  # Metodos de mejora
  
  def open_combobox_dropdown(self, event) -> None:
    """Abre el menú desplegable del Combobox al presionar la Barra Espaciadora"""
    event.widget.tk.call("ttk::combobox::Post", event.widget)
    return "break"

  def confirm_combobox(self, event) -> None:
    """Confirma la selección del Combobox con Enter y pasa al siguiente campo"""
    event.widget.selection_clear()
    self.navigate_grid(event, event.widget, 1)
    return "break"

  def select_radio_with_enter(self, val: str) -> None:
    """Selecciona el botón de opción en employment mode al presionar Enter"""
    self.var_emp_mode.set(val)
    current_focus = self.focus_get()
    try:
      idx = self.focusable_widgets.index(current_focus)
      next_idx = (idx + 1) % len(self.focusable_widgets)
      self.focusable_widgets[next_idx].focus_set()
    except ValueError:
      pass

  def navigate_grid(self, event, current_widget, step: int) -> str:
    """Permite moverse libremente hacia adelante o atrás entre campos usando las flechas"""
    try:
      idx = self.focusable_widgets.index(current_widget)
      next_idx = (idx + step) % len(self.focusable_widgets)
      self.focusable_widgets[next_idx].focus_set()
    except ValueError:
      pass
    return "break"

  def format_full_name_on_out(self, event) -> None:
    """Aplica mayúscula automática a la primera letra de cada palabra al salir de la casilla"""
    val = self.ent_full_name.get()
    formatted = " ".join([word.capitalize() for word in val.split()])
    self.ent_full_name.delete(0, tk.END)
    self.ent_full_name.insert(0, formatted)

  def format_currency_on_out(self, event) -> None:
    """Muestra el valor salarial en formato de moneda con signo $ y puntos separadores de miles"""
    raw = "".join(filter(str.isdigit, self.ent_income.get()))
    if raw:
      num = int(raw)
      self.ent_income.delete(0, tk.END)
      self.ent_income.insert(0, f"${num:,.0f}".replace(",", "."))

  def clean_currency_on_in(self, event) -> None:
    """Limpia los símbolos de moneda y puntos cuando el usuario hace clic para editar"""
    val = (
        self.ent_income.get()
        .replace("$", "")
        .replace(".", "")
        .replace(",", "")
        .strip()
    )
    self.ent_income.delete(0, tk.END)
    self.ent_income.insert(0, val)

  # Metodos de validación de entrada
  def validate_digits(self, P: str) -> bool:
    """Valida que solo se escriban caracteres numéricos"""
    return bool(re.match(r"^\d*$", P))

  def validate_letters(self, P: str) -> bool:
    """Valida que solo se escriban letras, espacios y la letra ñ o Ñ"""
    return bool(re.match(r"^[a-zA-ZñÑ\s]*$", P))

  # Métodos de acción para registro, reporte y eliminación de afiliados
  def compute_fee_action(self) -> Optional[float]:
    """Calcula y muestra la tarifa en pantalla extrayendo el valor numérico limpio del salario"""
    try:
      raw_income = (
          self.ent_income.get()
          .replace("$", "")
          .replace(".", "")
          .replace(",", "")
          .strip()
      )
      income = float(raw_income)
      emp_mode = self.var_emp_mode.get()
      service = self.cmb_service.get()

      fee = AffiliateData.calculate_affiliation_fee(income, emp_mode, service)

      self.ent_fee.config(state="normal")
      self.ent_fee.delete(0, tk.END)
      self.ent_fee.insert(0, f"${fee:,.2f}".replace(",", "."))
      self.ent_fee.config(state="readonly")
      return fee
    except ValueError:
      messagebox.showwarning(
          "Input Error", "Please enter a valid numeric current income."
      )
      return None

  def register_affiliate(self) -> None:
    """Registra el afiliado en la estructura seleccionada (Pila, Cola o Lista)"""
    doc_type = self.cmb_doc_type.get()
    doc_num = self.ent_doc_num.get().strip()
    full_name = self.ent_full_name.get().strip()
    raw_income = (
        self.ent_income.get()
        .replace("$", "")
        .replace(".", "")
        .replace(",", "")
        .strip()
    )
    emp_mode = self.var_emp_mode.get()
    service = self.cmb_service.get()

    day = self.spin_day.get().zfill(2)
    month = self.spin_month.get().zfill(2)
    year = self.spin_year.get()
    aff_date = f"{day}/{month}/{year}"

    if not (doc_num and full_name and raw_income and aff_date):
      messagebox.showwarning(
          "Required Fields", "All form fields must be completed."
      )
      return

    fee = self.compute_fee_action()
    if fee is None:
      return

    affiliate = AffiliateData(
        doc_type,
        doc_num,
        full_name,
        float(raw_income),
        emp_mode,
        service,
        fee,
        aff_date,
    )
    struct_type = self.cmb_structure.get()

    self.manager.register(affiliate, struct_type)
    self.refresh_treeview()
    self.update_report_field()

    messagebox.showinfo(
        "Success", "Affiliate successfully registered in memory."
    )
    self.cmb_doc_type.focus_set()

  def refresh_treeview(self) -> None:
    """Actualiza la tabla visual Treeview con los registros de la estructura activa"""
    for row in self.tree.get_children():
      self.tree.delete(row)

    struct_type = self.cmb_structure.get()
    records = self.manager.get_records(struct_type)

    for item in records:
      self.tree.insert(
          "",
          "end",
          values=(
              item.doc_type,
              item.doc_num,
              item.full_name,
              f"${item.income:,.0f}".replace(",", "."),
              item.emp_mode,
              item.service,
              f"${item.fee:,.0f}".replace(",", "."),
              item.aff_date,
          ),
      )

  def on_structure_change(self, event: tk.Event) -> None:
    """Cambia la vista de la tabla y los reportes al seleccionar otra estructura"""
    self.refresh_treeview()
    self.update_report_field()

  def update_report_field(self) -> None:
    """Actualiza el campo de estadísticas según la estructura seleccionada"""
    struct_type = self.cmb_structure.get()
    report_text = self.manager.generate_report(struct_type)

    self.ent_report.config(state="normal")
    self.ent_report.delete(0, tk.END)
    self.ent_report.insert(0, report_text)
    self.ent_report.config(state="readonly")

  def delete_affiliate(self) -> None:
    """Elimina registros según el comportamiento lógico de Pila, Cola o Lista"""
    struct_type = self.cmb_structure.get()
    doc_num = self.ent_doc_num.get().strip() if "List" in struct_type else ""

    if not messagebox.askyesno(
        "Confirm Delete",
        f"Proceed with record deletion according to {struct_type} rules?",
    ):
      return

    success, message = self.manager.remove_record(struct_type, doc_num)

    if success:
      self.refresh_treeview()
      self.update_report_field()
      messagebox.showinfo("Success", message)
      self.cmb_doc_type.focus_set()
    else:
      messagebox.showwarning("Warning", message)
      self.cmb_doc_type.focus_set()

  def clear_form(self) -> None:
    """Limpia los campos del formulario de ingreso de datos sin borrar el Treeview"""
    self.ent_doc_num.delete(0, tk.END)
    self.ent_full_name.delete(0, tk.END)
    self.ent_income.delete(0, tk.END)

    now = datetime.now()
    self.spin_day.delete(0, "end")
    self.spin_day.insert(0, f"{now.day:02d}")
    self.spin_month.delete(0, "end")
    self.spin_month.insert(0, f"{now.month:02d}")
    self.spin_year.delete(0, "end")
    self.spin_year.insert(0, str(now.year))

    self.ent_fee.config(state="normal")
    self.ent_fee.delete(0, tk.END)
    self.ent_fee.config(state="readonly")

    self.cmb_doc_type.focus_set()


if __name__ == "__main__":
  app = CompensandoteApp()
  app.mainloop()