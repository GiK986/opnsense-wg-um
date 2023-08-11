from django.contrib import messages
from rest_framework import generics as api_views, permissions
from rest_framework import views
from rest_framework.response import Response

from apps.api import serializers as api_serializers
from apps.api.services import send_email, parse_wireguard_config, create_or_update_wireguard_config
from apps.utils import mixins as utils_mixins
from apps.utils.api_client import ApiClient
from apps.utils.pywgtools import wg_allowed_ips
from apps.utils.pywgtools.wgtools import genkey, pubkey
from apps.wg_users.models import WireguardConfig


class DeleteWgUserAPIView(utils_mixins.APIClientRequiredMixin, api_views.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, wg_user_uuid):
        wg_user_name = self.api_client.get_client(wg_user_uuid)["name"]
        self.api_client.delete_client(wg_user_uuid)
        wireguard_config = WireguardConfig.objects.filter(wg_user_uuid=wg_user_uuid).first()

        if wireguard_config:
            wireguard_config.delete()

        messages.success(request, f"Deleted client {wg_user_name}")

        return Response({"status": "ok"})


class ReconfigurationWgUserAPIView(utils_mixins.APIClientRequiredMixin, api_views.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = api_serializers.ReconfigurationWgUserSerializer

    def post(self, request, wg_user_uuid):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        interface_uuid = serializer.validated_data["interface_uuid"]
        allowed_ips_group_id = serializer.validated_data["allowed_ips_group"]
        wg_user = self.api_client.get_client(wg_user_uuid)
        wg_user["keepalive"] = wg_user["keepalive"] if wg_user["keepalive"] else 15

        server_config = self.api_client.get_server_config(interface_uuid)
        allowed_ips = request.user.allowedipsgroup_set.get(id=allowed_ips_group_id).allowed_ips_calculated
        server_endpoint = request.user.default_api_client.endpoint_url
        private_key = genkey()
        public_key = pubkey(private_key)

        wireguard_config = WireguardConfig.objects.filter(wg_user_uuid=wg_user_uuid).first()
        if not wireguard_config:
            wireguard_config = WireguardConfig(
                wg_user_uuid=wg_user_uuid,
                name=wg_user["name"],
                address=wg_user["tunneladdress"],
                private_key=private_key,
                public_key=public_key,
                server_public_key=server_config["pubkey"],
                server_endpoint=server_endpoint,
                server_endpoint_port=server_config["port"],
                server_allowed_ips=allowed_ips,
                persistent_keepalive=wg_user["keepalive"],
                dns=server_config["dns"],
            )
            wireguard_config.save()
        else:
            wireguard_config.private_key = private_key
            wireguard_config.public_key = public_key
            wireguard_config.server_public_key = server_config["pubkey"]
            wireguard_config.server_endpoint = server_endpoint
            wireguard_config.server_endpoint_port = server_config["port"]
            wireguard_config.server_allowed_ips = allowed_ips
            wireguard_config.persistent_keepalive = wg_user["keepalive"]
            wireguard_config.dns = server_config["dns"]
            wireguard_config.save()

        wg_user["pubkey"] = public_key
        self.api_client.set_client(wg_user_uuid, wg_user)
        self.api_client.service_reconfigure()

        messages.success(request, f'Reconfigured client {wg_user["name"]}')
        return Response({"status": "ok"})


class SendEmailAPIView(api_views.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = api_serializers.SendEmailSerializer

    def post(self, request, wg_user_uuid):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email_sender = serializer.validated_data["email"]
        result = send_email(wg_user_uuid, email_sender)
        messages.success(request, f"Email sent to {email_sender}")
        return Response(result)


class OPNsenseAPIClientTestConnectionAPIView(utils_mixins.APIClientRequiredMixin, api_views.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = api_serializers.OPNsenseAPIClientTestConnectionSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        base_url = serializer.validated_data.get("base_url")
        api_key = serializer.validated_data.get("api_key")
        api_secret = serializer.validated_data.get("api_secret")
        api_client = ApiClient(base_url=base_url, api_key=api_key, api_secret=api_secret)
        result = api_client.test_connection()
        if result[0]:
            return Response({'status': 'success', 'message': result[1]})

        return Response({'status': 'error', 'message': result[1]})


class CalculateAllowedIPsAPIView(api_views.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = api_serializers.AllowedIPsSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        allowed_ips = serializer.validated_data.get("allowed_ips")
        disallowed_ips = serializer.validated_data.get("disallowed_ips")
        allowed_ips_calculated = wg_allowed_ips.calculate_allowed_ips(allowed_ips, disallowed_ips)

        return Response({"allowed_ips_calculated": allowed_ips_calculated})


class SearchAPIView(utils_mixins.APIClientRequiredMixin, views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializers = api_serializers.WGUserSerializer

    def get(self, request, q):
        wg_users = self.api_client.get_clients(q)
        results = [
            {
                "title": wg_user["name"],
                "url": f"{request.scheme}://{request.get_host()}/wg_users/update/{wg_user['uuid']}/"
            }
            for wg_user in wg_users
        ]

        serializer = api_serializers.WGUserSerializer(results, many=True)
        return Response(serializer.data)


class UploadFilesAPIView(utils_mixins.APIClientRequiredMixin, api_views.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = api_serializers.FileSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Access the uploaded files using request.FILES
        files = serializer.validated_data["files"]

        if not files:
            return Response({'error': 'No files were uploaded.'})

        for file in files:
            config = {}
            parse_config = parse_wireguard_config(file.read().decode("utf-8"))
            client = self.api_client.find_client(parse_config["Address"], parse_config["public_key"])

            if client:
                config["wg_user_uuid"] = client["uuid"]
                config["name"] = client["name"]
                config["address"] = parse_config.get("Address")
                config["private_key"] = parse_config.get("PrivateKey")
                config["public_key"] = parse_config.get("public_key")
                config["server_public_key"] = parse_config.get("PublicKey")
                config["server_endpoint"] = parse_config.get("Endpoint").split(":")[0]
                config["server_endpoint_port"] = parse_config.get("Endpoint").split(":")[1]
                config["server_allowed_ips"] = parse_config.get("AllowedIPs", "")
                config["persistent_keepalive"] = int(parse_config.get("PersistentKeepalive", "") or 0)
                config["dns"] = parse_config.get("DNS", "")

                create_or_update_wireguard_config(config)
                messages.success(request, f'File {file.name} uploaded successfully!')
            else:
                messages.error(request, f'No client found for file {file.name}!')

        return Response({'message': 'finished'})
