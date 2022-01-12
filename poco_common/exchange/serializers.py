from rest_framework import serializers
from poco_common.core.models import SymbolInfo, GrabberSettings, BinanceAccount, \
    CoinInfo


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


class CoinInfoSerializer(serializers.ModelSerializer):

    class Meta:
        model = CoinInfo
        fields = '__all__'
        read_only_fields = ('slug',)
