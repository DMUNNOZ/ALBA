from rest_framework import viewsets
from .serializers import HomeSerializer,DeviceSerializer,VulnerabilitySerializer,ConnectionSerializer,ConnectionVulnerabilitySerializer,AppSerializer,CWESerializer,PowerSerializer,ConnectivitySerializer
from .models import Home,Device,Vulnerability,Connection,ConnectionVulnerability,App,CWE,Power,Connectivity
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse, JsonResponse
from django.core import serializers
from ortools.sat.python import cp_model
import json
from collections import defaultdict
from django.views.decorators.csrf import csrf_exempt
import re
import sys
sys.setrecursionlimit(30000)

class HomeView(viewsets.ModelViewSet):
    serializer_class = HomeSerializer
    queryset = Home.objects.all()

class DeviceView(viewsets.ModelViewSet):
    serializer_class = DeviceSerializer
    queryset = Device.objects.all()

class AppView(viewsets.ModelViewSet):
    serializer_class = AppSerializer
    queryset = App.objects.all()

class CWEView(viewsets.ModelViewSet):
    serializer_class = CWESerializer
    queryset = CWE.objects.all()

class PowerView(viewsets.ModelViewSet):
    serializer_class = PowerSerializer
    queryset = Power.objects.all()

class ConnectivityView(viewsets.ModelViewSet):
    serializer_class = ConnectivitySerializer
    queryset = Connectivity.objects.all()

class VulnerabilityView(viewsets.ModelViewSet):
    serializer_class = VulnerabilitySerializer
    queryset = Vulnerability.objects.all()

class ConnectionView(viewsets.ModelViewSet):
    serializer_class = ConnectionSerializer
    queryset = Connection.objects.all()

class ConnectionVulnerabilityView(viewsets.ModelViewSet):
    serializer_class = ConnectionVulnerabilitySerializer
    queryset = ConnectionVulnerability.objects.all()

class ImpactMinView(APIView):
    def get(self, request):

        # Obtener el valor especificado por el usuario
        try:
            n = int(request.query_params.get('n'))
        except:
            return JsonResponse({'error': 'Se debe especificar el numero de dispositivos mediante el parametro N.'}, status=400)

        # Obtener todos los dispositivos y sus vulnerabilidades asociadas
        devices = Device.objects.all()

        # Crear modelo de optimización
        model = cp_model.CpModel()

        # Variables: cada dispositivo es una variable binaria (0 o 1)
        device_vars = []
        for device in devices:
            var_name = f'device_{device.id}'
            device_var = model.NewBoolVar(var_name)
            device_vars.append(device_var)
        print('\n' + str(device_vars) + '\n')

        # Obtener los baseScore de las vulnerabilidades asociadas a cada dispositivo
        base_scores_per_device = []
        for device in devices:
            base_scores = [vulnerability.baseScore for vulnerability in device.vulnerabilities.all()]
            total_base_score = sum(map(int, base_scores))
            base_scores_per_device.append((device, total_base_score))
        print('\n' + str(base_scores_per_device) + '\n')

        # Restricción: seleccionar n dispositivos exactamente
        num_selected_devices = sum(device_vars)
        print(num_selected_devices)
        model.Add(num_selected_devices == n)

        # Restricción: la suma total de los baseScore debe ser mínima
        total_base_scores = []
        for i, device in enumerate(devices):
            total_base_score_var = model.NewIntVar(0, sum(score[1] for score in base_scores_per_device), f'total_base_score_{i}')
            total_base_scores.append(total_base_score_var)
        print(str(total_base_scores)+ '\n')

        total_base_score_expr = sum(device_vars[i] * base_scores_per_device[i][1] for i in range(len(devices)))
        print(total_base_score_expr)
        model.Add(total_base_score_expr == sum(total_base_scores))
        print(str(sum(total_base_scores)))
        model.Minimize(sum(total_base_scores))

        # Crear solver
        solver = cp_model.CpSolver()

        # Resolver el modelo
        status = solver.Solve(model)

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            # Mostrar salida en bruto del solver
            for i, device_var in enumerate(device_vars):
                print(f"Dispositivo {i}: {device_var} - Valor asignado: {solver.Value(device_var)}")

            # Obtener los dispositivos seleccionados
            selected_devices = []
            for i, device_var in enumerate(device_vars):
                if solver.Value(device_var) == 1:
                    selected_devices.append(base_scores_per_device[i])

            print("Dispositivos seleccionados:", selected_devices)

            # Crear un diccionario para almacenar los datos de los dispositivos seleccionados
            selected_devices_data = []
            for device, total_base_score in selected_devices:
                vulnerabilities = [{'identifier': vulnerability.identifier, 'baseScore': vulnerability.baseScore} for vulnerability in device.vulnerabilities.all()]
                selected_devices_data.append({
                    'device': device.model,
                    'total_base_score': total_base_score,
                    'vulnerabilities': vulnerabilities
                })

            response_data = {
                'status': 'success',
                'selected_devices': selected_devices_data
            }
        else:
            response_data = {
                'status': 'error',
                'message': 'No se pudo encontrar una solución óptima.'
            }

        return JsonResponse(response_data)
        

class ConnectionsMaxView(APIView):
    def get(self, request):
        # Obtener el valor especificado por el usuario
        try:
            tec_user = str(request.query_params.get('tec'))
            n = int(request.query_params.get('n'))
        except:
            return JsonResponse({'error': 'Se debe especificar el numero de dispositivos mediante el parametro TEC y el numero de smart homes con N.'}, status=400)

        # Obtener todos los hogares
        homes = Home.objects.all()

        # Crear modelo de optimización
        model = cp_model.CpModel()

        # Variables: cada hogar es una variable binaria (0 o 1)
        home_vars = []
        for home in homes:
            var_name = f'home_{home.id}'
            home_var = model.NewBoolVar(var_name)
            home_vars.append(home_var)
        
        print('\n' + str(home_vars) + '\n')

        # Obtener la equivalencia tecnologica con la del usuario de cada smart home
        tec_per_home = []
        for home in homes:
            cont = 0
            for device in home.devices.all():
                tecs = device.connectivities.all()
                for tec in tecs:
                    if tec.technology == tec_user:
                        cont +=1
            tec_per_home.append((home, cont))
        print(str(tec_per_home))
           
        # Restricción: seleccionar n hogares como maximo
        num_selected_homes = sum(home_vars)
        model.Add(num_selected_homes <= n)

        total_tec_n = []
        for i, home in enumerate(homes):
            total_tec_n_var = model.NewIntVar(0, sum(t[1] for t in tec_per_home), f'total_tec_n_{i}')
            total_tec_n.append(total_tec_n_var)
        print(str(total_tec_n)+ '\n')

        total_tecs_expr = sum(home_vars[i] * tec_per_home[i][1] for i in range(len(homes)))
        print(total_tecs_expr)
        model.Add(total_tecs_expr == sum(total_tec_n))
        model.Maximize(sum(total_tec_n))

        # Crear solver
        solver = cp_model.CpSolver()

        # Resolver el modelo
        status = solver.Solve(model)

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            # Mostrar salida en bruto del solver
            for i, home_var in enumerate(home_vars):
                print(f"Home {i}: {home_var} - Valor asignado: {solver.Value(home_var)}")

            # Obtener los hogares seleccionados
            selected_homes = []
            for i, home_var in enumerate(home_vars):
                if solver.Value(home_var) == 1:
                    selected_homes.append(tec_per_home[i])

            print("Dispositivos seleccionados:", selected_homes)

            # Crear un diccionario para almacenar los datos de los dispositivos seleccionados
            selected_home_data = []
            for home, total_tecn in selected_homes:
                selected_home_data.append({
                    'home': home.id,
                    'total_tec_n': total_tecn
                })

            response_data = {
                'status': 'success',
                'selected_homes': selected_home_data
            }
        else:
            response_data = {
                'status': 'error',
                'message': 'No se pudo encontrar una solución óptima.'
            }

        return JsonResponse(response_data)
    
