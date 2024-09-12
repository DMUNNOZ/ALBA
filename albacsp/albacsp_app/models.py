
from django.db import models


class Home(models.Model):
    identifier = models.TextField(blank=False) 
    n_app  = models.IntegerField(blank=True, null=True)   
    impact=models.FloatField(blank=True, null=True)   
    risk=models.FloatField(blank=True, null=True)  
    sustainability=models.FloatField(blank=True, null=True) 

    def __str__(self):
        return str(self.identifier)


class App(models.Model):
    name = models.TextField(blank=True)

    def __str__(self):
        return str(self.name)

class Power(models.Model):
    source = models.TextField(blank=True)
    rechargable = models.BooleanField(default = False)
    renewable = models.BooleanField(default = False)
    disposable = models.BooleanField(default = False)

    def __str__(self):
        return str(self.source)

class Connectivity(models.Model):
    technology = models.TextField(blank=True)
    wireless = models.BooleanField(default=True)

    def __str__(self):
        return str(self.technology)

class Device(models.Model):
    model = models.TextField(blank=False)
    type = models.TextField(blank=False)
    capability = models.TextField(blank=False)
    connectivities = models.ManyToManyField(Connectivity, blank=True)
    impact=models.FloatField(blank=True, null=True)
    risk=models.FloatField(blank=True, null=True)
    sustainability=models.FloatField(blank=True, null=True)
    apps = models.ManyToManyField(App, blank=True)
    power_supplies = models.ManyToManyField(Power, blank=True)
    home = models.ForeignKey(Home, on_delete=models.CASCADE, related_name="devices",blank=True, null=True)

    def __str__(self):
        return str(self.model)+"-" + str(self.home.identifier)
    

class CWE(models.Model):
    identifier = models.TextField(blank=True)

    def __str__(self):
        return str(self.identifier)


class Vulnerability(models.Model):
    identifier = models.TextField()
    description = models.TextField()
    baseSeverity = models.TextField()
    baseScore=models.FloatField()
    impactScore=models.FloatField()
    exploitabilityScore=models.FloatField()
    vector= models.TextField()
    cwes = models.ManyToManyField(CWE, blank=True)
    version = models.FloatField()
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name="vulnerabilities")

    def __str__(self):
       return str(self.identifier)


class Connection(models.Model):
    connectivity = models.TextField(blank=False)
    first_device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name="firstdevice")
    second_device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name="seconddevice")

    def __str__(self):
            return str(self.connectivity)


class ConnectionVulnerability(models.Model):
    identifier = models.TextField()
    description = models.TextField()
    baseSeverity = models.TextField()
    baseScore=models.FloatField()
    impactScore=models.FloatField()
    exploitabilityScore=models.FloatField()
    vector= models.TextField()
    cwe_cap = models.ManyToManyField(CWE, blank=True)
    version = models.FloatField()
    connection = models.ForeignKey(Connection, on_delete=models.CASCADE, related_name="connectionvulnerabilities")

    def __str__(self):
       return str(self.identifier)