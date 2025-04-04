import os
import requests
import json
import random
import time
from datetime import datetime
from openpyxl import Workbook, load_workbook
import csv


url = 'http://127.0.0.1:8000/api/config/'

dataset_n=425

device_types = [
        "switch", "router", "bridge", "repeater", "modern", "gateway", "firewall",
        "low_end_sensor", "high_end_sensor", "bulb", "energy_management", "lock",
        "security_alarm", "security_ip_camera", "appliance", "tv", "smartphone",
        "tablet", "pc", "smartwatch", "security_hub", "assistant_hub", "nas"
    ]

max_limits = {
    "switch": 18,
    "router": 16,
    "bridge": 16,
    "repeater": 16,
    "modern": 15,
    "gateway": 15,
    "firewall": 15,
    "low_end_sensor": 15,
    "high_end_sensor": 28,
    "bulb": 24,
    "energy_management": 26,
    "lock": 16,
    "security_alarm": 17,
    "security_ip_camera": 31,
    "appliance": 24,
    "tv": 19,
    "smartphone": 15,
    "tablet": 15,
    "pc": 16,
    "smartwatch": 15,
    "security_hub": 16,
    "assistant_hub": 22,
    "nas": 15
}




def req_sec(n_dev):

    # Número total de unidades a distribuir
    number = n_dev

    # Nombre de la carpeta para guardar archivos
    folder_name = "SECURITY_" + str(dataset_n) + "-" + str(number)


    # Verificar que el número total a distribuir no exceda el máximo permitido
    total_max = sum(max_limits[device] for device in device_types)
    if number > total_max:
        raise ValueError("El número a distribuir excede el máximo permitido para la distribución.")

    # Inicializar la configuración de dispositivos con 0 asignado para cada tipo
    new_config_devices = {device: 0 for device in device_types}
    remaining_number = number

    # Lista de dispositivos que aún pueden recibir asignaciones
    available_devices = device_types.copy()

    # Distribuir aleatoriamente el número entre los dispositivos disponibles
    while remaining_number > 0 and available_devices:
        # Elegir aleatoriamente un tipo de dispositivo de los que aún tienen capacidad
        device_type = random.choice(available_devices)
        
        # Calcular el máximo que se puede asignar a este dispositivo
        max_allocation = min(remaining_number, max_limits[device_type] - new_config_devices[device_type])
        
        if max_allocation > 0:
            allocation = random.randint(1, max_allocation)  # Asignar al menos 1 unidad
            new_config_devices[device_type] += allocation
            remaining_number -= allocation

        # Si el dispositivo ha alcanzado su límite, removerlo de la lista de disponibles
        if new_config_devices[device_type] >= max_limits[device_type]:
            available_devices.remove(device_type)

    # Construir el payload completo
    payload = {
        "newConfigDevices": new_config_devices,
        "availableDevices": {device: '' for device in device_types},
        "properties": {
            "security": "VERYHIGH",
            "usability": "NONE",
            "connectivity": "NONE",
            "sustainability": "NONE"
        }
    }

    # Convertir el payload a un JSON con indentación
    json_payload = json.dumps(payload, indent=4)

    # Definir los headers de la solicitud
    headers = {
        'Content-Type': 'application/json'
    }

    # Crear la carpeta si no existe
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    # Nombres de archivos para guardar la solicitud, respuesta y registros
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    request_filename = os.path.join(folder_name, f"request_{now}.json")
    response_filename = os.path.join(folder_name, f"response_{now}.json")
    csv_filename = os.path.join(folder_name, 'api_response_data.csv')
    excel_filename = 'api_response_data.xlsx'

    try:
        # Guardar la solicitud en un archivo
        with open(request_filename, 'w') as f_request:
            f_request.write(json_payload)

        # Realizar la solicitud y medir el tiempo de respuesta
        start_time = time.time()
        response = requests.post(url, data=json_payload, headers=headers)
        end_time = time.time()
        response_time = end_time - start_time

        # Procesar la respuesta en formato JSON si es posible, o como texto
        response_json = response.json() if 'application/json' in response.headers.get('Content-Type', '') else response.text

        # Guardar la respuesta en un archivo
        with open(response_filename, 'w') as f_response:
            json.dump(response_json, f_response, indent=4)

        # Imprimir información en consola
        print('Status Code:', response.status_code)
        print('Solicitud guardada como:', request_filename)
        print('Respuesta guardada como:', response_filename)
        print('Tiempo de respuesta:', response_time, 'segundos')

        # Registrar la información en un archivo CSV
        with open(csv_filename, 'a', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            if csvfile.tell() == 0:
                csv_writer.writerow(['Timestamp', 'Request Filename', 'Response Filename', 'Response Time (s)'])
            csv_writer.writerow([now, request_filename, response_filename, response_time])

        # Registrar los tiempos de respuesta en un archivo Excel
        if not os.path.exists(excel_filename):
            workbook = Workbook()
            sheet = workbook.active
            sheet.title = 'API Response Data'
            sheet.append([folder_name])  # Cabecera con el nombre de la carpeta
        else:
            workbook = load_workbook(excel_filename)
            sheet = workbook.active

        # Buscar la columna correspondiente al nombre de la carpeta
        col_idx = None
        for col in range(1, sheet.max_column + 1):
            if sheet.cell(row=1, column=col).value == folder_name:
                col_idx = col
                break
        if col_idx is None:
            col_idx = sheet.max_column + 1
            sheet.cell(row=1, column=col_idx).value = folder_name

        # Agregar el tiempo de respuesta en la columna correspondiente
        row_idx = 2  # Comenzamos desde la segunda fila
        while sheet.cell(row=row_idx, column=col_idx).value is not None:
            row_idx += 1
        sheet.cell(row=row_idx, column=col_idx).value = response_time

        workbook.save(excel_filename)

    except Exception as e:
        print("Error al realizar la solicitud:", e)


def req_usa(n_dev):

    # Número total de unidades a distribuir
    number = n_dev

    # Nombre de la carpeta para guardar archivos
    folder_name = "USABILITY_" + str(dataset_n) + "-" + str(number)

    # Verificar que el número total a distribuir no exceda el máximo permitido
    total_max = sum(max_limits[device] for device in device_types)
    if number > total_max:
        raise ValueError("El número a distribuir excede el máximo permitido para la distribución.")

    # Inicializar la configuración de dispositivos con 0 asignado para cada tipo
    new_config_devices = {device: 0 for device in device_types}
    remaining_number = number

    # Lista de dispositivos que aún pueden recibir asignaciones
    available_devices = device_types.copy()

    # Distribuir aleatoriamente el número entre los dispositivos disponibles
    while remaining_number > 0 and available_devices:
        # Elegir aleatoriamente un tipo de dispositivo de los que aún tienen capacidad
        device_type = random.choice(available_devices)
        
        # Calcular el máximo que se puede asignar a este dispositivo
        max_allocation = min(remaining_number, max_limits[device_type] - new_config_devices[device_type])
        
        if max_allocation > 0:
            allocation = random.randint(1, max_allocation)  # Asignar al menos 1 unidad
            new_config_devices[device_type] += allocation
            remaining_number -= allocation

        # Si el dispositivo ha alcanzado su límite, removerlo de la lista de disponibles
        if new_config_devices[device_type] >= max_limits[device_type]:
            available_devices.remove(device_type)

    # Construir el payload completo
    payload = {
        "newConfigDevices": new_config_devices,
        "availableDevices": {device: '' for device in device_types},
        "properties": {
            "security": "NONE",
            "usability": "VERYHIGH",
            "connectivity": "NONE",
            "sustainability": "NONE"
        }
    }

    # Convertir el payload a un JSON con indentación
    json_payload = json.dumps(payload, indent=4)

    # Definir los headers de la solicitud
    headers = {
        'Content-Type': 'application/json'
    }

    # Crear la carpeta si no existe
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    # Nombres de archivos para guardar la solicitud, respuesta y registros
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    request_filename = os.path.join(folder_name, f"request_{now}.json")
    response_filename = os.path.join(folder_name, f"response_{now}.json")
    csv_filename = os.path.join(folder_name, 'api_response_data.csv')
    excel_filename = 'api_response_data.xlsx'

    try:
        # Guardar la solicitud en un archivo
        with open(request_filename, 'w') as f_request:
            f_request.write(json_payload)

        # Realizar la solicitud y medir el tiempo de respuesta
        start_time = time.time()
        response = requests.post(url, data=json_payload, headers=headers)
        end_time = time.time()
        response_time = end_time - start_time

        # Procesar la respuesta en formato JSON si es posible, o como texto
        response_json = response.json() if 'application/json' in response.headers.get('Content-Type', '') else response.text

        # Guardar la respuesta en un archivo
        with open(response_filename, 'w') as f_response:
            json.dump(response_json, f_response, indent=4)

        # Imprimir información en consola
        print('Status Code:', response.status_code)
        print('Solicitud guardada como:', request_filename)
        print('Respuesta guardada como:', response_filename)
        print('Tiempo de respuesta:', response_time, 'segundos')

        # Registrar la información en un archivo CSV
        with open(csv_filename, 'a', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            if csvfile.tell() == 0:
                csv_writer.writerow(['Timestamp', 'Request Filename', 'Response Filename', 'Response Time (s)'])
            csv_writer.writerow([now, request_filename, response_filename, response_time])

        # Registrar los tiempos de respuesta en un archivo Excel
        if not os.path.exists(excel_filename):
            workbook = Workbook()
            sheet = workbook.active
            sheet.title = 'API Response Data'
            sheet.append([folder_name])  # Cabecera con el nombre de la carpeta
        else:
            workbook = load_workbook(excel_filename)
            sheet = workbook.active

        # Buscar la columna correspondiente al nombre de la carpeta
        col_idx = None
        for col in range(1, sheet.max_column + 1):
            if sheet.cell(row=1, column=col).value == folder_name:
                col_idx = col
                break
        if col_idx is None:
            col_idx = sheet.max_column + 1
            sheet.cell(row=1, column=col_idx).value = folder_name

        # Agregar el tiempo de respuesta en la columna correspondiente
        row_idx = 2  # Comenzamos desde la segunda fila
        while sheet.cell(row=row_idx, column=col_idx).value is not None:
            row_idx += 1
        sheet.cell(row=row_idx, column=col_idx).value = response_time

        workbook.save(excel_filename)

    except Exception as e:
        print("Error al realizar la solicitud:", e)


def req_con(n_dev):

    # Número total de unidades a distribuir
    number = n_dev

    # Nombre de la carpeta para guardar archivos
    folder_name = "CONNECTIVITY_" + str(dataset_n) + "-" + str(number)

    # Verificar que el número total a distribuir no exceda el máximo permitido
    total_max = sum(max_limits[device] for device in device_types)
    if number > total_max:
        raise ValueError("El número a distribuir excede el máximo permitido para la distribución.")

    # Inicializar la configuración de dispositivos con 0 asignado para cada tipo
    new_config_devices = {device: 0 for device in device_types}
    remaining_number = number

    # Lista de dispositivos que aún pueden recibir asignaciones
    available_devices = device_types.copy()

    # Distribuir aleatoriamente el número entre los dispositivos disponibles
    while remaining_number > 0 and available_devices:
        # Elegir aleatoriamente un tipo de dispositivo de los que aún tienen capacidad
        device_type = random.choice(available_devices)
        
        # Calcular el máximo que se puede asignar a este dispositivo
        max_allocation = min(remaining_number, max_limits[device_type] - new_config_devices[device_type])
        
        if max_allocation > 0:
            allocation = random.randint(1, max_allocation)  # Asignar al menos 1 unidad
            new_config_devices[device_type] += allocation
            remaining_number -= allocation

        # Si el dispositivo ha alcanzado su límite, removerlo de la lista de disponibles
        if new_config_devices[device_type] >= max_limits[device_type]:
            available_devices.remove(device_type)

    # Construir el payload completo
    payload = {
        "newConfigDevices": new_config_devices,
        "availableDevices": {device: '' for device in device_types},
        "properties": {
            "security": "NONE",
            "usability": "NONE",
            "connectivity": "VERYHIGH",
            "sustainability": "NONE"
        }
    }

    # Convertir el payload a un JSON con indentación
    json_payload = json.dumps(payload, indent=4)

    # Definir los headers de la solicitud
    headers = {
        'Content-Type': 'application/json'
    }

    # Crear la carpeta si no existe
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    # Nombres de archivos para guardar la solicitud, respuesta y registros
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    request_filename = os.path.join(folder_name, f"request_{now}.json")
    response_filename = os.path.join(folder_name, f"response_{now}.json")
    csv_filename = os.path.join(folder_name, 'api_response_data.csv')
    excel_filename = 'api_response_data.xlsx'

    try:
        # Guardar la solicitud en un archivo
        with open(request_filename, 'w') as f_request:
            f_request.write(json_payload)

        # Realizar la solicitud y medir el tiempo de respuesta
        start_time = time.time()
        response = requests.post(url, data=json_payload, headers=headers)
        end_time = time.time()
        response_time = end_time - start_time

        # Procesar la respuesta en formato JSON si es posible, o como texto
        response_json = response.json() if 'application/json' in response.headers.get('Content-Type', '') else response.text

        # Guardar la respuesta en un archivo
        with open(response_filename, 'w') as f_response:
            json.dump(response_json, f_response, indent=4)

        # Imprimir información en consola
        print('Status Code:', response.status_code)
        print('Solicitud guardada como:', request_filename)
        print('Respuesta guardada como:', response_filename)
        print('Tiempo de respuesta:', response_time, 'segundos')

        # Registrar la información en un archivo CSV
        with open(csv_filename, 'a', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            if csvfile.tell() == 0:
                csv_writer.writerow(['Timestamp', 'Request Filename', 'Response Filename', 'Response Time (s)'])
            csv_writer.writerow([now, request_filename, response_filename, response_time])

        # Registrar los tiempos de respuesta en un archivo Excel
        if not os.path.exists(excel_filename):
            workbook = Workbook()
            sheet = workbook.active
            sheet.title = 'API Response Data'
            sheet.append([folder_name])  # Cabecera con el nombre de la carpeta
        else:
            workbook = load_workbook(excel_filename)
            sheet = workbook.active

        # Buscar la columna correspondiente al nombre de la carpeta
        col_idx = None
        for col in range(1, sheet.max_column + 1):
            if sheet.cell(row=1, column=col).value == folder_name:
                col_idx = col
                break
        if col_idx is None:
            col_idx = sheet.max_column + 1
            sheet.cell(row=1, column=col_idx).value = folder_name

        # Agregar el tiempo de respuesta en la columna correspondiente
        row_idx = 2  # Comenzamos desde la segunda fila
        while sheet.cell(row=row_idx, column=col_idx).value is not None:
            row_idx += 1
        sheet.cell(row=row_idx, column=col_idx).value = response_time

        workbook.save(excel_filename)

    except Exception as e:
        print("Error al realizar la solicitud:", e)



def req_sus(n_dev):

    # Número total de unidades a distribuir
    number = n_dev

    # Nombre de la carpeta para guardar archivos
    folder_name = "SUSTAINABILITY_" + str(dataset_n) + "-" + str(number)

    # Verificar que el número total a distribuir no exceda el máximo permitido
    total_max = sum(max_limits[device] for device in device_types)
    if number > total_max:
        raise ValueError("El número a distribuir excede el máximo permitido para la distribución.")

    # Inicializar la configuración de dispositivos con 0 asignado para cada tipo
    new_config_devices = {device: 0 for device in device_types}
    remaining_number = number

    # Lista de dispositivos que aún pueden recibir asignaciones
    available_devices = device_types.copy()

    # Distribuir aleatoriamente el número entre los dispositivos disponibles
    while remaining_number > 0 and available_devices:
        # Elegir aleatoriamente un tipo de dispositivo de los que aún tienen capacidad
        device_type = random.choice(available_devices)
        
        # Calcular el máximo que se puede asignar a este dispositivo
        max_allocation = min(remaining_number, max_limits[device_type] - new_config_devices[device_type])
        
        if max_allocation > 0:
            allocation = random.randint(1, max_allocation)  # Asignar al menos 1 unidad
            new_config_devices[device_type] += allocation
            remaining_number -= allocation

        # Si el dispositivo ha alcanzado su límite, removerlo de la lista de disponibles
        if new_config_devices[device_type] >= max_limits[device_type]:
            available_devices.remove(device_type)

    # Construir el payload completo
    payload = {
        "newConfigDevices": new_config_devices,
        "availableDevices": {device: '' for device in device_types},
        "properties": {
            "security": "NONE",
            "usability": "NONE",
            "connectivity": "NONE",
            "sustainability": "VERYHIGH"
        }
    }

    # Convertir el payload a un JSON con indentación
    json_payload = json.dumps(payload, indent=4)

    # Definir los headers de la solicitud
    headers = {
        'Content-Type': 'application/json'
    }

    # Crear la carpeta si no existe
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    # Nombres de archivos para guardar la solicitud, respuesta y registros
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    request_filename = os.path.join(folder_name, f"request_{now}.json")
    response_filename = os.path.join(folder_name, f"response_{now}.json")
    csv_filename = os.path.join(folder_name, 'api_response_data.csv')
    excel_filename = 'api_response_data.xlsx'

    try:
        # Guardar la solicitud en un archivo
        with open(request_filename, 'w') as f_request:
            f_request.write(json_payload)

        # Realizar la solicitud y medir el tiempo de respuesta
        start_time = time.time()
        response = requests.post(url, data=json_payload, headers=headers)
        end_time = time.time()
        response_time = end_time - start_time

        # Procesar la respuesta en formato JSON si es posible, o como texto
        response_json = response.json() if 'application/json' in response.headers.get('Content-Type', '') else response.text

        # Guardar la respuesta en un archivo
        with open(response_filename, 'w') as f_response:
            json.dump(response_json, f_response, indent=4)

        # Imprimir información en consola
        print('Status Code:', response.status_code)
        print('Solicitud guardada como:', request_filename)
        print('Respuesta guardada como:', response_filename)
        print('Tiempo de respuesta:', response_time, 'segundos')

        # Registrar la información en un archivo CSV
        with open(csv_filename, 'a', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            if csvfile.tell() == 0:
                csv_writer.writerow(['Timestamp', 'Request Filename', 'Response Filename', 'Response Time (s)'])
            csv_writer.writerow([now, request_filename, response_filename, response_time])

        # Registrar los tiempos de respuesta en un archivo Excel
        if not os.path.exists(excel_filename):
            workbook = Workbook()
            sheet = workbook.active
            sheet.title = 'API Response Data'
            sheet.append([folder_name])  # Cabecera con el nombre de la carpeta
        else:
            workbook = load_workbook(excel_filename)
            sheet = workbook.active

        # Buscar la columna correspondiente al nombre de la carpeta
        col_idx = None
        for col in range(1, sheet.max_column + 1):
            if sheet.cell(row=1, column=col).value == folder_name:
                col_idx = col
                break
        if col_idx is None:
            col_idx = sheet.max_column + 1
            sheet.cell(row=1, column=col_idx).value = folder_name

        # Agregar el tiempo de respuesta en la columna correspondiente
        row_idx = 2  # Comenzamos desde la segunda fila
        while sheet.cell(row=row_idx, column=col_idx).value is not None:
            row_idx += 1
        sheet.cell(row=row_idx, column=col_idx).value = response_time

        workbook.save(excel_filename)

    except Exception as e:
        print("Error al realizar la solicitud:", e)