class AppMinConfigView(APIView):
    def post(self, request):
        config = request.data
        n_switch = int(config.get('n_switch'))
        n_router = int(config.get('n_router'))
        n_bridge = int(config.get('n_bridge'))
        n_repeater = int(config.get('n_repeater'))
        n_modern = int(config.get('n_modern'))
        n_gateway = int(config.get('n_gateway'))
        n_firewall = int(config.get('n_firewall'))
        n_low_end_sensor = int(config.get('n_low_end_sensor'))
        n_high_end_sensor = int(config.get('n_high_end_sensor'))
        n_bulb = int(config.get('n_bulb'))
        n_energy_management = int(config.get('n_energy_management'))
        n_lock = int(config.get('n_lock'))
        n_security_alarm = int(config.get('n_security_alarm'))
        n_security_ip_camera = int(config.get('n_security_ip_camera'))
        n_appliance = int(config.get('n_appliance'))
        n_tv = int(config.get('n_tv'))
        n_smartphone = int(config.get('n_smartphone'))
        n_tablet = int(config.get('n_tablet'))
        n_pc = int(config.get('n_pc'))
        n_smartwatch = int(config.get('n_smartwatch'))
        n_security_hub = int(config.get('n_security_hub'))
        n_assistant_hub = int(config.get('n_assistant_hub'))
        n_nas = int(config.get('n_nas'))

        # Obtener todos los dispositivos
        devices = Device.objects.all()

        # Crear modelo de optimización
        model = cp_model.CpModel()

        device_types_dict = {
            'Switch': 'switch',
            'Router': 'router',
            'Bridge': 'bridge',
            'Repeater': 'repeater',
            'Modern': 'modern',
            'Gateway': 'gateway',
            'Firewall': 'firewall',
            'Low-End Sensor': 'low_end_sensor',
            'High-End Sensor': 'high_end_sensor',
            'Smart Bulb': 'bulb',
            'Smart Energy Management Device': 'energy_management',
            'Smart Lock': 'lock',
            'Smart Security Alarm': 'security_alarm',
            'Smart Security IP Camera': 'security_ip_camera',
            'Smart Appliance': 'appliance',
            'Smart TV': 'tv',
            'Smartphone': 'smartphone',
            'Tablet': 'tablet',
            'Personal Computer': 'pc',
            'Smartwatch': 'smartwatch',
            'Smart Security Hub': 'security_hub',
            'Home Assistant Hub': 'assistant_hub',
            'Network Attached Storage (NAS)': 'nas'
        }
        # Inicializar el diccionario de contadores para cada tipo de dispositivo
        type_counters = {type_key: 0 for type_key in device_types_dict.values()}

        # Variables: cada dispositivo es una variable binaria (0 o 1)
        device_vars = {}
        for device in devices:
            device_type = device.type
            type_key = device_types_dict.get(device_type, None)
            if type_key is not None:
                type_counter = type_counters[type_key]
                var_name = f'device_{type_key}_{type_counter}'
                device_var = model.NewBoolVar(var_name)
                device_vars[device] = device_var
                type_counters[type_key] += 1
        

        # Imprimir todas las variables de dispositivos
        for device, device_var in device_vars.items():
            print(f"Dispositivo: {device.model}, Variable: {device_var}")
            
        # Crear un diccionario para almacenar las variables de cada tipo de dispositivo
        device_vars_by_type = {type_key: [] for type_key in device_types_dict.values()}

        # Iterar sobre los dispositivos y agregar las variables a las listas correspondientes
        for device, device_var in device_vars.items():
            device_type = device.type
            type_key = device_types_dict.get(device_type, None)
            if type_key is not None:
                device_vars_by_type[type_key].append(device_var)

        # Agregar restricciones de cantidad
        model.Add(sum(device_vars_by_type['switch']) == n_switch)
        model.Add(sum(device_vars_by_type['router']) == n_router)
        model.Add(sum(device_vars_by_type['bridge']) == n_bridge)
        model.Add(sum(device_vars_by_type['repeater']) == n_repeater)
        model.Add(sum(device_vars_by_type['modern']) == n_modern)
        model.Add(sum(device_vars_by_type['gateway']) == n_gateway)
        model.Add(sum(device_vars_by_type['firewall']) == n_firewall)
        model.Add(sum(device_vars_by_type['low_end_sensor']) == n_low_end_sensor)
        model.Add(sum(device_vars_by_type['high_end_sensor']) == n_high_end_sensor)
        model.Add(sum(device_vars_by_type['bulb']) == n_bulb)
        model.Add(sum(device_vars_by_type['energy_management']) == n_energy_management)
        model.Add(sum(device_vars_by_type['lock']) == n_lock)
        model.Add(sum(device_vars_by_type['security_alarm']) == n_security_alarm)
        model.Add(sum(device_vars_by_type['security_ip_camera']) == n_security_ip_camera)
        model.Add(sum(device_vars_by_type['appliance']) == n_appliance)
        model.Add(sum(device_vars_by_type['tv']) == n_tv)
        model.Add(sum(device_vars_by_type['smartphone']) == n_smartphone)
        model.Add(sum(device_vars_by_type['tablet']) == n_tablet)
        model.Add(sum(device_vars_by_type['pc']) == n_pc)
        model.Add(sum(device_vars_by_type['smartwatch']) == n_smartwatch)
        model.Add(sum(device_vars_by_type['security_hub']) == n_security_hub)
        model.Add(sum(device_vars_by_type['assistant_hub']) == n_assistant_hub)
        model.Add(sum(device_vars_by_type['nas']) == n_nas)

        # Obtener todos las aplicaciones
        apps = App.objects.all()

        # Define un diccionario para almacenar los nombres de las variables asociadas a cada aplicación
        app_vars_dict = {}

        # Itera sobre todas las aplicaciones
        for app in apps:
            # Define el nombre de la variable asociada a esta aplicación
            app_var_id = f'app_{app.id}'
            
            # Crea la variable binaria y asigna el nombre
            app_var = model.NewBoolVar(app_var_id)
            
            # Almacena el nombre de la variable en el diccionario, con el nombre de la aplicación como clave
            app_vars_dict[app.name] = app_var

        print('\n' + str(app_vars_dict) + '\n')
        
        # Define un diccionario para almacenar los nombres de las aplicaciones asociadas a cada dispositivo
        apps_per_device_vars = {}

        # Itera sobre cada dispositivo
        for device in devices:
            # Obtén los nombres de las aplicaciones asociadas a este dispositivo
            app_names = [app_vars_dict[app.name] for app in device.apps.all()]
            apps_per_device_vars[device] = app_names


        for dev in devices:
            dev_apps=apps_per_device_vars[dev]
            # Añadir la restricción: x ↔ (a || b || c || d)
            print(f"Dispositivo: {device_vars[dev]}, Apps: {dev_apps}")
            model.AddBoolOr(dev_apps).OnlyEnforceIf(device_vars[dev])


        # Minimizar el número de aplicaciones
        obj_func=sum(app_vars_dict.values())
        model.Minimize(obj_func)

        # Resolver el modelo y obtener la solución
        solver = cp_model.CpSolver()
        status = solver.Solve(model)

        # Verificar si se encontró una solución
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            # Crear un diccionario para almacenar la solución
            solution = {}

            # Iterar sobre las variables de los dispositivos y obtener sus valores
            for device, device_var in device_vars.items():
                if solver.Value(device_var) == 1:
                    solution[str(device.type)+" -> "+str(device.model)+"-" + str(device.home.identifier)] = solver.Value(device_var)
                    solution[str(device.model)+ "-" + str(device.home.identifier)+' apps'] = list(Device.objects.get(id=device.id).apps.all().values_list('name', flat=True))
            
            print('----------------------')

            for app, app_var in app_vars_dict.items():
                if solver.Value(app_var) == 1:
                    print(app)


            # Devolver la solución como JSON
            return JsonResponse(solution)

        else:
            # Si no se encontró una solución factible, devolver un mensaje de error
            return JsonResponse({"error": "No se encontró una solución factible"})
        

