from rest_framework import serializers
from poco_common.core.models import BinanceAccountStatus


class BinanceAccountStatusSerializer(serializers.ModelSerializer):
    user_slug = serializers.CharField(source='user.slug')

    class Meta:
        model = BinanceAccountStatus
        fields = (
            'slug',
            'created',
            'status',
            'user_slug',
        )
