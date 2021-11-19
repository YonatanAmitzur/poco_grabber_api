from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from poco_common.core.models import SymbolInfo, GrabberSettings, BinanceAccount
from poco_common.exchange import serializers


class BinanceAccountViewSet(viewsets.GenericViewSet,
                            mixins.ListModelMixin,
                            mixins.CreateModelMixin):
    """Manage binance account from the database"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    queryset = BinanceAccount.objects.all()
    serializer_class = serializers.BinanceAccountSerializer

    def get_queryset(self):
        """Return objects for the current authenticated user only"""
        slug = self.request.user.slug
        queryset = self.queryset
        if slug is not None:
            queryset = queryset.filter(user__slug=slug)

        return queryset

    def perform_create(self, serializer):
        """Create a new object"""
        serializer.save(user=self.request.user)


class SymbolInfoViewSet(viewsets.GenericViewSet,
                        mixins.ListModelMixin,
                        mixins.CreateModelMixin):
    """Manage grabber symbol info in the database"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    queryset = SymbolInfo.objects.all()
    serializer_class = serializers.SymbolInfoSerializer

    def get_queryset(self):
        """Return objects for the current authenticated user only"""
        requested_symbol = self.request.query_params.get('symbol', None)
        queryset = self.queryset
        if requested_symbol is not None:
            queryset = queryset.filter(symbol=requested_symbol)

        return queryset.order_by('-symbol').distinct()

    def perform_create(self, serializer):
        """Create a new object"""
        serializer.save()


class GrabberSettingsViewSet(viewsets.GenericViewSet,
                             mixins.ListModelMixin,
                             mixins.UpdateModelMixin,
                             mixins.CreateModelMixin):
    """Manage looper settings in the database"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    queryset = GrabberSettings.objects.all()
    serializer_class = serializers.GrabberSettingsSerializer
    lookup_field = 'slug'

    def perform_create(self, serializer):
        """Create a new object"""
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)