class ConnectivityMaxConfigView(APIView):
    def post(self, request):
        config = request.data
        n_switch = int(config.get('n_switch'))
        n_router = int(config.get('n_router'))
        n_bridge = int(config.get('n_bridge'))
        n_repeater = int(config.get('n_repeater'))
        n_modern = int(config.get('n_modern'))
        n_gateway = int(config.get('n_gateway'))
        n_firewall = int(config.get('n_firewall'))
        n_low_end_sensor = int(config.get('n_low_end_sensor'))
        n_high_end_sensor = int(config.get('n_high_end_sensor'))
        n_bulb = int(config.get('n_bulb'))
        n_energy_management = int(config.get('n_energy_management'))
        n_lock = int(config.get('n_lock'))
        n_security_alarm = int(config.get('n_security_alarm'))
        n_security_ip_camera = int(config.get('n_security_ip_camera'))
        n_appliance = int(config.get('n_appliance'))
        n_tv = int(config.get('n_tv'))
        n_smartphone = int(config.get('n_smartphone'))
        n_tablet = int(config.get('n_tablet'))
        n_pc = int(config.get('n_pc'))
        n_smartwatch = int(config.get('n_smartwatch'))
        n_security_hub = int(config.get('n_security_hub'))
        n_assistant_hub = int(config.get('n_assistant_hub'))
        n_nas = int(config.get('n_nas'))

        # Obtener todos los dispositivos
        devices = Device.objects.all()

        # Crear modelo de optimización
        model = cp_model.CpModel()

        device_types_dict = {
            'Switch': 'switch',
            'Router': 'router',
            'Bridge': 'bridge',
            'Repeater': 'repeater',
            'Modern': 'modern',
            'Gateway': 'gateway',
            'Firewall': 'firewall',
            'Low-End Sensor': 'low_end_sensor',
            'High-End Sensor': 'high_end_sensor',
            'Smart Bulb': 'bulb',
            'Smart Energy Management Device': 'energy_management',
            'Smart Lock': 'lock',
            'Smart Security Alarm': 'security_alarm',
            'Smart Security IP Camera': 'security_ip_camera',
            'Smart Appliance': 'appliance',
            'Smart TV': 'tv',
            'Smartphone': 'smartphone',
            'Tablet': 'tablet',
            'Personal Computer': 'pc',
            'Smartwatch': 'smartwatch',
            'Smart Security Hub': 'security_hub',
            'Home Assistant Hub': 'assistant_hub',
            'Network Attached Storage (NAS)': 'nas'
        }
        # Inicializar el diccionario de contadores para cada tipo de dispositivo
        type_counters = {type_key: 0 for type_key in device_types_dict.values()}

        # Variables: cada dispositivo es una variable binaria (0 o 1)
        device_vars = {}
        for device in devices:
            device_type = device.type
            type_key = device_types_dict.get(device_type, None)
            if type_key is not None:
                type_counter = type_counters[type_key]
                var_name = f'device_{type_key}_{type_counter}'
                device_var = model.NewBoolVar(var_name)
                device_vars[device] = device_var
                type_counters[type_key] += 1
        

        # Imprimir todas las variables de dispositivos
        for device, device_var in device_vars.items():
            print(f"Dispositivo: {device.model}, Variable: {device_var}")
            
        # Crear un diccionario para almacenar las variables de cada tipo de dispositivo
        device_vars_by_type = {type_key: [] for type_key in device_types_dict.values()}

        # Iterar sobre los dispositivos y agregar las variables a las listas correspondientes
        for device, device_var in device_vars.items():
            device_type = device.type
            type_key = device_types_dict.get(device_type, None)
            if type_key is not None:
                device_vars_by_type[type_key].append(device_var)

        # Agregar restricciones de cantidad
        model.Add(sum(device_vars_by_type['switch']) == n_switch)
        model.Add(sum(device_vars_by_type['router']) == n_router)
        model.Add(sum(device_vars_by_type['bridge']) == n_bridge)
        model.Add(sum(device_vars_by_type['repeater']) == n_repeater)
        model.Add(sum(device_vars_by_type['modern']) == n_modern)
        model.Add(sum(device_vars_by_type['gateway']) == n_gateway)
        model.Add(sum(device_vars_by_type['firewall']) == n_firewall)
        model.Add(sum(device_vars_by_type['low_end_sensor']) == n_low_end_sensor)
        model.Add(sum(device_vars_by_type['high_end_sensor']) == n_high_end_sensor)
        model.Add(sum(device_vars_by_type['bulb']) == n_bulb)
        model.Add(sum(device_vars_by_type['energy_management']) == n_energy_management)
        model.Add(sum(device_vars_by_type['lock']) == n_lock)
        model.Add(sum(device_vars_by_type['security_alarm']) == n_security_alarm)
        model.Add(sum(device_vars_by_type['security_ip_camera']) == n_security_ip_camera)
        model.Add(sum(device_vars_by_type['appliance']) == n_appliance)
        model.Add(sum(device_vars_by_type['tv']) == n_tv)
        model.Add(sum(device_vars_by_type['smartphone']) == n_smartphone)
        model.Add(sum(device_vars_by_type['tablet']) == n_tablet)
        model.Add(sum(device_vars_by_type['pc']) == n_pc)
        model.Add(sum(device_vars_by_type['smartwatch']) == n_smartwatch)
        model.Add(sum(device_vars_by_type['security_hub']) == n_security_hub)
        model.Add(sum(device_vars_by_type['assistant_hub']) == n_assistant_hub)
        model.Add(sum(device_vars_by_type['nas']) == n_nas)

        # Obtener el numero de tipos de conectividad asociado a cada dispositivo
        connectivity_per_device = []
        for device in devices:
            connectivity_per_device.append((device, (len(device.connectivities.all()))))
        print('\n' + str(connectivity_per_device) + '\n')


        # -----------------------------------------------------------

        # Extraer los valores de conectividad
        connectivity_values = [connectivity for _, connectivity in connectivity_per_device]
        print('Valores de conectividad:', connectivity_values)

        # Obtener el valor mínimo y máximo de las conectividades
        min_connectivity = min(connectivity_values)
        max_connectivity = max(connectivity_values)

        print('Conectividad mínimo:', min_connectivity)
        print('Conectividad máximo:', max_connectivity)

        # Normalizar los valores de conectividad
        connectivity_per_device_norm = []
        diff_connectivity = max_connectivity - min_connectivity
        for device, connectivity in connectivity_per_device:
            normalized_connectivity = (connectivity - min_connectivity) / diff_connectivity
            rounded_scaled_connectivity = round(normalized_connectivity * 1000)
            connectivity_per_device_norm.append((device, rounded_scaled_connectivity))

        print('Conectividades normalizadas por dispositivo:\n', connectivity_per_device_norm)

        # -----------------------------------------------------------

        # Restricción: la suma total de las conectividades debe ser maxima
        connectivity_vars = []
        for i, device in enumerate(devices):
            connectivity_var = model.NewIntVar(0, sum(n_conn[1] for n_conn in connectivity_per_device_norm), f'n_connectivity_{i}')
            connectivity_vars.append(connectivity_var)
        #print(str(connectivity_vars)+ '\n')

        connectivity_expr = sum(list(device_vars.values())[i] * connectivity_per_device_norm[i][1] for i in range(len(devices)))
        #print(connectivity_expr)
        model.Add(connectivity_expr == (sum(connectivity_vars)))
        obj_func=sum(connectivity_vars)*-1
        model.Minimize(obj_func)

        # Resolver el modelo y obtener la solución
        solver = cp_model.CpSolver()
        status = solver.Solve(model)

        # Verificar si se encontró una solución
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            # Crear un diccionario para almacenar la solución
            solution = {}

            # Iterar sobre las variables de los dispositivos y obtener sus valores
            for device, device_var in device_vars.items():
                if solver.Value(device_var) == 1:
                    solution[str(device.type)+" -> "+str(device.model)+"-" + str(device.home.identifier)] = solver.Value(device_var)
                    solution[str(device.model)+ "-" + str(device.home.identifier)+' connectivities'] = list(Device.objects.get(id=device.id).connectivities.all().values_list('technology', flat=True))
            # Iterar sobre las variables de los dispositivos y obtener sus valores
            #for conn, conn_var in conns_vars.items():
            #    solution[conn.technology] = solver.Value(conn_var)

            # Devolver la solución como JSON
            return JsonResponse(solution)

        else:
            # Si no se encontró una solución factible, devolver un mensaje de error
            return JsonResponse({"error": "No se encontró una solución factible"})
        
