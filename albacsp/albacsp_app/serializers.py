from rest_framework import serializers
from .models import Home,Device,Vulnerability,Connection,ConnectionVulnerability,App,Connectivity,CWE,Power

class AppSerializer(serializers.ModelSerializer):
    class Meta:
        model = App
        fields = '__all__'

class ConnectivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Connectivity
        fields = '__all__'

class PowerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Power
        fields = '__all__'

class CWESerializer(serializers.ModelSerializer):
    class Meta:
        model = CWE
        fields = '__all__'

class VulnerabilitySerializer(serializers.ModelSerializer):
    cwes = CWESerializer(many=True, required=False)
    class Meta:
        model = Vulnerability
        fields = '__all__'

class DeviceSerializer(serializers.ModelSerializer):
    vulnerabilities = VulnerabilitySerializer(many=True, required=False)
    apps = AppSerializer(many=True, required=False)
    power_supplies = PowerSerializer(many=True, required=False)
    connectivities = ConnectivitySerializer(many=True, required=False)
    class Meta:
        model = Device
        fields = '__all__'

class HomeSerializer(serializers.ModelSerializer):
    devices = DeviceSerializer(many=True, required=False)
    class Meta:
        model = Home
        fields = '__all__'

class ConnectionVulnerabilitySerializer(serializers.ModelSerializer):
    cwes = CWESerializer(many=True, required=False)
    class Meta:
        model = ConnectionVulnerability
        fields = '__all__'

class ConnectionSerializer(serializers.ModelSerializer):
    connectionvulnerabilities = ConnectionVulnerabilitySerializer(many=True, required=False)
    first_device = DeviceSerializer()
    second_device = DeviceSerializer()
    class Meta:
        model = Connection
        fields = '__all__'