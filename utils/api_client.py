from utils.pyopnsense.wireguard import EndpointClient, GeneralClient, ServerClient
from datetime import datetime, timedelta


class ApiClient:
    def __init__(self, api_key, api_secret, base_url):
        self.endpoint_client = EndpointClient(api_key, api_secret, base_url)
        self.general_client = GeneralClient(api_key, api_secret, base_url)
        self.server_client = ServerClient(api_key, api_secret, base_url)

    def get_all_clients(self):
        return self.endpoint_client.get_all()

    def get_client(self, uuid):
        return self.endpoint_client.get_client(uuid)

    def get_all_reserved_ips(self):
        return self.endpoint_client.get_all_reserved_ips()

    def get_status(self):
        return self.general_client.get_status()['items']

    def add_client(self, body):
        return self.endpoint_client.add_client(body)

    def del_client(self, uuid):
        return self.endpoint_client.del_client(uuid)

    def set_client(self, uuid, peer_client):
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