class ImpactMinConfigView(APIView):
    def post(self, request):
        config = request.data
        n_switch = int(config.get('n_switch'))
        n_router = int(config.get('n_router'))
        n_bridge = int(config.get('n_bridge'))
        n_repeater = int(config.get('n_repeater'))
        n_modern = int(config.get('n_modern'))
        n_gateway = int(config.get('n_gateway'))
        n_firewall = int(config.get('n_firewall'))
        n_low_end_sensor = int(config.get('n_low_end_sensor'))
        n_high_end_sensor = int(config.get('n_high_end_sensor'))
        n_bulb = int(config.get('n_bulb'))
        n_energy_management = int(config.get('n_energy_management'))
        n_lock = int(config.get('n_lock'))
        n_security_alarm = int(config.get('n_security_alarm'))
        n_security_ip_camera = int(config.get('n_security_ip_camera'))
        n_appliance = int(config.get('n_appliance'))
        n_tv = int(config.get('n_tv'))
        n_smartphone = int(config.get('n_smartphone'))
        n_tablet = int(config.get('n_tablet'))
        n_pc = int(config.get('n_pc'))
        n_smartwatch = int(config.get('n_smartwatch'))
        n_security_hub = int(config.get('n_security_hub'))
        n_assistant_hub = int(config.get('n_assistant_hub'))
        n_nas = int(config.get('n_nas'))

        # Obtener todos los dispositivos
        devices = Device.objects.all()

        # Crear modelo de optimización
        model = cp_model.CpModel()

        device_types_dict = {
            'Switch': 'switch',
            'Router': 'router',
            'Bridge': 'bridge',
            'Repeater': 'repeater',
            'Modern': 'modern',
            'Gateway': 'gateway',
            'Firewall': 'firewall',
            'Low-End Sensor': 'low_end_sensor',
            'High-End Sensor': 'high_end_sensor',
            'Smart Bulb': 'bulb',
            'Smart Energy Management Device': 'energy_management',
            'Smart Lock': 'lock',
            'Smart Security Alarm': 'security_alarm',
            'Smart Security IP Camera': 'security_ip_camera',
            'Smart Appliance': 'appliance',
            'Smart TV': 'tv',
            'Smartphone': 'smartphone',
            'Tablet': 'tablet',
            'Personal Computer': 'pc',
            'Smartwatch': 'smartwatch',
            'Smart Security Hub': 'security_hub',
            'Home Assistant Hub': 'assistant_hub',
            'Network Attached Storage (NAS)': 'nas'
        }
        # Inicializar el diccionario de contadores para cada tipo de dispositivo
        type_counters = {type_key: 0 for type_key in device_types_dict.values()}

        # Variables: cada dispositivo es una variable binaria (0 o 1)
        device_vars = {}
        for device in devices:
            device_type = device.type
            type_key = device_types_dict.get(device_type, None)
            if type_key is not None:
                type_counter = type_counters[type_key]
                var_name = f'device_{type_key}_{type_counter}'
                device_var = model.NewBoolVar(var_name)
                device_vars[device] = device_var
                type_counters[type_key] += 1
        

        # Imprimir todas las variables de dispositivos
        for device, device_var in device_vars.items():
            print(f"Dispositivo: {device.model}, Variable: {device_var}")
            
        # Crear un diccionario para almacenar las variables de cada tipo de dispositivo
        device_vars_by_type = {type_key: [] for type_key in device_types_dict.values()}

        # Iterar sobre los dispositivos y agregar las variables a las listas correspondientes
        for device, device_var in device_vars.items():
            device_type = device.type
            type_key = device_types_dict.get(device_type, None)
            if type_key is not None:
                device_vars_by_type[type_key].append(device_var)

        # Agregar restricciones de cantidad
        model.Add(sum(device_vars_by_type['switch']) == n_switch)
        model.Add(sum(device_vars_by_type['router']) == n_router)
        model.Add(sum(device_vars_by_type['bridge']) == n_bridge)
        model.Add(sum(device_vars_by_type['repeater']) == n_repeater)
        model.Add(sum(device_vars_by_type['modern']) == n_modern)
        model.Add(sum(device_vars_by_type['gateway']) == n_gateway)
        model.Add(sum(device_vars_by_type['firewall']) == n_firewall)
        model.Add(sum(device_vars_by_type['low_end_sensor']) == n_low_end_sensor)
        model.Add(sum(device_vars_by_type['high_end_sensor']) == n_high_end_sensor)
        model.Add(sum(device_vars_by_type['bulb']) == n_bulb)
        model.Add(sum(device_vars_by_type['energy_management']) == n_energy_management)
        model.Add(sum(device_vars_by_type['lock']) == n_lock)
        model.Add(sum(device_vars_by_type['security_alarm']) == n_security_alarm)
        model.Add(sum(device_vars_by_type['security_ip_camera']) == n_security_ip_camera)
        model.Add(sum(device_vars_by_type['appliance']) == n_appliance)
        model.Add(sum(device_vars_by_type['tv']) == n_tv)
        model.Add(sum(device_vars_by_type['smartphone']) == n_smartphone)
        model.Add(sum(device_vars_by_type['tablet']) == n_tablet)
        model.Add(sum(device_vars_by_type['pc']) == n_pc)
        model.Add(sum(device_vars_by_type['smartwatch']) == n_smartwatch)
        model.Add(sum(device_vars_by_type['security_hub']) == n_security_hub)
        model.Add(sum(device_vars_by_type['assistant_hub']) == n_assistant_hub)
        model.Add(sum(device_vars_by_type['nas']) == n_nas)

        # Obtener el impacto asociado a cada dispositivo
        impact_per_device = []
        for device in devices:
            impact_per_device.append((device, int(round(device.impact))))
        print('\n' + str(impact_per_device) + '\n')


        # -----------------------------------------------------------

        # Extraer los valores de impacto
        impact_values = [impact for _, impact in impact_per_device]
        print('Valores de impacto:', impact_values)

        # Obtener el valor mínimo y máximo de los impactos
        min_impact = min(impact_values)
        max_impact = max(impact_values)

        print('Impacto mínimo:', min_impact)
        print('Impacto máximo:', max_impact)

        # Normalizar los valores de impacto
        impact_per_device_norm = []
        diff_impact = max_impact - min_impact
        for device, impact in impact_per_device:
            normalized_impact = (impact - min_impact) / diff_impact
            rounded_scaled_impact = round(normalized_impact * 1000)
            impact_per_device_norm.append((device, rounded_scaled_impact))

        print('Impactos normalizados por dispositivo:\n', impact_per_device_norm)

        # -----------------------------------------------------------

        # Restricción: la suma total de los impactos debe ser mínima
        impact_scores = []
        for i, device in enumerate(devices):
            impact_var = model.NewIntVar(0, sum(score[1] for score in impact_per_device_norm), f'impact_{i}')
            impact_scores.append(impact_var)
        #print(str(impact_scores)+ '\n')

        impact_score_expr = sum(list(device_vars.values())[i] * impact_per_device_norm[i][1] for i in range(len(devices)))
        #print(impact_score_expr)
        model.Add(impact_score_expr == sum(impact_scores))
        #print(str(sum(impact_scores)))
        obj_func=sum(impact_scores)
        model.Minimize(obj_func)

       # Resolver el modelo y obtener la solución
        solver = cp_model.CpSolver()
        status = solver.Solve(model)

        # Verificar si se encontró una solución
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            # Crear un diccionario para almacenar la solución
            solution = {}

            # Iterar sobre las variables de los dispositivos y obtener sus valores
            for device, device_var in device_vars.items():
                if solver.Value(device_var) == 1:
                    solution[str(device.type)+" -> "+str(device.model)+"-" + str(device.home.identifier)] = solver.Value(device_var)
                    solution[str(device.model)+ "-" + str(device.home.identifier)+' impact'] = [int(round(device.impact))]

            # Devolver la solución como JSON
            return JsonResponse(solution)

        else:
            # Si no se encontró una solución factible, devolver un mensaje de error
            return JsonResponse({"error": "No se encontró una solución factible"})
        
