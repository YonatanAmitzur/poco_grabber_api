from rest_framework import serializers
from poco_common.core.models import SymbolInfo, GrabberRun, \
    GrabberSettings, BinanceAccount


class GrabberRunSerializer(serializers.ModelSerializer):

    class Meta:
        model = GrabberRun
        fields = '__all__'
        read_only_fields = ('slug',)


class GrabberSettingsSerializer(serializers.ModelSerializer):

    class Meta:
        model = GrabberSettings
        fields = '__all__'
        read_only_fields = ('slug',)


class SymbolInfoSerializer(serializers.ModelSerializer):

    class Meta:
        model = SymbolInfo
        fields = '__all__'
        read_only_fields = ('slug',)


class BinanceAccountSerializer(serializers.ModelSerializer):

    class Meta:
        model = BinanceAccount
        fields = '__all__'
        read_only_fields = ('slug',)

        def create(self, validated_data):
            validated_data['user'] = self.context['request'].user
            return super(BinanceAccountSerializer, self).create(validated_data)
