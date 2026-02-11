from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import User, SavedVideo # ★ 같은 앱에서 정확히 가져오기

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    profile_img = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = (
            'id', 'username', 'password', 'email', 'nickname', 
            'phone_number', 'birth_date', 'age', 'money', 'salary',
            'profile_img', 'description', 'investment_persona'
        )

    def create(self, validated_data):
        # 회원가입 시 모든 정보를 저장하도록 보강
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data.get('email', '')
        )
        user.nickname = validated_data.get('nickname', '')
        user.phone_number = validated_data.get('phone_number', '')
        user.birth_date = validated_data.get('birth_date', None)
        user.age = validated_data.get('age', 0)
        user.money = validated_data.get('money', 0)
        user.salary = validated_data.get('salary', 0)
        user.profile_img = validated_data.get('profile_img', None)
        user.description = validated_data.get('description', '')
        user.save()
        return user