from ipaddress import ip_network


def calculate_total_ips(ip_address):
    return ip_network(ip_address.strip(), strict=False).num_addresses - 2


def get_selected_key(dictionary: dict) -> str:
    selected_keys = [key for key, value in dictionary.items() if isinstance(value, dict) and 'selected' in value and (value['selected'] == '1' or value['selected'] == 1)]
    return selected_keys[0] if selected_keys else None
