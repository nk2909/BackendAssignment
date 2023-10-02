from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import BlogPost, User, NonBuiltInUserToken
from .serializers import BlogPostSerializer, UserSerializer
from django.contrib import auth
from django.contrib.auth.hashers import make_password
from .authentication import UserTokenAuthentication
import datetime


class UserView(APIView):
    def get(self, request, pk=None):
        if pk is not None:
            user_obj = User.objects.get(pk=pk)
            serializer = UserSerializer(instance=user_obj)
        else:
            data = User.objects.all().values()
            serializer = UserSerializer(instance=data, many=True)

        return Response({"data": serializer.data})

    def post(self, request, pk=None):
        serializer = UserSerializer(data=request.data)
        password = request.data.get("password")
        if pk is None:
            if not serializer.is_valid():
                return Response(serializer.errors)
            user_add = serializer.save()
            hashed_password = make_password(password)
            user_add.password = hashed_password
            user_add.save()
            return Response({"data": serializer.data})
        user_obj = User.objects.get(pk=pk)
        serializer = UserSerializer(data=request.data, instance=user_obj, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"Message": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST
            )

    def delete(self, request, pk=None):
        user_obj = User.objects.get(pk=pk)
        user_obj.delete()
        user_obj.save()
        return Response({"Message": "User deleted"})


class UserRegisterView(APIView):
    def post(self, request):
        email = request.data.get("email", None)
        password = request.data.get("password", None)
        if user := User.objects.filter(email=email).exists():
            return Response({"Message": "User with the email already exists"})
        else:
            hashed_password = make_password(password)
            user_obj = User.objects.create(email=email, password=hashed_password)
            user_obj.save()
            return Response({"Message": "User Successfully created"})


class UserLoginView(APIView):
    def post(self, request):
        email = request.data.get("email", None)
        password = request.data.get("password", None)
        if user := User.objects.filter(email=email).first():
            user = auth.authenticate(username=email, password=password)
            if user is not None:
                token = NonBuiltInUserToken.objects.create(user_id=user.id)
                return Response(
                    {"Token": str(token), "is_superuser": user.is_superuser},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response({"Message": "Invalid username or password"})
        else:
            return Response({"Message": "Incorrect credentials"})


class PostListAPIView(APIView):
    authentication_classes = [
        UserTokenAuthentication,
    ]

    def get(self, request, *args, **kwargs):
        posts = BlogPost.objects.all()
        serializer = BlogPostSerializer(instance=posts, many=True)
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = BlogPostSerializer(data=data)
        if serializer.is_valid():
            post = serializer.save()
            post.posted_by = request.user
            post.save()
            return Response({"data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostDetailAPIView(APIView):
    authentication_classes = [
        UserTokenAuthentication,
    ]

    def get_object(self, pk):
        try:
            return BlogPost.objects.get(pk=pk)
        except BlogPost.DoesNotExist:
            return None

    def get(self, request, pk, *args, **kwargs):
        post = self.get_object(pk)
        if post is None:
            return Response(
                {"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = BlogPostSerializer(post)
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)

    def put(self, request, pk, *args, **kwargs):
        post = self.get_object(pk)
        if post is None:
            return Response(
                {"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND
            )
        data = request.data
        serializer = BlogPostSerializer(post, data=data, partial=True)
        if serializer.is_valid():
            if post.posted_by.id == request.user.id:
                serializer.save()
                return Response({"data": serializer.data}, status=status.HTTP_200_OK)
            return Response(
                {"error": "You are not authorized to edit this post"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        post = self.get_object(pk)
        if post is None:
            return Response(
                {"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND
            )
        if post.posted_by.id == request.user.id:
            post.delete()
            return Response({"Message": "Object deleted!"}, status=status.HTTP_200_OK)
        return Response(
            {"error": "You are not authorized to delete this post"},
            status=status.HTTP_401_UNAUTHORIZED,
        )