class CWEMinConfigView(APIView):
    def post(self, request):
        config = request.data
        n_switch = int(config.get('n_switch'))
        n_router = int(config.get('n_router'))
        n_bridge = int(config.get('n_bridge'))
        n_repeater = int(config.get('n_repeater'))
        n_modern = int(config.get('n_modern'))
        n_gateway = int(config.get('n_gateway'))
        n_firewall = int(config.get('n_firewall'))
        n_low_end_sensor = int(config.get('n_low_end_sensor'))
        n_high_end_sensor = int(config.get('n_high_end_sensor'))
        n_bulb = int(config.get('n_bulb'))
        n_energy_management = int(config.get('n_energy_management'))
        n_lock = int(config.get('n_lock'))
        n_security_alarm = int(config.get('n_security_alarm'))
        n_security_ip_camera = int(config.get('n_security_ip_camera'))
        n_appliance = int(config.get('n_appliance'))
        n_tv = int(config.get('n_tv'))
        n_smartphone = int(config.get('n_smartphone'))
        n_tablet = int(config.get('n_tablet'))
        n_pc = int(config.get('n_pc'))
        n_smartwatch = int(config.get('n_smartwatch'))
        n_security_hub = int(config.get('n_security_hub'))
        n_assistant_hub = int(config.get('n_assistant_hub'))
        n_nas = int(config.get('n_nas'))

        # Obtener todos los dispositivos
        devices = Device.objects.all()

        # Crear modelo de optimización
        model = cp_model.CpModel()

        device_types_dict = {
            'Switch': 'switch',
            'Router': 'router',
            'Bridge': 'bridge',
            'Repeater': 'repeater',
            'Modern': 'modern',
            'Gateway': 'gateway',
            'Firewall': 'firewall',
            'Low-End Sensor': 'low_end_sensor',
            'High-End Sensor': 'high_end_sensor',
            'Smart Bulb': 'bulb',
            'Smart Energy Management Device': 'energy_management',
            'Smart Lock': 'lock',
            'Smart Security Alarm': 'security_alarm',
            'Smart Security IP Camera': 'security_ip_camera',
            'Smart Appliance': 'appliance',
            'Smart TV': 'tv',
            'Smartphone': 'smartphone',
            'Tablet': 'tablet',
            'Personal Computer': 'pc',
            'Smartwatch': 'smartwatch',
            'Smart Security Hub': 'security_hub',
            'Home Assistant Hub': 'assistant_hub',
            'Network Attached Storage (NAS)': 'nas'
        }
        # Inicializar el diccionario de contadores para cada tipo de dispositivo
        type_counters = {type_key: 0 for type_key in device_types_dict.values()}

        # Variables: cada dispositivo es una variable binaria (0 o 1)
        device_vars = {}
        for device in devices:
            device_type = device.type
            type_key = device_types_dict.get(device_type, None)
            if type_key is not None:
                type_counter = type_counters[type_key]
                var_name = f'device_{type_key}_{type_counter}'
                device_var = model.NewBoolVar(var_name)
                device_vars[device] = device_var
                type_counters[type_key] += 1
        

        # Imprimir todas las variables de dispositivos
        for device, device_var in device_vars.items():
            print(f"Dispositivo: {device.model}, Variable: {device_var}")
            
        # Crear un diccionario para almacenar las variables de cada tipo de dispositivo
        device_vars_by_type = {type_key: [] for type_key in device_types_dict.values()}

        # Iterar sobre los dispositivos y agregar las variables a las listas correspondientes
        for device, device_var in device_vars.items():
            device_type = device.type
            type_key = device_types_dict.get(device_type, None)
            if type_key is not None:
                device_vars_by_type[type_key].append(device_var)

        # Agregar restricciones de cantidad
        model.Add(sum(device_vars_by_type['switch']) == n_switch)
        model.Add(sum(device_vars_by_type['router']) == n_router)
        model.Add(sum(device_vars_by_type['bridge']) == n_bridge)
        model.Add(sum(device_vars_by_type['repeater']) == n_repeater)
        model.Add(sum(device_vars_by_type['modern']) == n_modern)
        model.Add(sum(device_vars_by_type['gateway']) == n_gateway)
        model.Add(sum(device_vars_by_type['firewall']) == n_firewall)
        model.Add(sum(device_vars_by_type['low_end_sensor']) == n_low_end_sensor)
        model.Add(sum(device_vars_by_type['high_end_sensor']) == n_high_end_sensor)
        model.Add(sum(device_vars_by_type['bulb']) == n_bulb)
        model.Add(sum(device_vars_by_type['energy_management']) == n_energy_management)
        model.Add(sum(device_vars_by_type['lock']) == n_lock)
        model.Add(sum(device_vars_by_type['security_alarm']) == n_security_alarm)
        model.Add(sum(device_vars_by_type['security_ip_camera']) == n_security_ip_camera)
        model.Add(sum(device_vars_by_type['appliance']) == n_appliance)
        model.Add(sum(device_vars_by_type['tv']) == n_tv)
        model.Add(sum(device_vars_by_type['smartphone']) == n_smartphone)
        model.Add(sum(device_vars_by_type['tablet']) == n_tablet)
        model.Add(sum(device_vars_by_type['pc']) == n_pc)
        model.Add(sum(device_vars_by_type['smartwatch']) == n_smartwatch)
        model.Add(sum(device_vars_by_type['security_hub']) == n_security_hub)
        model.Add(sum(device_vars_by_type['assistant_hub']) == n_assistant_hub)
        model.Add(sum(device_vars_by_type['nas']) == n_nas)

        # Obtener todos los cwe
        cwes = CWE.objects.all()

        # Define un diccionario para almacenar los nombres de las variables asociadas a cada cwe
        cwe_vars_dict = {}

        # Itera sobre todas los cwe
        for cwe in cwes:
            if bool(re.search(r'\d', cwe.identifier)):
                # Define el nombre de la variable asociada al cwe
                cwe_var_id = f'cwe_{str(cwe.identifier).split("-")[1]}'
                
                # Crea la variable binaria y asigna el nombre
                cwe_var = model.NewBoolVar(cwe_var_id)
                
                # Almacena el nombre de la variable en el diccionario, con el nombre del cwe como clave
                cwe_vars_dict[cwe.identifier] = cwe_var

        print('\n' + str(cwe_vars_dict) + '\n')
        
        # Define un diccionario para almacenar las variables que representan los identificadores de los cwes asociados a un dispositivo
        cwes_per_device_vars = {}
        cwes_per_device = {}
        # Obtiene todas las vulnerabilidades
        vulns = Vulnerability.objects.all()

        # Obtiene todos los cwes asociados a un dispositivo
        for device in devices:
            # Obtén los cwes asociados a este dispositivo
            cwes_ids_var = set()
            cwes_ids = set()
            device_vulns = vulns.filter(device=device)
            for dev_vuln in device_vulns:
                cwes = dev_vuln.cwes.all()
                cwes_id = [cwe.identifier for cwe in cwes]
                for id in cwes_id:
                    if bool(re.search(r'\d', id)):
                        cwes_ids_var.add(cwe_vars_dict[id])
                        cwes_ids.add(id)
            cwes_per_device_vars[device] = cwes_ids_var
            cwes_per_device[device] = cwes_ids
        print(cwes_per_device_vars)
        print(cwes_per_device)


        for dev in devices:
            dev_cwes_v=cwes_per_device_vars[dev]
            # Añadir la restricción: x ↔ (a ∨ b ∨ c ∨ d)
            print(f"Dispositivo: {device_vars[dev]}, Cwes: {dev_cwes_v}")
            model.AddBoolAnd(dev_cwes_v).OnlyEnforceIf(device_vars[dev])

        # Minimizar el número de aplicaciones
        obj_func=sum(cwe_vars_dict.values())
        model.Minimize(obj_func)

        # Resolver el modelo y obtener la solución
        solver = cp_model.CpSolver()
        status = solver.Solve(model)

        # Verificar si se encontró una solución
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            # Crear un diccionario para almacenar la solución
            solution = {}

            # Iterar sobre las variables de los dispositivos y obtener sus valores
            for device, device_var in device_vars.items():
                if solver.Value(device_var) == 1:
                    solution[str(device.type)+" -> "+str(device.model)+"-" + str(device.home.identifier)] = solver.Value(device_var)
                    solution[str(device.model)+ "-" + str(device.home.identifier)+' cwes'] = list(cwes_per_device[device])

            # Devolver la solución como JSON
            return JsonResponse(solution)

        else:
            # Si no se encontró una solución factible, devolver un mensaje de error
            return JsonResponse({"error": "No se encontró una solución factible"})



