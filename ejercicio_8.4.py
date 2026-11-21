"""Ejercicio 8.4 - Cuadros de diálogo: Nómina de empleados (Tkinter)."""
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

CARGOS = ["Directivo", "Estratégico", "Operativo"]


# ----------------------------- MODELO ---------------------------------
class Empleado:
    def __init__(self, nombre, apellidos, cargo, genero, salario_dia,
                 dias_trabajados, otros_ingresos, pago_salud, aporte_pension):
        self.nombre = nombre
        self.apellidos = apellidos
        self.cargo = cargo
        self.genero = genero
        self.salario_dia = salario_dia
        self.dias_trabajados = dias_trabajados
        self.otros_ingresos = otros_ingresos
        self.pago_salud = pago_salud
        self.aporte_pension = aporte_pension

    def calcular_salario_mensual(self):
        return (self.dias_trabajados * self.salario_dia + self.otros_ingresos
                - self.pago_salud - self.aporte_pension)


class Nomina:
    """Gestiona la lista de empleados de la empresa."""

    def __init__(self):
        self.empleados = []

    def agregar_empleado(self, empleado):
        self.empleados.append(empleado)

    def calcular_total(self):
        return sum(e.calcular_salario_mensual() for e in self.empleados)

    def guardar_archivo(self, carpeta):
        ruta = os.path.join(carpeta, "Nómina.txt")
        with open(ruta, "w", encoding="utf-8") as f:
            f.write("NÓMINA DE LA EMPRESA\n" + "=" * 40 + "\n")
            for i, e in enumerate(self.empleados, 1):
                f.write(f"\nEmpleado {i}\n")
                f.write(f"  Nombre: {e.nombre}\n  Apellidos: {e.apellidos}\n")
                f.write(f"  Cargo: {e.cargo}\n  Género: {e.genero}\n")
                f.write(f"  Salario por día: {e.salario_dia:,.2f}\n")
                f.write(f"  Días trabajados: {e.dias_trabajados}\n")
                f.write(f"  Otros ingresos: {e.otros_ingresos:,.2f}\n")
                f.write(f"  Pagos por salud: {e.pago_salud:,.2f}\n")
                f.write(f"  Aporte pensiones: {e.aporte_pension:,.2f}\n")
                f.write(f"  Sueldo mensual: {e.calcular_salario_mensual():,.2f}\n")
            f.write("\n" + "=" * 40 + f"\nTOTAL NÓMINA: {self.calcular_total():,.2f}\n")
        return ruta


# ------------------------------ VISTA ---------------------------------
class VentanaAgregarEmpleado(tk.Toplevel):
    def __init__(self, principal, nomina):
        super().__init__(principal)
        self.nomina = nomina
        self.title("Agregar empleado")
        self.resizable(False, False)
        self.transient(principal)
        self.grab_set()  # ventana modal

        self.nombre = tk.StringVar()
        self.apellidos = tk.StringVar()
        self.genero = tk.StringVar(value="Masculino")
        self.salario = tk.StringVar()
        self.dias = tk.IntVar(value=30)
        self.otros = tk.StringVar(value="0")
        self.salud = tk.StringVar(value="0")
        self.pension = tk.StringVar(value="0")

        marco = ttk.Frame(self, padding=15)
        marco.grid()
        filas = [("Nombre:", ttk.Entry(marco, textvariable=self.nombre, width=28)),
                 ("Apellidos:", ttk.Entry(marco, textvariable=self.apellidos, width=28))]
        for r, (txt, w) in enumerate(filas):
            ttk.Label(marco, text=txt).grid(row=r, column=0, sticky="w", pady=4)
            w.grid(row=r, column=1, sticky="w")

        ttk.Label(marco, text="Cargo:").grid(row=2, column=0, sticky="nw", pady=4)
        self.lista_cargos = tk.Listbox(marco, height=3, exportselection=False)
        for c in CARGOS:
            self.lista_cargos.insert(tk.END, c)
        self.lista_cargos.selection_set(2)
        self.lista_cargos.grid(row=2, column=1, sticky="w")

        ttk.Label(marco, text="Género:").grid(row=3, column=0, sticky="w", pady=4)
        fr = ttk.Frame(marco)
        fr.grid(row=3, column=1, sticky="w")
        ttk.Radiobutton(fr, text="Masculino", value="Masculino",
                        variable=self.genero).pack(side="left")
        ttk.Radiobutton(fr, text="Femenino", value="Femenino",
                        variable=self.genero).pack(side="left", padx=8)

        ttk.Label(marco, text="Salario por día:").grid(row=4, column=0, sticky="w", pady=4)
        ttk.Entry(marco, textvariable=self.salario, width=15).grid(row=4, column=1, sticky="w")
        ttk.Label(marco, text="Días trabajados (1-31):").grid(row=5, column=0, sticky="w", pady=4)
        ttk.Spinbox(marco, from_=1, to=31, textvariable=self.dias, width=6).grid(row=5, column=1, sticky="w")
        ttk.Label(marco, text="Otros ingresos:").grid(row=6, column=0, sticky="w", pady=4)
        ttk.Entry(marco, textvariable=self.otros, width=15).grid(row=6, column=1, sticky="w")
        ttk.Label(marco, text="Pagos por salud:").grid(row=7, column=0, sticky="w", pady=4)
        ttk.Entry(marco, textvariable=self.salud, width=15).grid(row=7, column=1, sticky="w")
        ttk.Label(marco, text="Aporte pensiones:").grid(row=8, column=0, sticky="w", pady=4)
        ttk.Entry(marco, textvariable=self.pension, width=15).grid(row=8, column=1, sticky="w")

        botones = ttk.Frame(marco)
        botones.grid(row=9, column=0, columnspan=2, pady=(12, 0))
        ttk.Button(botones, text="Guardar", command=self.guardar).pack(side="left", padx=5)
        ttk.Button(botones, text="Cancelar", command=self.destroy).pack(side="left", padx=5)

    def _numero(self, texto, campo):
        try:
            valor = float(texto.get().replace(",", "."))
            if valor < 0:
                raise ValueError
            return valor
        except ValueError:
            raise ValueError(f"El campo «{campo}» debe ser un número mayor o igual a 0.")

    def guardar(self):
        try:
            if not self.nombre.get().strip() or not self.apellidos.get().strip():
                raise ValueError("El nombre y los apellidos son obligatorios.")
            seleccion = self.lista_cargos.curselection()
            if not seleccion:
                raise ValueError("Seleccione un cargo.")
            dias = int(self.dias.get())
            if not 1 <= dias <= 31:
                raise ValueError("Los días trabajados deben estar entre 1 y 31.")
            emp = Empleado(self.nombre.get().strip(), self.apellidos.get().strip(),
                           CARGOS[seleccion[0]], self.genero.get(),
                           self._numero(self.salario, "Salario por día"), dias,
                           self._numero(self.otros, "Otros ingresos"),
                           self._numero(self.salud, "Pagos por salud"),
                           self._numero(self.pension, "Aporte pensiones"))
        except (ValueError, tk.TclError) as err:
            messagebox.showerror("Datos inválidos", str(err) if str(err) else
                                 "Revise los datos ingresados.", parent=self)
            return
        self.nomina.agregar_empleado(emp)
        messagebox.showinfo("Empleado agregado",
                            f"Se agregó a {emp.nombre} {emp.apellidos}.", parent=self)
        if messagebox.askyesno("Agregar otro", "¿Desea agregar otro empleado?", parent=self):
            for v in (self.nombre, self.apellidos, self.salario):
                v.set("")
        else:
            self.destroy()


