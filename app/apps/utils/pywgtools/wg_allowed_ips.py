from ipaddress import ip_network


def calculate_allowed_ips(allowed_ips_str, disallowed_ips_str):
    allowed_ips = []
    disallowed_ips = []

    # Convert input strings into lists of ipaddress objects
    for allowed_ip_str in allowed_ips_str.split(','):
        allowed_ips.append(ip_network(allowed_ip_str.strip()))

    for disallowed_ip_str in disallowed_ips_str.split(','):
        disallowed_ips.append(ip_network(disallowed_ip_str.strip()))

    set_of_ips = set()

    for allowed_ip in allowed_ips:
        for disallowed_ip in disallowed_ips:
            if len(set_of_ips) == 0 and allowed_ip.overlaps(disallowed_ip):
                for ip in allowed_ip.address_exclude(disallowed_ip):
                    set_of_ips.add(ip)
            else:
                for set_of_ip in list(set_of_ips):
                    if set_of_ip.overlaps(disallowed_ip):
                        set_of_ips.remove(set_of_ip)
                        for ip in set_of_ip.address_exclude(disallowed_ip):
                            set_of_ips.add(ip)

    return ', '.join([str(ip) for ip in sorted(set_of_ips, key=lambda x: x)])