class SustainabilityMaxConfigView(APIView):
    def post(self, request):
        config = request.data
        n_switch = int(config.get('n_switch'))
        n_router = int(config.get('n_router'))
        n_bridge = int(config.get('n_bridge'))
        n_repeater = int(config.get('n_repeater'))
        n_modern = int(config.get('n_modern'))
        n_gateway = int(config.get('n_gateway'))
        n_firewall = int(config.get('n_firewall'))
        n_low_end_sensor = int(config.get('n_low_end_sensor'))
        n_high_end_sensor = int(config.get('n_high_end_sensor'))
        n_bulb = int(config.get('n_bulb'))
        n_energy_management = int(config.get('n_energy_management'))
        n_lock = int(config.get('n_lock'))
        n_security_alarm = int(config.get('n_security_alarm'))
        n_security_ip_camera = int(config.get('n_security_ip_camera'))
        n_appliance = int(config.get('n_appliance'))
        n_tv = int(config.get('n_tv'))
        n_smartphone = int(config.get('n_smartphone'))
        n_tablet = int(config.get('n_tablet'))
        n_pc = int(config.get('n_pc'))
        n_smartwatch = int(config.get('n_smartwatch'))
        n_security_hub = int(config.get('n_security_hub'))
        n_assistant_hub = int(config.get('n_assistant_hub'))
        n_nas = int(config.get('n_nas'))

        # Obtener todos los dispositivos
        devices = Device.objects.all()

        # Crear modelo de optimización
        model = cp_model.CpModel()

        device_types_dict = {
            'Switch': 'switch',
            'Router': 'router',
            'Bridge': 'bridge',
            'Repeater': 'repeater',
            'Modern': 'modern',
            'Gateway': 'gateway',
            'Firewall': 'firewall',
            'Low-End Sensor': 'low_end_sensor',
            'High-End Sensor': 'high_end_sensor',
            'Smart Bulb': 'bulb',
            'Smart Energy Management Device': 'energy_management',
            'Smart Lock': 'lock',
            'Smart Security Alarm': 'security_alarm',
            'Smart Security IP Camera': 'security_ip_camera',
            'Smart Appliance': 'appliance',
            'Smart TV': 'tv',
            'Smartphone': 'smartphone',
            'Tablet': 'tablet',
            'Personal Computer': 'pc',
            'Smartwatch': 'smartwatch',
            'Smart Security Hub': 'security_hub',
            'Home Assistant Hub': 'assistant_hub',
            'Network Attached Storage (NAS)': 'nas'
        }
        # Inicializar el diccionario de contadores para cada tipo de dispositivo
        type_counters = {type_key: 0 for type_key in device_types_dict.values()}

        # Variables: cada dispositivo es una variable binaria (0 o 1)
        device_vars = {}
        for device in devices:
            device_type = device.type
            type_key = device_types_dict.get(device_type, None)
            if type_key is not None:
                type_counter = type_counters[type_key]
                var_name = f'device_{type_key}_{type_counter}'
                device_var = model.NewBoolVar(var_name)
                device_vars[device] = device_var
                type_counters[type_key] += 1
        

        # Imprimir todas las variables de dispositivos
        for device, device_var in device_vars.items():
            print(f"Dispositivo: {device.model}, Variable: {device_var}")
            
        # Crear un diccionario para almacenar las variables de cada tipo de dispositivo
        device_vars_by_type = {type_key: [] for type_key in device_types_dict.values()}

        # Iterar sobre los dispositivos y agregar las variables a las listas correspondientes
        for device, device_var in device_vars.items():
            device_type = device.type
            type_key = device_types_dict.get(device_type, None)
            if type_key is not None:
                device_vars_by_type[type_key].append(device_var)

        # Agregar restricciones de cantidad
        model.Add(sum(device_vars_by_type['switch']) == n_switch)
        model.Add(sum(device_vars_by_type['router']) == n_router)
        model.Add(sum(device_vars_by_type['bridge']) == n_bridge)
        model.Add(sum(device_vars_by_type['repeater']) == n_repeater)
        model.Add(sum(device_vars_by_type['modern']) == n_modern)
        model.Add(sum(device_vars_by_type['gateway']) == n_gateway)
        model.Add(sum(device_vars_by_type['firewall']) == n_firewall)
        model.Add(sum(device_vars_by_type['low_end_sensor']) == n_low_end_sensor)
        model.Add(sum(device_vars_by_type['high_end_sensor']) == n_high_end_sensor)
        model.Add(sum(device_vars_by_type['bulb']) == n_bulb)
        model.Add(sum(device_vars_by_type['energy_management']) == n_energy_management)
        model.Add(sum(device_vars_by_type['lock']) == n_lock)
        model.Add(sum(device_vars_by_type['security_alarm']) == n_security_alarm)
        model.Add(sum(device_vars_by_type['security_ip_camera']) == n_security_ip_camera)
        model.Add(sum(device_vars_by_type['appliance']) == n_appliance)
        model.Add(sum(device_vars_by_type['tv']) == n_tv)
        model.Add(sum(device_vars_by_type['smartphone']) == n_smartphone)
        model.Add(sum(device_vars_by_type['tablet']) == n_tablet)
        model.Add(sum(device_vars_by_type['pc']) == n_pc)
        model.Add(sum(device_vars_by_type['smartwatch']) == n_smartwatch)
        model.Add(sum(device_vars_by_type['security_hub']) == n_security_hub)
        model.Add(sum(device_vars_by_type['assistant_hub']) == n_assistant_hub)
        model.Add(sum(device_vars_by_type['nas']) == n_nas)

        # Obtener la sostenibilidad asociada a cada dispositivo
        sustainability_per_device = []
        for device in devices:
            sustainability_per_device.append((device, int(round(device.sustainability))))
        print('\n' + str(sustainability_per_device) + '\n')


        # -----------------------------------------------------------

        # Extraer los valores de sostenibilidad
        sustainability_values = [sustainability for _, sustainability in sustainability_per_device]
        print('Valores de sostenibilidad:', sustainability_values)

        # Obtener el valor mínimo y máximo de las sostenibilidades
        min_sustainability = min(sustainability_values)
        max_sustainability = max(sustainability_values)

        print('Sostenibilidad mínima:', min_sustainability)
        print('Sostenibilidad máxima:', max_sustainability)

        # Normalizar los valores de sostenibilidad y aplicar redondeo y escalado
        sustainability_per_device_norm = []
        diff_sustainability = max_sustainability - min_sustainability
        for device, sustainability in sustainability_per_device:
            normalized_sustainability = (sustainability - min_sustainability) / diff_sustainability
            scaled_sustainability = round(normalized_sustainability * 1000)
            sustainability_per_device_norm.append((device, scaled_sustainability))

        print('Sostenibilidades normalizadas y escaladas por dispositivo:\n', sustainability_per_device_norm)

        # -----------------------------------------------------------

        # Restricción: la suma total de las sostenibilidades debe ser máxima
        sustainability_scores = []
        for i, device in enumerate(devices):
            sus_var = model.NewIntVar(0, sum(score[1] for score in sustainability_per_device_norm), f'sustainability_{i}')
            sustainability_scores.append(sus_var)
        #print(str(sustainability_scores)+ '\n')

        sus_score_expr = sum(list(device_vars.values())[i] * sustainability_per_device_norm[i][1] for i in range(len(devices)))
        #print(sus_score_expr)
        model.Add(sus_score_expr == sum(sustainability_scores))
        #print(str(sum(sustainability_scores)))
        obj_func=sum(sustainability_scores)*-1
        model.Minimize(obj_func)

       # Resolver el modelo y obtener la solución
        solver = cp_model.CpSolver()
        status = solver.Solve(model)

        # Verificar si se encontró una solución
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            # Crear un diccionario para almacenar la solución
            solution = {}

            # Iterar sobre las variables de los dispositivos y obtener sus valores
            for device, device_var in device_vars.items():
                if solver.Value(device_var) == 1:
                    solution[str(device.type)+" -> "+str(device.model)+"-" + str(device.home.identifier)] = solver.Value(device_var)
                    solution[str(device.model)+ "-" + str(device.home.identifier)+' sustainability'] = [int(round(device.sustainability))]

            # Devolver la solución como JSON
            return JsonResponse(solution)

        else:
            # Si no se encontró una solución factible, devolver un mensaje de error
            return JsonResponse({"error": "No se encontró una solución factible"})


