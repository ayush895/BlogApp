from rest_framework import serializers


class RegisterSerializer(serializers.Serializer):
	# Registration requires only email and password per new schema
	email = serializers.EmailField(required=True)
	password = serializers.CharField(write_only=True, min_length=8)

	def create(self, validated_data):
		# Create the user using Django's create_user helper
		from django.contrib.auth.models import User
		email = validated_data.get('email')
		# Use email as username to keep uniqueness; if username exists, raise
		if User.objects.filter(username=email).exists():
			raise serializers.ValidationError({'email': 'A user with this email already exists.'})
		user = User.objects.create_user(
			username=email,
			email=email,
			password=validated_data.get('password')
		)
		return user


class UserPublicSerializer(serializers.Serializer):
    """Minimal user representation used in API responses (exposed fields only)."""
    id = serializers.IntegerField(read_only=True)
    email = serializers.EmailField(read_only=True)


class RegisterResponseSerializer(serializers.Serializer):
	# Response for registration should include only minimal user info
	message = serializers.CharField()
	user = UserPublicSerializer()


class LoginSerializer(serializers.Serializer):
	# Login should accept email and password only
	email = serializers.EmailField()
	password = serializers.CharField(write_only=True, min_length=8)


class LoginResponseSerializer(serializers.Serializer):
	# Return token in login response for authorization in other APIs
	message = serializers.CharField()
	user = UserPublicSerializer()
	access = serializers.CharField()



class BlogSerializer(serializers.Serializer):
	id = serializers.IntegerField(read_only=True)
	title = serializers.CharField()
	author = serializers.CharField(source='author.username', read_only=True)
	image_url = serializers.SerializerMethodField()
	content = serializers.CharField()
	status = serializers.CharField()
	created_at = serializers.DateTimeField(read_only=True)
	updated_at = serializers.DateTimeField(read_only=True)

	def get_image_url(self, obj):
		# Use Blog.get_image_url if available else fallback to field url
		try:
			url = obj.get_image_url()
		except Exception:
			if getattr(obj, 'image', None) and getattr(obj.image, 'url', None):
				url = obj.image.url
			else:
				return None

		# If we have a request in context, return an absolute URI so clients can fetch it
		request = self.context.get('request') if hasattr(self, 'context') else None
		if request and url and not url.startswith('http'):
			try:
				return request.build_absolute_uri(url)
			except Exception:
				return url

		return url


class BlogCreateSerializer(serializers.ModelSerializer):
	"""Serializer for creating Blog instances. Accepts an author id to assign ownership."""
	author = serializers.IntegerField(write_only=True, required=True)

	class Meta:
		model = __import__('blogapp.models', fromlist=['Blog']).Blog
		fields = ['title', 'content', 'image', 'status', 'author']

	def validate_author(self, value):
		from django.contrib.auth.models import User
		try:
			User.objects.get(pk=value)
		except User.DoesNotExist:
			raise serializers.ValidationError('Author (user id) does not exist')
		return value

	def create(self, validated_data):
		from django.contrib.auth.models import User
		author_id = validated_data.pop('author')
		author = User.objects.get(pk=author_id)
		blog = self.Meta.model.objects.create(author=author, **validated_data)
		return blog


class BlogUpdateSerializer(serializers.ModelSerializer):
	"""Serializer for updating Blog instances. Author is not writable here."""
	class Meta:
		model = __import__('blogapp.models', fromlist=['Blog']).Blog
		fields = ['title', 'content', 'image', 'status']


class CommentSerializer(serializers.Serializer):
	id = serializers.IntegerField(read_only=True)
	user = serializers.CharField(source='user.username', read_only=True)
	content = serializers.CharField()
	created_at = serializers.DateTimeField(read_only=True)
	updated_at = serializers.DateTimeField(read_only=True)

	class Meta:
		ref_name = 'Comment'
