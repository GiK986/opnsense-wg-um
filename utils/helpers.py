from ipaddress import ip_network


def calculate_total_ips(ip_address):
    return ip_network(ip_address.strip(), strict=False).num_addresses - 2