class ConfigView(APIView):
    def post(self, request):
        
        config = request.data

        value_mapping = {
            'NONE': 0,
            'LOW': 0.25,
            'MEDIUM': 0.50,
            'HIGH': 0.75,
            'VERYHIGH': 1
        }
        device_types_dict = {
            'Switch': 'switch',
            'Router': 'router',
            'Bridge': 'bridge',
            'Repeater': 'repeater',
            'Modern': 'modern',
            'Gateway': 'gateway',
            'Firewall': 'firewall',
            'Low-End Sensor': 'low_end_sensor',
            'High-End Sensor': 'high_end_sensor',
            'Smart Bulb': 'bulb',
            'Smart Energy Management Device': 'energy_management',
            'Smart Lock': 'lock',
            'Smart Security Alarm': 'security_alarm',
            'Smart Security IP Camera': 'security_ip_camera',
            'Smart Appliance': 'appliance',
            'Smart TV': 'tv',
            'Smartphone': 'smartphone',
            'Tablet': 'tablet',
            'Personal Computer': 'pc',
            'Smartwatch': 'smartwatch',
            'Smart Security Hub': 'security_hub',
            'Home Assistant Hub': 'assistant_hub',
            'Network Attached Storage (NAS)': 'nas'
        }

        device_counts = {key: int(config.get('newConfigDevices', {}).get(key, 0)) for key in device_types_dict.values()}
        available_devices = config.get('availableDevices', {})
        available_devices_dict = {key: available_devices.get(key, []) for key in device_types_dict.values()}
        devices = Device.objects.all()
        model_to_device = {device.model: device for device in devices}
        for device_type, models in available_devices_dict.items():
            available_devices_dict[device_type] = [model_to_device[model] for model in models if model in model_to_device]
        available_devices_list = []
        for key in available_devices_dict:
            available_devices_list.extend(available_devices_dict[key])
        total_device_sum = sum(device_counts.values())
        attributes = ['security', 'usability', 'connectivity', 'sustainability']
        values = [value_mapping.get(config.get('properties', {}).get(attr, 'NONE')) for attr in attributes]
        total = sum(values)
        values = [value / total for value in values] if total > 0 else [0.25] * len(values)
        user_security_v, user_usability_v, user_connectivity_v, user_sustainability_v = values
        print("##########################################################################")
        print(f"Security: {user_security_v}, Usability: {user_usability_v}, Connectivity: {user_connectivity_v}, Sustainability: {user_sustainability_v}")
        print("##########################################################################")
        model = cp_model.CpModel()
        type_counters = {type_key: 0 for type_key in device_types_dict.values()}
        device_vars = {}
        for device in devices:
            type_key = device_types_dict.get(device.type)
            if type_key:
                var_name = f'device_{type_key}_{type_counters[type_key]}'
                device_var = model.NewBoolVar(var_name)
                device_vars[device] = device_var
                type_counters[type_key] += 1
        device_vars_by_type = {type_key: [] for type_key in device_types_dict.values()}
        for device, device_var in device_vars.items():
            type_key = device_types_dict.get(device.type)
            if type_key:
                device_vars_by_type[type_key].append(device_var)
        for key, count in device_counts.items():
            model.Add(sum(device_vars_by_type[key]) == count)
        available_devices_vars = []
        for av_dev in available_devices_list:
                available_devices_vars.append(device_vars[av_dev])
        for av_dev_var in available_devices_vars:
             model.Add(av_dev_var == 1)

       # -------------------------------------------- IMPACT ----------------------------------------------

        impact_per_device = []
        for device in devices:
            impact_per_device.append((device, int(round(device.impact))))
        impact_values = [impact for _, impact in impact_per_device]
        min_impact = min(impact_values)
        max_impact = max(impact_values)
        impact_per_device_norm = []
        diff_impact = max_impact - min_impact
        for device, impact in impact_per_device:
            normalized_impact = (impact - min_impact) / diff_impact
            rounded_scaled_impact = round(normalized_impact * 1000)
            impact_per_device_norm.append((device, rounded_scaled_impact))
        impact_scores = []
        for i, device in enumerate(devices): 
            impact_var = model.NewIntVar(0, sum(score[1] for score in impact_per_device_norm), f'impact_{i}')  ######### VARS
            impact_scores.append(impact_var)
        impact_score_expr = sum(list(device_vars.values())[i] * impact_per_device_norm[i][1] for i in range(len(devices)))
        model.Add(impact_score_expr == sum(impact_scores))
        obj_func_imp=sum(impact_scores)

        # ------------------------------------------ CONNECTIVITY -------------------------------------------

        connectivity_per_device = []
        for device in devices:
            connectivity_per_device.append((device, (len(device.connectivities.all()))))
        connectivity_values = [connectivity for _, connectivity in connectivity_per_device]
        min_connectivity = min(connectivity_values)
        max_connectivity = max(connectivity_values)
        connectivity_per_device_norm = []
        diff_connectivity = max_connectivity - min_connectivity
        for device, connectivity in connectivity_per_device:
            normalized_connectivity = (connectivity - min_connectivity) / diff_connectivity
            rounded_scaled_connectivity = round(normalized_connectivity * 1000)
            connectivity_per_device_norm.append((device, rounded_scaled_connectivity))
        connectivity_vars = []
        for i, device in enumerate(devices):
            connectivity_var = model.NewIntVar(0, sum(n_conn[1] for n_conn in connectivity_per_device_norm), f'n_connectivity_{i}')    ######### VARS
            connectivity_vars.append(connectivity_var)
        connectivity_expr = sum(list(device_vars.values())[i] * connectivity_per_device_norm[i][1] for i in range(len(devices)))
        model.Add(connectivity_expr == (sum(connectivity_vars)))
        obj_func_conn=sum(connectivity_vars)*-1  

        # ----------------------------------------- SUSTAINABILITY ------------------------------------------

        sustainability_per_device = []
        for device in devices:
            sustainability_per_device.append((device, int(round(device.sustainability))))
        sustainability_values = [sustainability for _, sustainability in sustainability_per_device]
        #print('Valores de sostenibilidad:', sustainability_values)
        min_sustainability = min(sustainability_values)
        max_sustainability = max(sustainability_values)
        #print('Sostenibilidad mínima:', min_sustainability)
        #print('Sostenibilidad máxima:', max_sustainability)
        sustainability_per_device_norm = []
        diff_sustainability = max_sustainability - min_sustainability
        for device, sustainability in sustainability_per_device:
            normalized_sustainability = (sustainability - min_sustainability) / diff_sustainability
            scaled_sustainability = round(normalized_sustainability * 1000)
            sustainability_per_device_norm.append((device, scaled_sustainability))
        #print('Sostenibilidades normalizadas y escaladas por dispositivo:\n', sustainability_per_device_norm)
        sustainability_scores = []
        for i, device in enumerate(devices):
            sus_var = model.NewIntVar(0, sum(score[1] for score in sustainability_per_device_norm), f'sustainability_{i}')
            sustainability_scores.append(sus_var)
        sus_score_expr = sum(list(device_vars.values())[i] * sustainability_per_device_norm[i][1] for i in range(len(devices)))
        model.Add(sus_score_expr == sum(sustainability_scores))
        obj_func_sus=sum(sustainability_scores)*-1

        # ---------------------------------------------- APP ------------------------------------------------

        apps = App.objects.all()
        app_vars_dict = {}
        for app in apps:
            app_var_id = f'app_{app.id}'           
            app_var = model.NewBoolVar(app_var_id)
            app_vars_dict[app.name] = app_var        
        apps_per_device_vars = {}
        for device in devices:
            app_names = [app_vars_dict[app.name] for app in device.apps.all()]
            apps_per_device_vars[device] = app_names
        for dev in devices:
            dev_apps=apps_per_device_vars[dev]
            if dev_apps:
                model.AddBoolOr(dev_apps).OnlyEnforceIf(device_vars[dev])      ######### VARS
        norm_app = (1/total_device_sum)  #   x' = (x - xmin)/(xmax-xmin) ->    x' = (x - 0)/(n-0) ->    x' = (1/n)*x
        factor_app = 1000
        obj_func_app=norm_app * factor_app * sum(app_vars_dict.values())

        # ---------------------------------------------- CWE ------------------------------------------------

        cwes = CWE.objects.all()
        cwe_vars_dict = {}
        for cwe in cwes:
            if bool(re.search(r'\d', cwe.identifier)):
                cwe_var_id = f'cwe_{str(cwe.identifier).split("-")[1]}'
                cwe_var = model.NewBoolVar(cwe_var_id)
                cwe_vars_dict[cwe.identifier] = cwe_var        
        cwes_per_device_vars = {}
        cwes_per_device = {}
        vulns = Vulnerability.objects.all()
        for device in devices:
            cwes_ids_var = set()
            cwes_ids = set()
            device_vulns = vulns.filter(device=device)
            for dev_vuln in device_vulns:
                cwes = dev_vuln.cwes.all()
                cwes_id = [cwe.identifier for cwe in cwes]
                for id in cwes_id:
                    if bool(re.search(r'\d', id)):
                        cwes_ids_var.add(cwe_vars_dict[id])
                        cwes_ids.add(id)
            cwes_per_device_vars[device] = cwes_ids_var
            cwes_per_device[device] = cwes_ids
        for dev in devices:
            dev_cwes_v=cwes_per_device_vars[dev] 
            if dev_cwes_v:
                model.AddBoolAnd(dev_cwes_v).OnlyEnforceIf(device_vars[dev])    ######### VARS
        norm_cwe = (1/938)  #   x' = (x - xmin)/(xmax-xmin) ->    x' = (x - 0)/(938-0) ->    x' = (1/938)*x
        factor_cwe = 1000
        obj_func_cwe=norm_cwe * factor_cwe * sum(cwe_vars_dict.values())

        # --------------------------------------------------------------------------------------------
        # --------------------------------------------------------------------------------------------

        total_obj = (user_security_v * 0.5 * obj_func_imp +
                     user_security_v * 0.5 * obj_func_cwe +
                     user_connectivity_v * obj_func_conn +
                     user_sustainability_v * obj_func_sus + 
                     user_usability_v * obj_func_app)
        
        print(total_obj)

        model.Minimize(total_obj)       
        solver = cp_model.CpSolver()
        status = solver.Solve(model)

        # --------------------------------------------------------------------------------------------

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:

            vars_to_app_dict = {v: k for k, v in app_vars_dict.items()}
            vars_to_cwe_dict = {v: k for k, v in cwe_vars_dict.items()}
            total_impact = []
            total_sustainability = []
            total_connectivity = set()
            total_app = []
            total_cwe = []
            for device, device_var in device_vars.items():
                if solver.Value(device_var) == 1:
                    total_impact.append(device.impact)
                    total_sustainability.append(device.sustainability)
                    connectivities = list(device.connectivities.all().values_list('technology', flat=True))
                    for con in connectivities:
                        total_connectivity.add(con)

            for app_var in app_vars_dict.values():
                if solver.Value(app_var) == 1:
                    total_app.append(vars_to_app_dict[app_var])

            for cwe_var in cwe_vars_dict.values():
                if solver.Value(cwe_var) == 1:
                    total_cwe.append(vars_to_cwe_dict[cwe_var])

            properties = {}
            if user_security_v != 0:
                properties["security"] = {
                    "average_impact": sum(total_impact) / len(total_impact),
                    "cwe_set": total_cwe
                }
            if user_usability_v != 0:
                properties["usability"] = total_app
            if user_connectivity_v != 0:
                properties["connectivity"] = list(total_connectivity)
            if user_sustainability_v != 0:
                properties["average_sustainability"] = sum(total_sustainability) / len(total_sustainability)

            solution = {
                "properties": properties,
                "devices": []
            }
            
            for device, device_var in device_vars.items():
                if solver.Value(device_var) == 1:
                    connectivities = list(device.connectivities.all().values_list('technology', flat=True))
                    
                    device_info = {
                        "model": device.model,
                        "type": device.type,
                        "security": {
                            "impact": device.impact,
                            "cwe_set": list(cwes_per_device[device])
                        },
                        "usability": list(
                            Device.objects.get(id=device.id).apps.all().values_list('name', flat=True)
                        ),
                        "connectivity": connectivities,
                        "sustainability": device.sustainability,

                    }
                    solution["devices"].append(device_info)

            return JsonResponse(solution)
        else:
            return JsonResponse({"error": "No se encontró una solución factible"})