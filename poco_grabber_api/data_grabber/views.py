from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from poco_common.core.models import SymbolInfo, GrabberSettings, BinanceAccount, User
from poco_common.exchange import serializers
from poco_common.exchange.exchange_actions.actions import ExchangeActions
from data_grabber.serializers import BinanceAccountStatusSerializer


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


class BinanceGeneralActionsViewSet(viewsets.ViewSet):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    lookup_field = 'slug'

    @action(detail=False, methods=['get'])
    def ping_binance(self, request, **kwargs):
        try:
            res = ExchangeActions().get_binance_ping()
        except Exception as ex:
            return Response({'error': str(ex)}, status=status.HTTP_400_BAD_REQUEST)
        if res == {}:
            return Response(data='ok', status=status.HTTP_200_OK)
        else:
            return Response({'error': 'error with no exception'},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def account_status(self, request, **kwargs):
        try:
            user = get_object_or_404(User, slug=kwargs['slug'])
            instance = ExchangeActions().get_account_status(user=user)
            serializer = BinanceAccountStatusSerializer(instance)
            return Response(serializer.data)
        except Exception as ex:
            return Response({'error': str(ex)}, status=status.HTTP_400_BAD_REQUEST)
