from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from .models import Home, Device, Vulnerability, CWE, Power
from .utils import vulns_search

@receiver(post_save, sender=Device)
def scan(sender, instance, created, **kwargs):
    if created:
        created_vulnerabilities = []
        vulns = vulns_search(instance.model)
        for vul in vulns:
            try:
                vul = str(vul).split("___")
                if len(vul) < 9:
                    continue

                vulnerability = Vulnerability.objects.create(
                    identifier=vul[0],
                    description=vul[1],
                    baseSeverity=vul[2],
                    baseScore=float(vul[4]),
                    impactScore=vul[6],
                    exploitabilityScore=vul[5],
                    vector=vul[8],
                    version=float(vul[3]),
                    device=instance
                )
                for cwe_identifier in vul[7].split(','):
                    cwe_obj, _ = CWE.objects.get_or_create(identifier=cwe_identifier.strip())
                    vulnerability.cwes.add(cwe_obj)

                created_vulnerabilities.append(vulnerability)
            except Exception as e:
                continue

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