class VentanaNomina(tk.Toplevel):
    def __init__(self, principal, nomina):
        super().__init__(principal)
        self.title("Calcular nómina")
        self.geometry("560x340")
        cols = ("nombre", "apellidos", "sueldo")
        tabla = ttk.Treeview(self, columns=cols, show="headings")
        for c, t, a in (("nombre", "Nombre", 160), ("apellidos", "Apellidos", 200),
                        ("sueldo", "Sueldo mensual", 140)):
            tabla.heading(c, text=t)
            tabla.column(c, width=a, anchor="e" if c == "sueldo" else "w")
        for e in nomina.empleados:
            tabla.insert("", tk.END, values=(e.nombre, e.apellidos,
                                             f"${e.calcular_salario_mensual():,.2f}"))
        tabla.pack(fill="both", expand=True, padx=10, pady=10)
        ttk.Label(self, text=f"Total de la nómina: ${nomina.calcular_total():,.2f}",
                  font=("Segoe UI", 11, "bold")).pack(pady=(0, 10))


class VentanaPrincipal(tk.Tk):
    def __init__(self):
        super().__init__()
        self.nomina = Nomina()
        self.title("Nómina de empleados")
        self.geometry("420x240")
        self.eval("tk::PlaceWindow . center")

        menu = tk.Menu(self)
        menu.add_command(label="Agregar empleado", command=self.agregar_empleado)
        menu.add_command(label="Calcular nómina", command=self.calcular_nomina)
        menu.add_command(label="Guardar archivo", command=self.guardar_archivo)
        self.config(menu=menu)

        ttk.Label(self, text="Sistema de nómina", font=("Segoe UI", 16, "bold")).pack(pady=(50, 6))
        ttk.Label(self, text="Use la barra de menús para comenzar.").pack()

    def agregar_empleado(self):
        VentanaAgregarEmpleado(self, self.nomina)

    def _hay_empleados(self):
        if not self.nomina.empleados:
            messagebox.showwarning("Sin empleados", "Primero debe agregar al menos un empleado.")
            return False
        return True

    def calcular_nomina(self):
        if self._hay_empleados():
            VentanaNomina(self, self.nomina)

    def guardar_archivo(self):
        if not self._hay_empleados():
            return
        carpeta = filedialog.askdirectory(title="Seleccione la carpeta donde guardar Nómina.txt")
        if not carpeta:
            return
        try:
            ruta = self.nomina.guardar_archivo(carpeta)
            messagebox.showinfo("Archivo guardado", f"Se generó el archivo:\n{ruta}")
        except OSError as err:
            messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{err}")


if __name__ == "__main__":
    VentanaPrincipal().mainloop()
