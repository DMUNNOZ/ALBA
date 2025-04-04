import subprocess
import time
from client import req_sec,req_con,req_sus,req_usa
from multi_client import req_multi
n = 100

script_path = '/home/kali/Escritorio/ALBACSP2/ALBACSP/utils/client.py'
n_devices = [5,10,15,20,25,35,50,75,100,125,150,175,200,225,250,275,300,325]
time.sleep(5)
for j in n_devices:
    for i in range(n):
        print(f"Ejecutando {i+1}/{n}...")
        req_sec(j)
for j in n_devices:
    for i in range(n):
        print(f"Ejecutando {i+1}/{n}...")
        req_con(j)
for j in n_devices:
    for i in range(n):
        print(f"Ejecutando {i+1}/{n}...")
        req_sus(j)
for j in n_devices:
    for i in range(n):
        print(f"Ejecutando {i+1}/{n}...")
        req_usa(j)
for j in n_devices:
    for i in range(n):
        print(f"Ejecutando {i+1}/{n}...")
        req_multi(j)


print("Ejecuciones completadas.")
