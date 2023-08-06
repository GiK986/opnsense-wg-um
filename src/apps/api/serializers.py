from rest_framework import serializers


class WGUserSerializer(serializers.Serializer):
    title = serializers.CharField()
    url = serializers.CharField()


class AllowedIPsSerializer(serializers.Serializer):
    allowed_ips = serializers.CharField()
    disallowed_ips = serializers.CharField()


class OPNsenseAPIClientTestConnectionSerializer(serializers.Serializer):
    base_url = serializers.CharField()
    api_key = serializers.CharField()
    api_secret = serializers.CharField()


class SendEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ReconfigurationWgUserSerializer(serializers.Serializer):
    interface_uuid = serializers.CharField()
    allowed_ips_group = serializers.CharField()
