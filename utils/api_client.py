from utils.pyopnsense.wireguard import EndpointClient, GeneralClient, ServerClient, ServiceClient
from datetime import datetime, timedelta
from ipaddress import ip_interface


class ApiClient:
    def __init__(self, api_key, api_secret, base_url):
        self.endpoint_client = EndpointClient(api_key, api_secret, base_url)
        self.general_client = GeneralClient(api_key, api_secret, base_url)
        self.server_client = ServerClient(api_key, api_secret, base_url)
        self.service_client = ServiceClient(api_key, api_secret, base_url)

    def get_all_clients(self):
        return self.endpoint_client.get_all()

    def get_client(self, uuid):
        return self.endpoint_client.get_client(uuid)

    def get_all_reserved_ips(self):
        return self.endpoint_client.get_all_reserved_ips()

    def get_status(self):
        return self.general_client.get_status()['items']

    def add_client(self, name, public_key, host_ip):
        payload = {
            "client": {
                "enabled": "1",
                "name": name,
                "pubkey": public_key,
                "tunneladdress": host_ip + '/32',
                "keepalive": 15
            }
        }
        response = self.endpoint_client.add_client(payload)

        return response['uuid']

    def delete_client(self, uuid):
        return self.endpoint_client.del_client(uuid)

    def set_client(self, uuid, peer_client_dict):
        peer_client = {
            "client": peer_client_dict
        }
        return self.endpoint_client.set_client(uuid, peer_client)

    def get_general(self):
        return self.general_client.get()

    def get_search_client(self):
        return self.endpoint_client.search_client()

    def get_interface_clients(self):
        all_clients = self.get_all_clients()
        interfaces = self.get_status()
        interface_clients = []
        for key, value in all_clients.items():
            value['uuid'] = key
            value['interface'] = 'n/a'
            value['interface_name'] = 'n/a'

            for interface in interfaces.values():
                if key in interface['peers']:
                    value['interface'] = interface['interface']
                    value['interface_name'] = interface['name']

            interface_clients.append(value)

        sorted_interface_clients = list(sorted(interface_clients,
                                               key=lambda x: int(x['tunneladdress'].split('.')[-1].split('/')[0]),
                                               reverse=True))

        return sorted_interface_clients

    def get_client_stats(self):
        all_clients = self.get_all_clients()
        clients_tunnel_address = {key: value['tunneladdress'] for key, value in all_clients.items()}
        interfaces = self.get_status()
        client_stats = []

        for interface in interfaces.values():
            for uuid, peer in interface['peers'].items():
                peer['interface'] = interface['interface']
                peer['interface_name'] = interface['name']
                peer['tunneladdress'] = clients_tunnel_address[uuid]
                peer['lastHandshake'] = datetime.strptime(peer['lastHandshake'], '%Y-%m-%d %H:%M:%S%z') \
                    if peer['lastHandshake'] != '0000-00-00 00:00:00+00:00' else datetime(1, 1, 1, 0, 0, 0, 0)
                peer['uuid'] = uuid
                del peer['publicKey'], peer['enabled']
                client_stats.append(peer)

        sorted_client_stats = list(sorted(client_stats,
                                          key=lambda x: int(x['tunneladdress'].split('.')[-1].split('/')[0]),
                                          reverse=True))

        return sorted_client_stats

    def get_client_stats_count(self):
        all_clients = self.get_client_stats()
        total = len(all_clients)
        inactive = len([client for client in all_clients if client['lastHandshake'] == datetime(1, 1, 1, 0, 0, 0, 0)])
        inactive_more_3days = len([client for client in all_clients if
                                   datetime(1, 1, 1, 0, 0, 0, 0) < client['lastHandshake'].replace(tzinfo=None) < datetime.now() - timedelta(days=3)])
        active = total - (inactive + inactive_more_3days)

        return {
            'total': total,
            'inactive': inactive,
            'inactive_more_3days': inactive_more_3days,
            'active': active,
        }

    def get_client_stats_by_filter(self, filter_key):
        all_clients = self.get_client_stats()

        filters = {
            'active': lambda x: x['lastHandshake'] != datetime(1, 1, 1, 0, 0, 0, 0) and x['lastHandshake'].replace(tzinfo=None) > datetime.now() - timedelta(days=3),
            'inactive': lambda x: x['lastHandshake'] == datetime(1, 1, 1, 0, 0, 0, 0),
            'inactive_more_3days': lambda x: datetime(1, 1, 1, 0, 0, 0, 0) < x['lastHandshake'].replace(tzinfo=None) < datetime.now() - timedelta(days=3),
        }

        if filter_key in filters:
            return [client for client in all_clients if filters[filter_key](client)]
        else:
            return all_clients

    def get_interfaces(self):
        servers = self.server_client.search_server()
        interfaces = list(map(lambda x: {'name': x['name'], 'uuid': x['uuid']}, servers['rows']))

        return interfaces

    def get_server_config(self, uuid):
        server = self.server_client.get_server(uuid)
        server['server']['tunneladdress'] = list(server['server']['tunneladdress'].keys())[0]
        server_config = {key: value for key, value in server['server'].items()
                         if key in ['pubkey', 'port', 'name', 'tunneladdress']}

        server_config['dns'] = ', '.join(list(server['server']['dns']))

        return server_config

    def get_hosts_iterator(self, uuid):
        server_address = self.get_server_config(uuid)['tunneladdress']
        reserved_ips = self.get_all_reserved_ips()
        net_interface = ip_interface(server_address)
        reserved_ips.add(str(net_interface.ip))
        network = net_interface.network
        hosts_iterator = (host for host in network.hosts() if str(host) not in reserved_ips)
        return hosts_iterator

    def update_server_config(self, uuid, added_clients):
        wireguard_instance_info = self.server_client.get_server(uuid)
        server_peers = wireguard_instance_info['server']['peers']
        del wireguard_instance_info['server']['instance']

        # find new peer if not selected
        for peerUUID in server_peers:
            if wireguard_instance_info['server']['peers'][peerUUID]['selected'] == 1:
                added_clients.append(peerUUID)

        if wireguard_instance_info['server']['dns']:
            wireguard_instance_info['server']['dns'] = list(wireguard_instance_info['server']['dns'].keys())[0]
        else:
            wireguard_instance_info['server']['dns'] = ''

        if wireguard_instance_info['server']['tunneladdress']:
            wireguard_instance_info['server']['tunneladdress'] = \
                list(wireguard_instance_info['server']['tunneladdress'].keys())[0]

        wireguard_instance_info['server']['peers'] = ','.join(added_clients)

        response = self.server_client.set_server(uuid, wireguard_instance_info)

        if response['result'] == 'saved':
            self.service_reconfigure()

        return response

    def test_connection(self):
        try:
            self.service_client.status()
            return True, "Test connection successful!"
        except Exception as ex:
            return False, str(ex)

    def get_clients(self, query=None):
        clients = self.get_interface_clients()

        if query:
            clients = [client for client in clients if query.lower() in client['name'].lower()]

        return clients

    def service_reconfigure(self):
        self.service_client.reconfigure()
