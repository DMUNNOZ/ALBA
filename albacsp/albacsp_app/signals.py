from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from .models import Home, Device, Vulnerability, CWE, Power
import json
import requests

# ------------------------- API -----------------------
import json
import requests

def vulns_search(model):
    model_url = model.replace(" ", "%20")
    response = requests.get('https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch=' + model_url).text

    vulns = []
    json_object = json.loads(response)
    json_vulns = json_object["vulnerabilities"]
    
    for vul in range(0, len(json_vulns)):
        try:
            version = str(json_vulns[vul]['cve']['metrics'])
            id = str(json_vulns[vul]["cve"]["id"])
            description = str(json_vulns[vul]["cve"]["descriptions"][0]["value"])
            if ("cvssMetricV31" in version):
                version31 = str(json_vulns[vul]['cve']['metrics']['cvssMetricV31'][0]['cvssData']['version'])
                cvss31 = str(json_vulns[vul]['cve']['metrics']['cvssMetricV31'][0]['cvssData']['baseScore'])
                severity31 = str(json_vulns[vul]['cve']['metrics']['cvssMetricV31'][0]['cvssData']['baseSeverity'])
                exploitability31 = str(json_vulns[vul]['cve']['metrics']['cvssMetricV31'][0]['exploitabilityScore'])
                impact31 = str(json_vulns[vul]['cve']['metrics']['cvssMetricV31'][0]['impactScore'])
                cwe31 = ",".join([description["value"] for weakness in json_vulns[vul]['cve']['weaknesses'] for description in weakness["description"]])
                vector31 = str(json_vulns[vul]['cve']['metrics']['cvssMetricV31'][0]['cvssData']['vectorString'])

                vulns.append(id + "___" + description + "___" + severity31 + "___" + version31 + "___" + cvss31 + "___" + exploitability31 + "___" + impact31 + "___" + cwe31 + "___" + vector31)

            elif ("cvssMetricV30" in version):
                version30 = str(json_vulns[vul]['cve']['metrics']['cvssMetricV30'][0]['cvssData']['version'])
                cvss30 = str(json_vulns[vul]['cve']['metrics']['cvssMetricV30'][0]['cvssData']['baseScore'])
                severity30 = str(json_vulns[vul]['cve']['metrics']['cvssMetricV30'][0]['cvssData']['baseSeverity'])
                exploitability30 = str(json_vulns[vul]['cve']['metrics']['cvssMetricV30'][0]['exploitabilityScore'])
                impact30 = str(json_vulns[vul]['cve']['metrics']['cvssMetricV30'][0]['impactScore'])
                cwe30 = ",".join([description["value"] for weakness in json_vulns[vul]['cve']['weaknesses'] for description in weakness["description"]])
                vector30 = str(json_vulns[vul]['cve']['metrics']['cvssMetricV30'][0]['cvssData']['vectorString'])

                vulns.append(id + "___" + description + "___" + severity30 + "___" + version30 + "___" + cvss30 + "___" + exploitability30 + "___" + impact30 + "___" + cwe30 + "___" + vector30)
            
            elif ("cvssMetricV2" in version):
                version2 = str(json_vulns[vul]['cve']['metrics']['cvssMetricV2'][0]['cvssData']['version'])
                cvss2 = str(json_vulns[vul]['cve']['metrics']['cvssMetricV2'][0]['cvssData']['baseScore'])
                severity2 = str(json_vulns[vul]['cve']['metrics']['cvssMetricV2'][0]['baseSeverity'])
                exploitability2 = str(json_vulns[vul]['cve']['metrics']['cvssMetricV2'][0]['exploitabilityScore'])
                impact2 = str(json_vulns[vul]['cve']['metrics']['cvssMetricV2'][0]['impactScore'])
                cwe2 = ",".join([description["value"] for weakness in json_vulns[vul]['cve']['weaknesses'] for description in weakness["description"]])
                vector2 = str(json_vulns[vul]['cve']['metrics']['cvssMetricV2'][0]['cvssData']['vectorString'])

                vulns.append(id + "___" + description + "___" + severity2 + "___" + version2 + "___" + cvss2 + "___" + exploitability2 + "___" + impact2 + "___" + cwe2 + "___" + vector2)
        except:
            continue
    return vulns


# ---------------------------------------------------

@receiver(post_save, sender=Device)
def scan(sender, instance, created, **kwargs):
    if created:
        created_vulnerabilities = []
        vulns = vulns_search(instance.model)
        for vul in vulns:
            vul = str(vul).split("___")
            print(vul)
            vulnerability = Vulnerability.objects.create(
                identifier=vul[0],
                description=vul[1],
                baseSeverity=vul[2],
                baseScore=float(vul[4]),
                impactScore=vul[6],
                exploitabilityScore=vul[5],
                vector=vul[8],
                version=vul[3],
                device=instance
            )
            for cwe_identifier in vul[7].split(','):
                cwe_obj, _ = CWE.objects.get_or_create(identifier=cwe_identifier.strip())
                vulnerability.cwes.add(cwe_obj)

            created_vulnerabilities.append(vulnerability)

        # -------------------------- IMPACT -------------------------------------
        weighted_sum = 0.0
        total_weight = 0.0
        for vuln in created_vulnerabilities:
            weight = vuln.baseScore
            total_weight += weight
            weighted_sum += weight * vuln.baseScore

        weighted_average = weighted_sum / total_weight if total_weight > 0 else 0.0
        instance.impact = weighted_average
        instance.save()

        # ------------------------ HOME IMPACT ----------------------------------

        home = Home.objects.get(id=instance.home.id) 

        devices = home.devices.all()

        vulns_home = []

        for device in devices:
            dev_vulns = device.vulnerabilities.all()
            vulns_home.extend(dev_vulns)

        weighted_sum_home= 0.0
        total_weight_home = 0.0
        for vul in vulns_home:
            weight_home = vul.baseScore
            total_weight_home += weight_home
            weighted_sum_home += weight_home * vul.baseScore

        weighted_average_home = weighted_sum_home / total_weight_home if total_weight_home > 0 else 0.0
        home.impact = weighted_average_home
        home.save()

@receiver(m2m_changed, sender=Device.power_supplies.through)
def calculate_sustainability(sender, instance, **kwargs):
    cap = instance.capability

    power_supplies = instance.power_supplies.all()

    cap_values = {
        'Class 0': 10,
        'Class 1': 7,
        'Class 2': 5,
        'Unconstrained': 2
    }

    cap_value = cap_values.get(cap, 0)

    ps_values = []
    for ps in power_supplies:
        ps_rech = 10 if ps.rechargable else 2
        ps_renw = 10 if ps.renewable else 2
        ps_disp = 10 if ps.disposable else 2

        ps_score = (ps_rech * 0.25) + (ps_renw * 0.25) + (ps_disp * 0.25)
        ps_values.append(ps_score)

    if ps_values:
        sustainability_value = (cap_value * 0.25) + max(ps_values)
    else:
        sustainability_value = cap_value * 0.25

    instance.sustainability = sustainability_value
    instance.save()