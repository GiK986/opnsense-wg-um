from apps.utils.pyopnsense import client


class EndpointClient(client.OPNClient):

    def __init__(self, api_key, api_secret, base_url):
        super().__init__(api_key, api_secret, base_url)
        self.module = 'wireguard'
        self.controller = 'client'

    def add_client(self, body):
        endpoint = self._generate_endpoint(command='addClient')
        return self._post_json(endpoint, payload=body)

    def del_client(self, uuid):
        endpoint = self._generate_endpoint(command='delClient', parameters=uuid)
        return self._post_json(endpoint, payload={})

    def get_all(self):
        endpoint = self._generate_endpoint(command='get')
        get_all_clients = self._get(endpoint)
        all_clients = get_all_clients['client']['clients']['client']
        for key, value in all_clients.items():
            value['tunneladdress'] = list(value['tunneladdress'].keys())[0]
        return all_clients

    def get_client(self, uuid):
        endpoint = self._generate_endpoint(command='getClient', parameters=uuid)
        client_info = self._get(endpoint)
        client_info['client']['tunneladdress'] = list(client_info['client']['tunneladdress'].keys())[0]
        client_info['client']['uuid'] = uuid
        client_info['client']['keepalive'] = int(client_info['client']['keepalive'] or 0)
        client_info['client']['enabled'] = bool(int(client_info['client']['enabled']))
        return client_info['client']

    def search_client(self):
        endpoint = self._generate_endpoint(command='searchClient')
        return self._get(endpoint)

    def set_client(self, uuid: str, peer_client: dict):
        endpoint = self._generate_endpoint(command='setClient', parameters=uuid)
        return self._post_json(endpoint, payload=peer_client)

    # https://91.132.60.114/api/wireguard/client/set
    def set(self, payload):
        endpoint = self._generate_endpoint(command='set')
        return self._post_json(endpoint, payload=payload)

    # https://91.132.60.114/api/wireguard/service/reconfigure
    def get_all_reserved_ips(self):
        result = self.search_client()
        reserved_ips = set(map(lambda x: x['tunneladdress'].split('/')[0], result['rows']))
        return reserved_ips


class GeneralClient(client.OPNClient):

    def __init__(self, api_key, api_secret, base_url):
        super().__init__(api_key, api_secret, base_url)
        self.module = 'wireguard'
        self.controller = 'general'

    def get(self):
        endpoint = self._generate_endpoint(command='get')
        return self._get(endpoint)

    def get_status(self):
        endpoint = self._generate_endpoint(command='getStatus')
        return self._get(endpoint)

    def set(self, payload):
        endpoint = self._generate_endpoint(command='set')
        return self._post_json(endpoint, payload)


class ServerClient(client.OPNClient):

    def __init__(self, api_key, api_secret, base_url):
        super().__init__(api_key, api_secret, base_url)
        self.module = 'wireguard'
        self.controller = 'server'

    def add_server(self, payload):
        endpoint = self._generate_endpoint(command='addServer')
        return self._post_json(endpoint, payload)

    def del_server(self, uuid):
        endpoint = self._generate_endpoint(command='delServer')
        return self._post_json(endpoint, payload=uuid)

    def get(self):
        endpoint = self._generate_endpoint(command='get')
        return self._get(endpoint)

    def get_server(self, uuid):
        endpoint = self._generate_endpoint(command='getServer', parameters=uuid)
        return self._get(endpoint)

    def search_server(self):
        endpoint = self._generate_endpoint(command='searchServer')
        return self._get(endpoint)

    def set(self, payload):
        endpoint = self._generate_endpoint(command='set')
        return self._post_json(endpoint, payload)

    def set_server(self, uuid, payload):
        endpoint = self._generate_endpoint(command='setServer', parameters=uuid)
        return self._post_json(endpoint, payload)

    def toggle_server(self, uuid):
        endpoint = self._generate_endpoint(command='toggleServer', parameters=uuid)
        return self._post_json(endpoint, payload={})


class ServiceClient(client.OPNClient):

    def __init__(self, api_key, api_secret, base_url):
        super().__init__(api_key, api_secret, base_url)
        self.module = 'wireguard'
        self.controller = 'service'

    def reconfigure(self):
        endpoint = self._generate_endpoint(command='reconfigure')
        return self._post_json(endpoint, payload={})

    def restart(self):
        endpoint = self._generate_endpoint(command='restart')
        return self._post_json(endpoint, payload={})

    def show(self):
        endpoint = self._generate_endpoint(command='show')
        return self._get(endpoint)

    def show_config(self):
        endpoint = self._generate_endpoint(command='showconf')
        return self._get(endpoint)

    def show_handshake(self):
        endpoint = self._generate_endpoint(command='showhandshake')
        return self._get(endpoint)

    def start(self):
        endpoint = self._generate_endpoint(command='start')
        return self._post_json(endpoint, payload={})

    def status(self):
        endpoint = self._generate_endpoint(command='status')
        return self._get(endpoint)

    def stop(self):
        endpoint = self._generate_endpoint(command='stop')
        return self._post_json(endpoint, payload={})
