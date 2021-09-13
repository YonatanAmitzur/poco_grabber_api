from rest_framework import serializers
from core.models import SymbolInfo, GrabberRun, LooperSettings


class GrabberRunSerializer(serializers.ModelSerializer):

    class Meta:
        model = GrabberRun
        fields = '__all__'
        read_only_fields = ('slug',)


class LooperSettingsSerializer(serializers.ModelSerializer):

    class Meta:
        model = LooperSettings
        fields = '__all__'
        read_only_fields = ('slug',)


class SymbolInfoSerializer(serializers.ModelSerializer):

    class Meta:
        model = SymbolInfo
        fields = '__all__'
        read_only_fields = ('slug',)
