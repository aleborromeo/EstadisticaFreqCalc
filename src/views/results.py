import ttkbootstrap as ttkb
import tkinter as tk
from tkinter import ttk , messagebox , IntVar
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class VentanaProcesamiento:
    tabla_contador = 1
    grafico_contador = 1

    def __init__(self, father_window , data , precision_from_main):
        try:
            self.father_window = father_window

            self.data = data
            self.root = ttkb.Window(themename="flatly")
            self.root.title("Procesamiento de Datos")
            self.root.iconbitmap("assets/icono.ico")
            self.root.configure(bg="#F5ECD5", highlightthickness=0, bd=0)

            width, height = 1500, 900
            x = (self.root.winfo_screenwidth() - width) // 2
            y = (self.root.winfo_screenheight() - height) // 2
            self.root.geometry(f"{width}x{height}+{x}+{y}")

            self.root.protocol("WM_DELETE_WINDOW" , self.regresar)

            self.contenedor = tk.Frame(self.root, bg="#F5ECD5", highlightthickness=0, bd=0)
            self.contenedor.pack(padx=20, pady=20, fill="both", expand=True)

            self.tabla = None
            self.df_frecuencia = None

            self.precision = IntVar(self.root)
            self.Input_Precision = ttk.Spinbox(self.root , from_=1 , to=10 , increment=1 , textvariable=self.precision , command=self.Uptade_Table , state="readonly" , width=3)
            self.Input_Precision.place(x=500 , y=20)
            self.Input_Precision.set(precision_from_main)
            
            self.mostrar_tabla_frecuencia()

            self.mostrar_resultados_estadisticos()
            self.mostrar_grafico()

            btn_regresar = ttkb.Button(self.contenedor, text="🔄 Volver a calcular", style="success.TButton", command=self.regresar)
            btn_regresar.pack(pady=10)
            btn_regresar.place(x=500, y=850)

            self.root.mainloop()
            self.root.resizable(False , False)
        except Exception as e:
            messagebox.showwarning("Alerta" , f"{e}")

    def Uptade_Table(self):
        if(self.tabla):
            for item in self.tabla.get_children():
                self.tabla.delete(item)
        if(self.df_frecuencia.empty):
            raise Exception("No se encontraron datos.")
        
        self.tabla.tag_configure("evenrow", background="#F2F2F2")
        self.tabla.tag_configure("oddrow", background="#FFFFFF")

        for index in range(0 , len(self.data["fi"])):
            tag = "evenrow" if index % 2 == 0 else "oddrow"
            if(self.data["tipo"] == "Continua"):
                clases = [f"[ {i[0]} - {i[1]} >" for i in self.data["intervalos"]]
                self.tabla.insert("", tk.END, values=(
                    clases[index],
                    f"{self.data["fi"][index]:.{self.precision.get()}f}",
                    f"{self.data["hi"][index]:.{self.precision.get()}f}",
                    f"{self.data["Hi"][index]:.{self.precision.get()}f}",
                    f"{self.data["pi"][index]:.{self.precision.get()}f}",
                    f"{self.data["Pi"][index]:.{self.precision.get()}f}",
                ) , tags=(tag, ))
            else:
                self.tabla.insert("", tk.END, values=(
                    self.data["fi"][index],
                    f"{self.data["fi"][index]:.{self.precision.get()}f}",
                    f"{self.data["hi"][index]:.{self.precision.get()}f}",
                    f"{self.data["Hi"][index]:.{self.precision.get()}f}",
                    f"{self.data["pi"][index]:.{self.precision.get()}f}",
                    f"{self.data["Pi"][index]:.{self.precision.get()}f}",
                ) , tags=(tag, ))

    def mostrar_tabla_frecuencia(self):
        if self.data["tipo"] == "Discreta":
            self.df_frecuencia = pd.DataFrame({
                "Clase": self.data["xi"],
                "Frecuencia": self.data["fi"],
                "Frec. Relativa": self.data["hi"],
                "Frec. Rel. Acum.": self.data["Hi"],
                "Pi%": self.data["pi"],
                "Pi Acum.": self.data["Pi"]
            })
        elif self.data["tipo"] == "Continua":
            clases = [f"[ {i[0]} - {i[1]} >" for i in self.data["intervalos"]]
            self.df_frecuencia = pd.DataFrame({
                "Clase": clases,
                "Frecuencia": self.data["fi"],
                "Frec. Relativa": self.data["hi"],
                "Frec. Rel. Acum.": self.data["Hi"],
                "Pi%": self.data["pi"],
                "Pi Acum.": self.data["Pi"],
            })
        else:
            self.df_frecuencia = pd.DataFrame()  # fallback

        # Tabla en Treeview
        if self.df_frecuencia.empty:
            raise Exception("No se encontraron datos.")
        else:
            columnas = list(self.df_frecuencia.columns)
            filas_totales = len(self.df_frecuencia)

            titulo = tk.Label(self.contenedor, text=f"Tabla {self.tabla_contador:02d}: Frecuencia", font=("Segoe UI", 12, "bold"), bg="#F5ECD5")
            titulo.pack(pady=(10, 5))

            style = ttk.Style()
            style.theme_use("clam")
            style.configure("Custom.Treeview", background="#FFFFFF", foreground="black", rowheight=25 , font=("Segoe UI", 10))
            style.layout("Custom.Treeview", [
                ('Treeview.field', {'sticky': 'nswe', 'border': '1', 'children': [
                    ('Treeview.padding', {'sticky': 'nswe', 'children': [
                        ('Treeview.treearea', {'sticky': 'nswe'})
                    ]})
                ]})
            ])
            style.configure("Custom.Treeview.Heading", background="#5D6D7E", foreground="white" , font=("Segoe UI", 10 , "bold"))
            

            tabla_frame = tk.Frame(self.contenedor, bg="#F5ECD5", highlightthickness=0)
            tabla_frame.pack(pady=(0, 5), fill="both", expand=True)

            self.tabla = ttk.Treeview(tabla_frame, columns=columnas, show="headings", height=filas_totales, style="Custom.Treeview")
            self.tabla.config(height=12)

            scrollbar_y = ttk.Scrollbar(tabla_frame , orient="vertical" , command=self.tabla.yview)
            self.tabla.configure(yscrollcommand=scrollbar_y.set)

            self.tabla.grid(row=0, column=0, sticky="nsew")
            scrollbar_y.grid(row=0 , column=1 , sticky="ns")

            tabla_frame.grid_rowconfigure(0, weight=1)

            self.tabla.tag_configure("evenrow", background="#F2F2F2")
            self.tabla.tag_configure("oddrow", background="#FFFFFF")

            tabla_frame.grid_rowconfigure(0, weight=1)
            tabla_frame.grid_columnconfigure(0, weight=1)
            for col in columnas:
                self.tabla.heading(col, text=col)
                self.tabla.column(col, anchor="center", width=130)

            for index in range(0 , len(self.data["fi"])):
                tag = "evenrow" if index % 2 == 0 else "oddrow"
                if(self.data["tipo"] == "Continua"):
                    self.tabla.insert("", tk.END, values=(
                        clases[index],
                        f"{self.data["fi"][index]:.{self.precision.get()}f}",
                        f"{self.data["hi"][index]:.{self.precision.get()}f}",
                        f"{self.data["Hi"][index]:.{self.precision.get()}f}",
                        f"{self.data["pi"][index]:.{self.precision.get()}f}",
                        f"{self.data["Pi"][index]:.{self.precision.get()}f}",
                    ) , tags=(tag,))
                else:
                    self.tabla.insert("", tk.END, values=(
                        self.data["fi"][index],
                        f"{self.data["fi"][index]:.{self.precision.get()}f}",
                        f"{self.data["hi"][index]:.{self.precision.get()}f}",
                        f"{self.data["Hi"][index]:.{self.precision.get()}f}",
                        f"{self.data["pi"][index]:.{self.precision.get()}f}",
                        f"{self.data["Pi"][index]:.{self.precision.get()}f}",
                    ) , tags=(tag, ))

    def mostrar_grafico(self):
        if(self.df_frecuencia.empty):
            raise Exception("No se encontraron datos.")
        
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(self.df_frecuencia["Clase"], self.df_frecuencia["Frecuencia"], color="#5D6D7E")
        ax.set_title(f"Gráfico {self.grafico_contador:02d}: Distribución de Frecuencias", fontsize=14, fontweight="bold")
        ax.set_xlabel("Clases", fontsize=12)
        ax.set_ylabel("Frecuencia", fontsize=12)

    # Etiquetas en las barras (Pi%)
        for i, v in enumerate(self.df_frecuencia["Frecuencia"]):
            ax.text(i, v + 0.5, f'{self.df_frecuencia["Pi%"].iloc[i]:.2f}%', ha='center', fontsize=10)

        plt.tight_layout()

        grafico_frame = tk.Frame(self.contenedor, bg="#F5ECD5")
        grafico_frame.pack(pady=(10, 0), fill="both", expand=True)

        canvas = FigureCanvasTkAgg(fig, master=grafico_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        VentanaProcesamiento.grafico_contador += 1


    def mostrar_resultados_estadisticos(self):
        marco_resultados = tk.Frame(self.contenedor, bg="#F5ECD5")
        marco_resultados.pack(pady=15, fill="x")

        titulo = tk.Label(marco_resultados, text="Medidas Estadísticas", font=("Segoe UI", 12, "bold"), bg="#F5ECD5")
        titulo.pack(anchor="w")

        texto = ""
        texto += f"Media: {self.data['media']:.2f}\n"
        texto += f"Mediana: {self.data['mediana']:.2f}\n"
        if isinstance(self.data['moda'], list):
            texto += f"Moda: {', '.join(map(str, self.data['moda']))}\n"
        else:
            texto += f"Moda: {self.data['moda']}\n"
        texto += f"Varianza: {self.data['varianza']:.2f}\n"
        texto += f"Desviación Estándar: {self.data['desviacion']:.2f}\n"
        texto += f"Coef. de Variación: {self.data['coef_variacion']:.2f}%"

        label = tk.Label(marco_resultados, text=texto, justify="left", font=("Segoe UI", 10), bg="#F5ECD5")
        label.pack(anchor="w")

    
    def regresar(self):
        self.father_window.state(newstate="normal")
        self.father_window.lift()

        for widget in self.root.winfo_children():
            widget.destroy()
        self.root.destroy()


