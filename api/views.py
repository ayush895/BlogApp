from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveUpdateDestroyAPIView, GenericAPIView
from rest_framework.exceptions import MethodNotAllowed
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import (
    RegisterSerializer,
    RegisterResponseSerializer,
    LoginSerializer,
    LoginResponseSerializer,
    BlogSerializer,
    BlogCreateSerializer,
)
from blogapp.models import Blog
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from .serializers import CommentSerializer
from blogapp.models import Comment as BlogComment

class Registeruser(APIView):
    """Register a new user."""

    # Request should only ask for email + password; response contains only a message and a minimal user object
    @extend_schema(request=RegisterSerializer, responses={201: RegisterResponseSerializer})
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Only email and password are required per new schema
        email = serializer.validated_data.get('email')
        password = serializer.validated_data.get('password')

        # Ensure uniqueness
        if User.objects.filter(email=email).exists() or User.objects.filter(username=email).exists():
            return Response({'error': 'A user with this email already exists'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=email, email=email, password=password)

        return Response({
            'message': 'User registered successfully',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
            }
        }, status=status.HTTP_201_CREATED)


# Permission: allow safe methods to everyone; require authenticated and author (or staff) for unsafe methods
class IsAuthorOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Allow GET, HEAD, OPTIONS
        if request.method in SAFE_METHODS:
            return True
        # For unsafe methods require authentication and that the user is author or staff
        return bool(request.user and request.user.is_authenticated and (obj.author == request.user or request.user.is_staff))


class LoginUser(APIView):
    """Authenticate an existing user (email + password)."""

    # Request should only ask for email + password; response returns user info and JWT token
    @extend_schema(request=LoginSerializer, responses={200: LoginResponseSerializer, 401: None})
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get('email')
        password = serializer.validated_data.get('password')

        # Find user by email and authenticate using username
        try:
            user_obj = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)

        user = authenticate(username=user_obj.username, password=password)

        if user is None:
            return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)

        # Generate JWT token
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        # Return user info and JWT token
        return Response({
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'email': user.email,
            },
            'access': access_token
        })


class BlogList(ListAPIView):
    """List all published blogs."""
    queryset = Blog.objects.filter(status='published').order_by('-created_at')
    serializer_class = BlogSerializer

    @extend_schema(responses=BlogSerializer(many=True))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class BlogCreate(CreateAPIView):
    """Create a new blog post."""
    parser_classes = [MultiPartParser, FormParser]
    queryset = Blog.objects.all()
    serializer_class = BlogCreateSerializer

    @extend_schema(request=BlogCreateSerializer, responses=BlogSerializer)
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class BlogDetail(RetrieveUpdateDestroyAPIView):
    """Retrieve, update (PATCH) or delete a single blog by id."""
    queryset = Blog.objects.all()
    lookup_field = 'id'
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthorOrReadOnly]
    authentication_classes = [JWTAuthentication]

    def get_serializer_class(self):
        # Use BlogSerializer for reads and BlogUpdateSerializer for updates
        if self.request and self.request.method in ('PUT', 'PATCH'):
            from api.serializers import BlogUpdateSerializer
            return BlogUpdateSerializer
        return BlogSerializer

    @extend_schema(responses=BlogSerializer)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(exclude=True)
    def put(self, request, *args, **kwargs):
        # Keep PUT behavior identical to PATCH but exclude it from the OpenAPI schema.
        return super().put(request, *args, **kwargs)

    @extend_schema(request=__import__('api.serializers', fromlist=['BlogUpdateSerializer']).BlogUpdateSerializer,
                   responses=BlogSerializer)
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @extend_schema(responses={204: None})
    def delete(self, request, *args, **kwargs):
        """Delete the blog instance. Returns 204 No Content on success."""
        return super().delete(request, *args, **kwargs)


class BlogSaveDraft(GenericAPIView):
    """Save a blog as draft (set status='draft')."""
    queryset = Blog.objects.all()
    lookup_field = 'id'
    serializer_class = BlogSerializer

    @extend_schema(request=None, responses=BlogSerializer)
    def post(self, request, id, *args, **kwargs):
        # use GenericAPIView's get_object for consistent lookup
        blog = self.get_object()
        blog.status = 'draft'
        blog.save()
        serializer = self.get_serializer(blog, context={'request': request})
        return Response(serializer.data)


class BlogPublish(GenericAPIView):
    """Publish a blog (set status='published')."""
    queryset = Blog.objects.all()
    lookup_field = 'id'
    serializer_class = BlogSerializer

    @extend_schema(request=None, responses=BlogSerializer)
    def post(self, request, id, *args, **kwargs):
        blog = self.get_object()
        blog.status = 'published'
        blog.save()
        serializer = self.get_serializer(blog, context={'request': request})
        return Response(serializer.data)


class CommentsList(ListAPIView):
    """List comments for a given blog (by blog id path param)."""
    serializer_class = CommentSerializer

    def get_queryset(self):
        blog_id = self.kwargs.get('id')
        return BlogComment.objects.filter(blog_id=blog_id).order_by('created_at')

    @extend_schema(responses=CommentSerializer(many=True))
    def get(self, request, id, *args, **kwargs):
        return super().get(request, *args, **kwargs)


# @api_view(['POST'])
# def login_user(request):
#     """
#     Authenticate an existing user.
#     """
#     username = request.data.get('username')
#     password = request.data.get('password')

#     user = authenticate(username=username, password=password)

#     if user is None:
#         return Response({'error': 'Invalid username or password'}, status=status.HTTP_401_UNAUTHORIZED)

#     token, _ = Token.objects.get_or_create(user=user)

#     return Response({
#         'message': 'Login successful',
#         'user': {
#             'id': user.id,
#             'username': user.username,
#             'email': user.email,
#         },
#         'token': token.key
#     })
