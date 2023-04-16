from utils.pyopnsense.wireguard import EndpointClient, GeneralClient


class ApiClient:
    def __init__(self, api_key, api_secret, base_url):
        self.endpoint_client = EndpointClient(api_key, api_secret, base_url)
        self.general_client = GeneralClient(api_key, api_secret, base_url)

    def get_all_clients(self):
        return self.endpoint_client.get_all()['client']

    def get_client(self, uuid):
        return self.endpoint_client.get_client(uuid)

    def get_all_reserved_ips(self):
        return self.endpoint_client.get_all_reserved_ips()

    def get_status(self):
        return self.general_client.get_status()

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
        all_clients = self.endpoint_client.get_all()
        interfaces = self.get_status()['items']
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
