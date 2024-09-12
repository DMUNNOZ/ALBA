import subprocess
import time

n = 100

script_path = 'multi_client.py'

for i in range(n):
    print(f"Ejecutando {i+1}/{n}...")
    time.sleep(0.3)
    subprocess.run(['python', script_path])

print("Ejecuciones completadas.")
