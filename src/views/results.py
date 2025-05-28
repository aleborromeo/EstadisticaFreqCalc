import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from path_manager import Get_Resource_Path
import ttkbootstrap as ttkb
import tkinter as tk
from tkinter import ttk, IntVar
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

from ttkbootstrap import Style

from tkinter import filedialog
from datetime import datetime

class VentanaProcesamiento:
    tabla_contador = 1
    grafico_contador = 1

    def __init__(self, main_window , data, precision_from_main):
        self.main_window = main_window
        self.main_window.state(newstate="withdraw")

        self.data = data
        self.root = ttkb.Window(themename="flatly")
        self.root.title("Procesamiento de Datos")
        self.root.iconbitmap(Get_Resource_Path("assets/icono.ico"))
        self.root.configure(bg="#F5ECD5", highlightthickness=0, bd=0)
        self.root.protocol("WM_DELETE_WINDOW" , self.ir_a_main)
        self.style = ttkb.Style() 
        self.estilos_personalizados()

        self.root.state('zoomed')
        self.fig = None

        # Calcular el tamaño de la ventana
        width = 1920
        height = 1080

        # Obtener las dimensiones de la pantalla
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()


        # Calcular la posición para centrar la ventana
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)

        # Establecer la geometría de la ventana centrada
        self.root.geometry(f"{width}x{height}+{x}+{y}")

        self.root.minsize(1100, 600)

        # Canvas + scrollbar general
        self.canvas = tk.Canvas(self.root, bg="#F5ECD5", highlightthickness=0)
        self.scroll_y = tk.Scrollbar(
            self.root, orient="vertical", command=self.canvas.yview
        )
        self.scroll_y.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.configure(yscrollcommand=self.scroll_y.set)

        self.contenedor = tk.Frame(self.canvas, bg="#F5ECD5")
        self.canvas.create_window((0, 0), window=self.contenedor, anchor="nw")

        self.contenedor.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # Frame centrado que contendrá los frames izquierdo y derecho
        self.frame_central = tk.Frame(self.contenedor, bg="#F5ECD5")
        self.frame_central.pack(pady=20)

        # Ajusta el ancho máximo deseado del contenido central (por ejemplo, 1200 px)
        self.frame_central.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.frame_central.configure(width=min(e.width, 1200)))

        self.decimals_precision = IntVar(self.root)
        self.decimals_precision.set(precision_from_main)

        self.tabla = None
        self.tabla_estadistica = None

        # Layout grid
        self.contenedor.grid_columnconfigure(0, weight=3, uniform="group1")
        self.contenedor.grid_columnconfigure(1, weight=2, uniform="group1")
        self.contenedor.grid_rowconfigure(0, weight=1)
        # Frames izquierdo y derecho
        self.frame_izquierdo = ttkb.Frame(
            self.frame_central, bootstyle="light", padding=10
        )
        self.frame_izquierdo.grid(
            row=0, column=0, sticky="nsew", padx=(20, 10), pady=20
        )

        self.frame_derecho = ttkb.Frame(
            self.frame_central,
            bootstyle="light",
            padding=10,
            width=1000,
            height=500  # Ajusta según lo que necesites
        )
        self.frame_derecho.grid(row=0, column=1, sticky="n", padx=(10, 20), pady=20)
        self.frame_derecho.grid_propagate(False) # Muy importante: evita expansión automática

        self.frame_central.grid_columnconfigure(0, weight=1)
        #self.frame_central.grid_columnconfigure(1, weight=0)  # ⬅️ evita que la derecha crezca


        # Control precisión y tabla frecuencia
        precision_label = ttkb.Label(
            self.frame_izquierdo, text="Precisión decimales:", font=("Segoe UI", 11)
        )
        precision_label.pack(anchor="nw")
        self.spinbox_precision = ttkb.Spinbox(
            self.frame_izquierdo,
            from_=0,
            to=10,
            width=6,
            textvariable=self.decimals_precision,
            state="readonly",
            command=self.update_table,
        )
        self.spinbox_precision.pack(anchor="nw", pady=(0, 10))

        tabla_title = ttkb.Label(
            self.frame_izquierdo,
            text=f"Tabla {self.tabla_contador:02d}: Frecuencia",
            font=("Segoe UI", 13, "bold"),
        )
        tabla_title.pack(anchor="nw")

        self.mostrar_tabla_frecuencia(self.decimals_precision.get())

        # Gráfico: crea frame y figura solo UNA VEZ
        self.grafico_frame = tk.Frame(self.frame_izquierdo, bg="#F5ECD5")
        self.grafico_frame.pack(fill="x", pady=10)

        plt.style.use('ggplot')

        self.fig, self.ax = plt.subplots(figsize=(10, 4))
        self.canvas_fig = FigureCanvasTkAgg(self.fig, master=self.grafico_frame)
        self.canvas_fig.get_tk_widget().pack(fill="both", expand=True)

        self._dibujar_grafico()

        # Tabla medidas estadísticas
        medidas_title = ttkb.Label(
            self.frame_derecho,
            text=f"Tabla {self.tabla_contador + 1:02d}: Medidas Estadísticas",
            font=("Segoe UI", 13, "bold"),
        )
        medidas_title.pack(anchor="nw", pady=(0, 10))

        self.mostrar_resultados_estadisticos(self.decimals_precision.get())

        btn_regresar = ttkb.Button(
            self.root,
            text="🔄 Volver a calcular",
            style="Custom.TButton",
            command=self.ir_a_main,
            width=40
        )
        btn_regresar.place(x=1425, y=600)
        
        btn_exportarGrafico = ttkb.Button(
            self.root,
            text="Exportar Gráfico",
            style="Custom.TButton",
            command=self.export_graphs,
            width=40
        )
        btn_exportarGrafico.place(x=1425, y=540)

        self.root.mainloop()

    def mostrar_tabla_frecuencia(self, precision):
        if(self.tabla):
            for item in self.tabla.get_children():
                self.tabla.delete(item)

        clases = None
        if self.data["tipo"] == "Discreta":
            clases = self.data["xi"]
        elif self.data["tipo"] == "Continua":
            clases = [f"[ {i[0]} - {i[1]} >" for i in self.data["intervalos"]]

        df_frecuencia = pd.DataFrame(
            {
                "Clase": clases,
                "Frecuencia": self.data["fi"],
                "Frec. Relativa": self.data["hi"],
                "Frec. Rel. Acum.": self.data["Hi"],
                "Pi%": self.data["pi"],
                "Pi Acum.": self.data["Pi"],
            }
        )

        self.total_row = (
            "Total",
            f'{np.sum(self.data["fi"])}',
            f'{np.sum(self.data["hi"]):.2f}',
            "",
            f'{np.sum(self.data["pi"]):.2f}%',
            "",
        )

        columnas = list(df_frecuencia.columns)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Custom.Treeview", background="#FFFFFF", foreground="black", rowheight=25
        )
        style.configure(
            "Custom.Treeview.Heading", background="#5D6D7E", foreground="white"
        )

        tabla_frame = tk.Frame(self.frame_izquierdo, bg="#F5ECD5")
        tabla_frame.pack(fill="both", expand=True)

        if(not self.tabla):
            style = ttk.Style()
            style.theme_use("clam")
            style.configure("Custom.Treeview", background="#FFFFFF", foreground="black", rowheight=25)
            style.configure("Custom.Treeview.Heading", background="#5D6D7E", foreground="white")

            tabla_frame = tk.Frame(self.frame_izquierdo, bg="#F5ECD5")
            tabla_frame.pack(fill="both", expand=True)

            scroll_y = tk.Scrollbar(tabla_frame, orient="vertical")
            scroll_y.pack(side="right", fill="y")
            scroll_x = tk.Scrollbar(tabla_frame, orient="horizontal")
            scroll_x.pack(side="bottom", fill="x")
            self.tabla = ttk.Treeview(tabla_frame,
                                    columns=columnas,
                                    show="headings",
                                    yscrollcommand=scroll_y.set,
                                    xscrollcommand=scroll_x.set,
                                    height=8,
                                    style="Custom.Treeview")

            scroll_y.config(command=self.tabla.yview)
            scroll_x.config(command=self.tabla.xview)

        for col in columnas:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, anchor="center", width=130)

        for index in range(len(self.data["fi"])):
            tag = "evenrow" if index % 2 == 0 else "oddrow"
            self.tabla.insert(
                "",
                tk.END,
                values=(
                    clases[index],
                    self.data["fi"][index],
                    f'{self.data["hi"][index]:.{precision}f}',
                    f'{self.data["Hi"][index]:.{precision}f}',
                    f'{self.data["pi"][index]:.{precision}f}%',
                    f'{self.data["Pi"][index]:.{precision}f}%',
                ),
                tags=(tag,),
            )
        self.tabla.insert("", tk.END, values=self.total_row)

        self.tabla.pack(fill="both", expand=True)

    def _dibujar_grafico(self):
        if(self.data["tipo"] == "Discreta"):
            self.ax.clear()

            clases = None
            if self.data["tipo"] == "Discreta":
                clases = self.data["xi"]
            elif self.data["tipo"] == "Continua":
                clases = [f"[ {i[0]} - {i[1]} >" for i in self.data["intervalos"]]

            self.ax.bar(clases, self.data["fi"], color="#69b3a2" , edgecolor="black" , width=0.6)
            self.ax.set_title(f"Gráfico {self.grafico_contador:02d}: Distribución de Frecuencias", fontsize=12, fontweight="bold")
            self.ax.set_xticks(range(len(clases)))
            self.ax.set_xticklabels(clases, fontsize=9, rotation=30, rotation_mode="anchor", ha="right")

            self.ax.set_xlabel("Clases", fontsize=12)
            self.ax.set_ylabel("Frecuencia", fontsize=12)

            self.ax.grid(axis='y', linestyle='--', alpha=0.5)

            for i, v in enumerate(self.data["fi"]):
                self.ax.text(i, v + (v * 0.01), f'{self.data["fi"][i]}', ha='center' , fontsize=10)
            
            for spine in ['top', 'right']:
                self.fig.gca().spines[spine].set_visible(False)
            
            self.fig.tight_layout()
            self.canvas_fig.draw()
        elif(self.data["tipo"] == "Continua"):
            if(not "data" in self.data):
                raise Exception("No se encontraron los datos originales.")
            self.ax.clear()

            inf_limits = [limits[0] for limits in self.data["intervalos"]]
            cuentas, bordes, patches = self.ax.hist(self.data["data"] , bins=inf_limits, edgecolor='white', align='mid', rwidth=1 , color="#69b3a2" , alpha=0.8)
            for i in range(len(cuentas)):
                altura = cuentas[i]
                centro = (bordes[i] + bordes[i+1]) / 2
                self.ax.text(centro, altura + (altura * 0.01), str(int(altura)), ha='center', va='bottom')
            puntos_medios = 0.5 * (bordes[:-1] + bordes[1:])

            self.ax.plot(
                puntos_medios, 
                cuentas, 
                color='crimson', 
                linewidth=2, 
                marker='o', 
                markersize=6,
                markerfacecolor='white',
                markeredgewidth=2
            )

            self.ax.set_xticks(inf_limits)
            # Opcional: Etiquetas y estilo
            self.ax.set_xlabel("Intervalos")
            self.ax.set_ylabel("Frecuencia")
            self.ax.set_title("Grafico N°01 Histograma de Frecuencias")
            self.ax.set_xticks(inf_limits)
            self.ax.set_xticklabels(inf_limits , rotation=30 , rotation_mode="anchor" , ha="right")

            for spine in ['top', 'right']:
                self.fig.gca().spines[spine].set_visible(False)

            self.ax.grid(axis='y', linestyle='--', alpha=0.4)

            self.fig.tight_layout()
            self.canvas_fig.draw()
        else:
            raise Exception("No se detecto el tipo de variable")

    def mostrar_resultados_estadisticos(self , precision):
        if(self.tabla_estadistica):
            for item in self.tabla_estadistica.get_children():
                self.tabla_estadistica.delete(item)

        if(not self.tabla_estadistica):
            self.tabla_estadistica = ttk.Treeview(self.frame_derecho, columns=("Medida", "Valor"), show="headings", height=15)
            self.tabla_estadistica.heading("Medida", text="Medida")
            self.tabla_estadistica.heading("Valor", text="Valor")
            self.tabla_estadistica.column("Medida", anchor="center", width=300)
            self.tabla_estadistica.column("Valor", anchor="center", width=200)

        if(self.data["tipo"] == "Discreta"):
            medidas = [
                ("Numero total de datos (n)", self.data["Numero Datos"]),
                ("Media", f"{self.data['media']:.{precision}f}"),
                ("Mediana", f"{self.data['mediana']:.{precision}f}"),
                ("Moda", "- ".join(f"{data:.{precision}f}" for data in self.data['moda']) if isinstance(self.data['moda'], list) else f"{self.data['moda']:.{precision}f}"),
                ("Varianza", f"{self.data['varianza']:.{precision}f}"),
                ("Desviación Estándar", f"{self.data['desviacion']:.{precision}f}"),
                ("Coef. de Variación", f"{self.data['coef_variacion']:.{precision}f}%")]
        elif(self.data["tipo"] == "Continua"):
            medidas = [
                ("Numero total de datos (n)", self.data["Numero Datos"]),
                ("Vmin", self.data["Vmin"]),
                ("Vmax", self.data["Vmax"]),
                ("Rango (R)", self.data["Rango"]),
                ("Numero de Intervalos (m)", self.data["Numero Intervalos"]),
                ("Amplitud (A)", self.data["Amplitud"]),
                ("Media", f"{self.data['media']:.{precision}f}"),
                ("Mediana", f"{self.data['mediana']:.{precision}f}"),
                ("Moda", "- ".join(f"{data:.{precision}f}" for data in self.data['moda']) if isinstance(self.data['moda'], list) else f"{self.data['moda']:.{precision}f}"),
                ("Varianza", f"{self.data['varianza']:.{precision}f}"),
                ("Desviación Estándar", f"{self.data['desviacion']:.{precision}f}"),
                ("Coef. de Variación", f"{self.data['coef_variacion']:.{precision}f}%")]
        for i, (medida, valor) in enumerate(medidas):
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            self.tabla_estadistica.insert("", tk.END, values=(medida, valor), tags=(tag,))

        self.tabla_estadistica.pack(fill="both", expand=False, padx=(0, 140))
        self.tabla_estadistica.tag_configure("evenrow", background="#F5F5F5")
        self.tabla_estadistica.tag_configure("oddrow", background="#FFFFFF")

    def export_graphs(self):
        PATH = filedialog.askdirectory()
        if(not os.path.exists(PATH)):
            raise Exception("Ruta no valida")

        if(self.data["tipo"] == "Discreta"):
            if(PATH):
                now_time = datetime.now().strftime("%d_%m_%Y %H_%M_%S")
                file_name = f"Image_{now_time}.jpg"
                PATH = os.path.join(PATH , file_name)
                self.fig.savefig(PATH , dpi=300)
        elif(self.data["tipo"] == "Continua"):
            if(PATH):
                now_time = datetime.now().strftime("%d_%m_%Y %H_%M_%S")
                file_name = f"Image_{now_time}.jpg"
                PATH = os.path.join(PATH , file_name)
                self.fig.savefig(PATH , dpi=300)

    def estilos_personalizados(self):
        self.style.configure("Custom.TButton",
            font=("Franklin Gothic Demi", 13),
            foreground="#F5ECD5",
            background="#626F47",
            padding=10,
            borderwidth=0,
            relief="flat")

        self.style.map("Custom.TButton",
            background=[("active", "#4E5A36"), ("!active", "#626F47")],
            foreground=[("disabled", "#A0A0A0"), ("!disabled", "#F5ECD5")])


    def update_table(self):
        self.mostrar_tabla_frecuencia(self.decimals_precision.get())
        self.mostrar_resultados_estadisticos(self.decimals_precision.get())
        
    def ir_a_main(self):
        self.root.quit()
        self.root.destroy()

        style = ttkb.Style()
        style.configure("Custom.TLabel", foreground="#222831", background="#F5ECD5", font=("Franklin Gothic Demi", 13))
        style.configure("Custom.TButton", foreground="#F5ECD5", background="#626F47", font=("Franklin Gothic Demi", 13))
        style.configure("Custom.TEntry", fieldbackground="#FFFFFF", foreground="#222831", font=("Aptos", 12))
        self.main_window.state(newstate="normal")
        self.main_window.lift()
