from rest_framework import serializers


class RegisterSerializer(serializers.Serializer):
	username = serializers.CharField(max_length=150)
	email = serializers.EmailField(required=False, allow_blank=True)
	password = serializers.CharField(write_only=True, min_length=8)

	def create(self, validated_data):
		# Create the user using Django's create_user helper
		from django.contrib.auth.models import User
		user = User.objects.create_user(
			username=validated_data.get('username'),
			email=validated_data.get('email', ''),
			password=validated_data.get('password')
		)
		return user


class RegisterResponseSerializer(serializers.Serializer):
	message = serializers.CharField()
	user = serializers.DictField()
	token = serializers.CharField()
