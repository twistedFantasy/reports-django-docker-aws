from rest_framework.serializers import ModelSerializer, Serializer, CharField, EmailField

from srt.users.models import User
from srt.core.serializers import CustomTokenObtainPairSerializer


FIELDS = ['id', 'email', 'is_staff', 'full_name']
READ_ONLY_FIELDS = ['id', 'email', 'is_staff']


class SRTTokenObtainPairSerializer(CustomTokenObtainPairSerializer):
    pass


class ChangePasswordSerializer(Serializer):
    old_password = CharField(required=True)
    new_password = CharField(required=True)


class StaffUserSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = FIELDS


class UserSerializer(StaffUserSerializer):

    class Meta(StaffUserSerializer.Meta):
        read_only_fields = READ_ONLY_FIELDS
