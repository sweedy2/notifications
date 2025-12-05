import tkinter as tk
from tkinter import messagebox
import json
import schedule
import threading
import time
from datetime import datetime
import requests
import os

# -------------------------
# CONFIGURACIÓN PUSHHOVER
# -------------------------
PUSHOVER_USER_KEY = os.getenv("PUSHOVER_USER_KEY") 
PUSHOVER_APP_TOKEN = os.getenv("PUSHOVER_APP_TOKEN")  # Reemplaza con tu token de aplicación

# -------------------------
# GESTIÓN DE TAREAS
# -------------------------
def cargar_tareas():
    try:
        with open("tareas.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def guardar_tareas(tareas):
    with open("tareas.json", "w") as f:
        json.dump(tareas, f, indent=4)

# -------------------------
# ENVÍO DE NOTIFICACIÓN
# -------------------------
def enviar_notificacion(tarea):
    data = {
        "token": PUSHOVER_APP_TOKEN,
        "user": PUSHOVER_USER_KEY,
        "message": tarea["mensaje"],
        "sound": "alien",  # Cambia por el sonido que quieras
        "priority": 1
    }
    requests.post("https://api.pushover.net/1/messages.json", data=data)
    log(f"🔔 Notificación enviada: {tarea['mensaje']}")

# -------------------------
# REVISIÓN DE TAREAS
# -------------------------
def revisar_tareas():
    tareas = cargar_tareas()
    ahora = datetime.now()
    nuevas = []

    for t in tareas:
        if (t["ano"], t["mes"], t["dia"], t["hora"], t["minuto"]) == \
           (ahora.year, ahora.month, ahora.day, ahora.hour, ahora.minute):
            enviar_notificacion(t)
        else:
            nuevas.append(t)

    guardar_tareas(nuevas)

def loop_notificaciones():
    schedule.every(10).seconds.do(revisar_tareas)
    while True:
        schedule.run_pending()
        time.sleep(1)

# -------------------------
# INTERFAZ GRÁFICA
# -------------------------
def log(text):
    log_box.insert(tk.END, text + "\n")
    log_box.see(tk.END)

def crear_tarea_gui():
    try:
        mensaje = mensaje_entry.get().strip()
        hora, minuto = map(int, hora_entry.get().split(":"))
        dia, mes, ano = map(int, fecha_entry.get().split("/"))

        tarea = {
            "mensaje": mensaje,
            "hora": hora,
            "minuto": minuto,
            "dia": dia,
            "mes": mes,
            "ano": ano
        }

        tareas = cargar_tareas()
        tareas.append(tarea)
        guardar_tareas(tareas)
        log(f"✅ Tarea programada: {mensaje} — {dia:02d}/{mes:02d}/{ano} {hora:02d}:{minuto:02d}")
        messagebox.showinfo("Éxito", "Tarea creada y programada correctamente.")

        # -------------------------------
        # Limpiar las casillas automáticamente
        # -------------------------------
        mensaje_entry.delete(0, tk.END)
        hora_entry.delete(0, tk.END)
        fecha_entry.delete(0, tk.END)

    except Exception as e:
        messagebox.showerror("Error", f"Revisa los formatos de hora y fecha.\nEjemplo hora: 17:40, fecha: 05/12/2025\n{str(e)}")

# -------------------------
# VENTANA PRINCIPAL
# -------------------------
root = tk.Tk()
root.title("Programador de Notificaciones Pushover")
root.geometry("500x400")
root.configure(bg="#1e1e1e")

# Título
title_label = tk.Label(root, text="Programador de Notificaciones", font=("Segoe UI", 16, "bold"),
                       fg="white", bg="#1e1e1e")
title_label.pack(pady=10)

# Entrada de mensaje
tk.Label(root, text="Mensaje:", fg="white", bg="#1e1e1e").pack(anchor="w", padx=20)
mensaje_entry = tk.Entry(root, width=50)
mensaje_entry.pack(padx=20, pady=5)

# Entrada de hora
tk.Label(root, text="Hora (HH:MM):", fg="white", bg="#1e1e1e").pack(anchor="w", padx=20)
hora_entry = tk.Entry(root, width=20)
hora_entry.pack(padx=20, pady=5)

# Entrada de fecha
tk.Label(root, text="Fecha (DD/MM/AAAA):", fg="white", bg="#1e1e1e").pack(anchor="w", padx=20)
fecha_entry = tk.Entry(root, width=20)
fecha_entry.pack(padx=20, pady=5)

# Botón crear tarea
tk.Button(root, text="Crear y Programar Tarea", bg="#4CAF50", fg="white",
          font=("Segoe UI", 12, "bold"), command=crear_tarea_gui).pack(pady=15)

# Logs
tk.Label(root, text="Logs:", fg="white", bg="#1e1e1e", font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=20)
log_box = tk.Text(root, height=10, bg="#111111", fg="white")
log_box.pack(fill="both", expand=True, padx=20, pady=5)

# -------------------------
# HILO DE NOTIFICACIONES
# -------------------------
threading.Thread(target=loop_notificaciones, daemon=True).start()

root.mainloop()
