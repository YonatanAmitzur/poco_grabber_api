from rest_framework.decorators import action
from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from core.models import SymbolInfo, GrabberRun, LooperSettings
from exchange import serializers
from data_grabber.looper.looper import Looper
from core.async_actions.async_operations import background


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


class GrabberRunsViewSet(viewsets.GenericViewSet,
                         mixins.ListModelMixin,
                         mixins.UpdateModelMixin,
                         mixins.CreateModelMixin):
    """Manage grabber runs in the database"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    queryset = GrabberRun.objects.all()
    serializer_class = serializers.GrabberRunSerializer

    @action(detail=False, methods=['get'])
    def start_run(self, request):
        grabber = GrabberRun(user=request.user)
        grabber.save()
        looper_settings = LooperSettings.load()
        looper_settings.is_running = True
        looper_settings.grabber_run_slug = grabber.slug
        looper_settings.run_type = LooperSettings.RUN_TYPE_UPDATE_SYMBOLS_ONLY
        looper_settings.save()
        self.start_looper(grabber)
        return Response(data={}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def stop_run(self, request):
        looper_settings = LooperSettings.load()
        looper_settings.is_running = False
        looper_settings.grabber_run_slug = None
        looper_settings.run_type = None
        looper_settings.save()
        return Response(data={}, status=status.HTTP_200_OK)

    @background
    def start_looper(self, grabber):
        looper = Looper(grabber)
        looper.run()

    def get_queryset(self):
        """Return objects for the current authenticated user only"""
        requested_status = self.request.query_params.get('status', None)
        queryset = self.queryset
        statuses_dict = {value: key for key, value in GrabberRun.STATUS_CHOICES}
        if requested_status is not None and requested_status in statuses_dict.keys():
            queryset = queryset.filter(status=requested_status)

        return queryset.filter(
            user=self.request.user
        ).order_by('-updated').distinct()

    def perform_create(self, serializer):
        """Create a new object"""
        serializer.save(user=self.request.user)


class LooperSettingsViewSet(viewsets.GenericViewSet,
                            mixins.ListModelMixin,
                            mixins.UpdateModelMixin,
                            mixins.CreateModelMixin):
    """Manage looper settings in the database"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    queryset = LooperSettings.objects.all()
    serializer_class = serializers.LooperSettingsSerializer

    def get_queryset(self):
        """Return objects for the current authenticated user only"""
        requested_is_running = self.request.query_params.get('is_running', None)
        requested_run_type = self.request.query_params.get('run_type', None)
        queryset = self.queryset
        if requested_is_running is not None:
            queryset = queryset.filter(is_running=requested_is_running)
        run_types_dict = {value: key for key, value in LooperSettings.RUN_TYPE_CHOICES}
        if requested_run_type is not None and requested_run_type in run_types_dict.keys():
            queryset = queryset.filter(run_type=requested_run_type)
        return queryset.filter(user=self.request.user).order_by('-updated').distinct()

    def perform_create(self, serializer):
        """Create a new object"""
        serializer.save(user=self.request.user)
