from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST


from srt.users.models import User
from srt.users.filters import UserFilter
from srt.users.serializers import SRTTokenObtainPairSerializer, ChangePasswordSerializer, UserSerializer, \
    StaffUserSerializer
from srt.users.permissions import UserCustomIsAllowedMethodOrStaff, IsCurrentUserOrStaff
from srt.core.filters import ObjectFieldFilterBackend
from srt.core.views import CustomTokenObtainPairView


class SRTTokenObtainPairView(CustomTokenObtainPairView):
    user = User
    serializer_class = SRTTokenObtainPairSerializer


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            old_password = serializer.data['old_password']
            if not self.request.user.check_password(old_password):
                return Response({"old_password": ["Wrong password"]}, status=HTTP_400_BAD_REQUEST)
            self.request.user.set_password(serializer.data['new_password'])
            self.request.user.save(update_fields=['password'])
            return Response(status=HTTP_200_OK)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, UserCustomIsAllowedMethodOrStaff, IsCurrentUserOrStaff]
    filter_backends = [ObjectFieldFilterBackend, SearchFilter, OrderingFilter, DjangoFilterBackend]
    filterset_class = UserFilter
    search_fields = ['email', 'full_name']
    ordering_fields = ['email', 'full_name']

    def get_serializer_class(self):
        return StaffUserSerializer if self.request.user.is_staff else UserSerializer
