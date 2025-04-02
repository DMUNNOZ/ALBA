from django.utils import timezone
import json
import requests
from datetime import timedelta
from .models import Device, Vulnerability, CWE


# ------------------------- API -----------------------

def vulns_search(model):
    model_url = model.replace(" ", "%20")
    response = requests.get('https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch=' + model_url)

    if response.status_code != 200:
        return []

    vulns = []
    json_object = json.loads(response.text)
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
# ------------------------- API -----------------------

def update_device_impact(device):
    vulns = device.vulnerabilities.all()
    weighted_sum = 0.0
    total_weight = 0.0
    for vuln in vulns:
        weight = vuln.baseScore
        total_weight += weight
        weighted_sum += weight * vuln.baseScore
    weighted_average = weighted_sum / total_weight if total_weight > 0 else 0.0
    device.impact = weighted_average
    device.save()


def update_home_impact(home):
    devices = home.devices.all()
    vulns_home = []
    for device in devices:
        dev_vulns = device.vulnerabilities.all()
        vulns_home.extend(dev_vulns)
    weighted_sum_home = 0.0
    total_weight_home = 0.0
    for vuln in vulns_home:
        weight_home = vuln.baseScore
        total_weight_home += weight_home
        weighted_sum_home += weight_home * vuln.baseScore
    weighted_average_home = weighted_sum_home / total_weight_home if total_weight_home > 0 else 0.0
    home.impact = weighted_average_home
    home.save()


def update_device_vuln():
    now = timezone.now()
    devices = Device.objects.all()

    for device in devices:
        if now >= device.lastUpdate + timedelta(seconds=device.updateFreq):
            vulns = vulns_search(device.model)

            for vul in vulns:
                try:
                    vul_data = vul.split("___")
                    if len(vul_data) < 9:
                        continue

                    identifier = vul_data[0]
                    base_score = float(vul_data[4])
                    version_value = float(vul_data[3])

                    existing_vulns = Vulnerability.objects.filter(identifier=identifier, device=device)
                    if existing_vulns.exists():
                        for vuln in existing_vulns:
                            vuln.description = vul_data[1]
                            vuln.baseSeverity = vul_data[2]
                            vuln.baseScore = base_score
                            vuln.impactScore = vul_data[6]
                            vuln.exploitabilityScore = vul_data[5]
                            vuln.vector = vul_data[8]
                            vuln.version = version_value
                            vuln.save()

                            vuln.cwes.clear()
                            for cwe_identifier in vul_data[7].split(','):
                                cwe_obj, _ = CWE.objects.get_or_create(identifier=cwe_identifier.strip())
                                vuln.cwes.add(cwe_obj)
                    else:
                        new_vuln = Vulnerability.objects.create(
                            identifier=identifier,
                            device=device,
                            description=vul_data[1],
                            baseSeverity=vul_data[2],
                            baseScore=base_score,
                            impactScore=vul_data[6],
                            exploitabilityScore=vul_data[5],
                            vector=vul_data[8],
                            version=version_value
                        )
                        for cwe_identifier in vul_data[7].split(','):
                            cwe_obj, _ = CWE.objects.get_or_create(identifier=cwe_identifier.strip())
                            new_vuln.cwes.add(cwe_obj)
                except Exception as e:
                    continue

            update_device_impact(device)
            update_home_impact(device.home)

            device.lastUpdate = now
            device.save()
