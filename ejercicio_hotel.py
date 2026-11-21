"""Ejercicio 8.5 - Gestión de contenidos: Hotel (Tkinter, varios layouts)."""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, date

FORMATO = "%Y-%m-%d"
FORMATO_TXT = "AAAA-MM-DD"


def parsear_fecha(texto):
    """Devuelve un date o None si el texto no es una fecha válida."""
    try:
        return datetime.strptime(texto.strip(), FORMATO).date()
    except ValueError:
        return None


# ----------------------------- MODELO ---------------------------------
class Huesped:
    def __init__(self, nombre, apellidos, documento):
        self.nombre = nombre
        self.apellidos = apellidos
        self.documento = documento

    def nombre_completo(self):
        return f"{self.nombre} {self.apellidos}"


class Habitacion:
    def __init__(self, numero, precio_dia):
        self.numero = numero
        self.precio_dia = precio_dia
        self.huesped = None
        self.fecha_ingreso = None

    @property
    def disponible(self):
        return self.huesped is None

    def ocupar(self, huesped, fecha_ingreso):
        self.huesped = huesped
        self.fecha_ingreso = fecha_ingreso

    def liberar(self):
        self.huesped = None
        self.fecha_ingreso = None

    def calcular_dias(self, fecha_salida):
        return (fecha_salida - self.fecha_ingreso).days

    def calcular_total(self, fecha_salida):
        return self.calcular_dias(fecha_salida) * self.precio_dia


class Hotel:
    """10 habitaciones: 1-5 a $120.000/día y 6-10 a $160.000/día."""

    def __init__(self):
        self.habitaciones = [Habitacion(n, 120_000 if n <= 5 else 160_000)
                             for n in range(1, 11)]

    def buscar(self, numero):
        for h in self.habitaciones:
            if h.numero == numero:
                return h
        return None


# ------------------------------ VISTA ---------------------------------
class VentanaHabitaciones(tk.Toplevel):
    """Muestra las 10 habitaciones en un GridLayout (grid) y deja elegir una."""

    def __init__(self, principal, hotel):
        super().__init__(principal)
        self.principal, self.hotel = principal, hotel
        self.title("Consultar habitaciones")
        self.resizable(False, False)
        self.transient(principal)

        ttk.Label(self, text="Seleccione la habitación a ocupar",
                  font=("Segoe UI", 12, "bold")).pack(pady=(12, 6))   # norte (Border)
        cuadricula = ttk.Frame(self, padding=10)
        cuadricula.pack()
        for i, h in enumerate(hotel.habitaciones):                     # Grid 2 x 5
            estado = "Disponible" if h.disponible else "No disponible"
            texto = f"Habitación {h.numero}\n${h.precio_dia:,.0f}/día\n{estado}"
            b = tk.Button(cuadricula, text=texto, width=16, height=4,
                          bg="#c8f7c5" if h.disponible else "#f7c5c5",
                          command=lambda hab=h: self.seleccionar(hab))
            b.grid(row=i // 5, column=i % 5, padx=4, pady=4)
        ttk.Button(self, text="Cerrar", command=self.destroy).pack(pady=(0, 10))  # sur

    def seleccionar(self, hab):
        if not hab.disponible:
            messagebox.showerror("Habitación ocupada",
                                 f"La habitación {hab.numero} no está disponible.", parent=self)
            return
        self.destroy()
        VentanaRegistro(self.principal, self.hotel, hab)


class VentanaRegistro(tk.Toplevel):
    def __init__(self, principal, hotel, hab):
        super().__init__(principal)
        self.hab = hab
        self.title(f"Registro - Habitación {hab.numero}")
        self.resizable(False, False)
        self.transient(principal)
        self.grab_set()

        self.fecha = tk.StringVar(value=date.today().strftime(FORMATO))
        self.nombre, self.apellidos, self.doc = tk.StringVar(), tk.StringVar(), tk.StringVar()

        marco = ttk.Frame(self, padding=15)
        marco.pack()
        campos = [(f"Fecha de ingreso ({FORMATO_TXT}):", self.fecha), ("Nombre:", self.nombre),
                  ("Apellidos:", self.apellidos), ("Documento de identidad:", self.doc)]
        for r, (txt, var) in enumerate(campos):                         # GridBag-like con grid
            ttk.Label(marco, text=txt).grid(row=r, column=0, sticky="w", pady=4)
            ttk.Entry(marco, textvariable=var, width=26).grid(row=r, column=1, pady=4, padx=(8, 0))
        ttk.Button(marco, text="Registrar huésped",
                   command=self.registrar).grid(row=4, column=0, columnspan=2, pady=(12, 0))

    def registrar(self):
        if not all(v.get().strip() for v in (self.fecha, self.nombre, self.apellidos, self.doc)):
            messagebox.showerror("Campos obligatorios", "Todos los campos son obligatorios.", parent=self)
            return
        f = parsear_fecha(self.fecha.get())
        if f is None:
            messagebox.showerror("Fecha inválida", f"Use el formato {FORMATO_TXT}.", parent=self)
            return
        if not self.doc.get().strip().isdigit():
            messagebox.showerror("Documento inválido", "El documento debe ser numérico.", parent=self)
            return
        self.hab.ocupar(Huesped(self.nombre.get().strip(), self.apellidos.get().strip(),
                                self.doc.get().strip()), f)
        messagebox.showinfo("Registro exitoso",
                            f"Habitación {self.hab.numero} asignada a "
                            f"{self.hab.huesped.nombre_completo()}.", parent=self)
        self.destroy()


class VentanaSalida(tk.Toplevel):
    def __init__(self, principal, hab):
        super().__init__(principal)
        self.hab, self.total, self.fecha_valida = hab, None, None
        self.title("Salida de huésped")
        self.resizable(False, False)
        self.transient(principal)
        self.grab_set()
        self.fecha = tk.StringVar()

        # BorderLayout con pack: norte (título), centro (datos), sur (botones)
        ttk.Label(self, text=f"Habitación {hab.numero}", font=("Segoe UI", 13, "bold")).pack(pady=(12, 4))
        centro = ttk.Frame(self, padding=12)
        centro.pack()
        info = [("Huésped:", hab.huesped.nombre_completo()),
                ("Fecha de ingreso:", hab.fecha_ingreso.strftime(FORMATO)),
                ("Precio por día:", f"${hab.precio_dia:,.0f}")]
        for r, (a, b) in enumerate(info):
            ttk.Label(centro, text=a).grid(row=r, column=0, sticky="w", pady=2)
            ttk.Label(centro, text=b).grid(row=r, column=1, sticky="w", padx=8)
        ttk.Label(centro, text=f"Fecha de salida ({FORMATO_TXT}):").grid(row=3, column=0, sticky="w", pady=6)
        entrada = ttk.Entry(centro, textvariable=self.fecha, width=14)
        entrada.grid(row=3, column=1, padx=8)
        entrada.bind("<KeyRelease>", self.validar_fecha)
        self.resultado = ttk.Label(centro, text="", font=("Segoe UI", 10, "bold"))
        self.resultado.grid(row=4, column=0, columnspan=2, pady=6)

        sur = ttk.Frame(self, padding=(0, 0, 0, 12))
        sur.pack()
        self.btn_calcular = ttk.Button(sur, text="Calcular total", state="disabled", command=self.calcular)
        self.btn_calcular.pack(side="left", padx=5)
        self.btn_registrar = ttk.Button(sur, text="Registrar salida", state="disabled", command=self.registrar)
        self.btn_registrar.pack(side="left", padx=5)

    def validar_fecha(self, _evento=None):
        f = parsear_fecha(self.fecha.get())
        if f is not None and f > self.hab.fecha_ingreso:
            self.fecha_valida = f
            self.btn_calcular.config(state="normal")
        else:
            self.fecha_valida = None
            self.btn_calcular.config(state="disabled")
            self.btn_registrar.config(state="disabled")
            self.resultado.config(text="")

    def calcular(self):
        dias = self.hab.calcular_dias(self.fecha_valida)
        self.total = self.hab.calcular_total(self.fecha_valida)
        self.resultado.config(text=f"Días: {dias}   |   Total a pagar: ${self.total:,.0f}")
        self.btn_registrar.config(state="normal")

    def registrar(self):
        self.hab.liberar()
        messagebox.showinfo("Salida registrada",
                            f"La habitación {self.hab.numero} quedó disponible.", parent=self)
        self.destroy()


class VentanaPrincipal(tk.Tk):
    def __init__(self):
        super().__init__()
        self.hotel = Hotel()
        self.title("Gestión de hotel")
        self.geometry("420x240")
        self.eval("tk::PlaceWindow . center")
        menu = tk.Menu(self)
        menu.add_command(label="Consultar habitaciones", command=self.consultar)
        menu.add_command(label="Salida de huéspedes", command=self.salida)
        self.config(menu=menu)
        ttk.Label(self, text="Hotel", font=("Segoe UI", 18, "bold")).pack(pady=(50, 6))
        ttk.Label(self, text="Use la barra de menús para comenzar.").pack()

    def consultar(self):
        VentanaHabitaciones(self, self.hotel)

    def salida(self):
        numero = simpledialog.askinteger("Salida de huéspedes", "Número de habitación a entregar:",
                                         parent=self)
        if numero is None:
            return
        hab = self.hotel.buscar(numero)
        if hab is None:
            messagebox.showerror("Dato incorrecto", "Ingrese un número entre 1 y 10.")
        elif hab.disponible:
            messagebox.showerror("Habitación libre", f"La habitación {numero} no está ocupada.")
        else:
            VentanaSalida(self, hab)


if __name__ == "__main__":
    VentanaPrincipal().mainloop()
