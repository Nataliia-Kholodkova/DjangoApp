from django.contrib.auth.models import User
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import status
from rest_framework_jwt.settings import api_settings
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from myapp.models import Post, Comment
from .serializers import PostSerializer, UserSerializer, LoginSerializer, CommentSerializer

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
jwt_decode_handler = api_settings.JWT_DECODE_HANDLER


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def posts(request):
    queryset = Post.objects.all()
    return Response(
        data=PostSerializer(queryset, many=True).data,
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def user_posts(request):
    token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
    payload = jwt_decode_handler(token)
    user_id = payload['user_id']
    try:
        user = User.objects.get(pk=user_id)
        posts = Post.objects.filter(user=user).all()
        return Response(
            data=PostSerializer(posts, many=True).data,
            status=status.HTTP_200_OK
        )
    except Exception:
        return Response(status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def add_post(request):
    token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
    payload = jwt_decode_handler(token)
    user_id = payload['user_id']
    try:
        user = User.objects.get(pk=user_id)
        post = Post(user=user, title=request.data['title'], text=request.data['text'])
        post.save()
        return Response(
            'Success',
            status=status.HTTP_201_CREATED
        )
    except Exception:
        return Response('Error', status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def like_post(request, id):
    try:
        post = Post.objects.get(pk=id)
        post.likes += 1
        post.save()
        return Response(
            'Success',
            status=status.HTTP_201_CREATED
        )
    except Exception:
        return Response('Error', status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def dislike_post(request, id):
    try:
        post = Post.objects.get(pk=id)
        post.dislikes += 1
        post.save()
        return Response(
            'Success',
            status=status.HTTP_201_CREATED
        )
    except Exception:
        return Response('Error', status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def delete_post(request, id):
    try:
        post = Post.objects.get(pk=id)
        token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
        payload = jwt_decode_handler(token)
        user_id = payload['user_id']
        if post.user.pk == user_id:
            post.delete()
            return Response(
                'Success',
                status=status.HTTP_200_OK
            )
        else:
            return Response('Error', status.HTTP_400_BAD_REQUEST)
    except Exception:
        return Response('Error', status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_comments(request, id):
    try:
        post = Post.objects.get(pk=id)
        comments = Comment.objects.filter(post=post).all()
        return Response(
            data=CommentSerializer(comments, many=True).data,
            status=status.HTTP_200_OK
        )
    except Exception:
        return Response('Error', status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def add_comment(request, id):
    token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
    payload = jwt_decode_handler(token)
    user_id = payload['user_id']
    try:
        user = User.objects.get(pk=user_id)
        post = Post.objects.get(pk=id)
        comment = Comment(user=user, post=post, text=request.data['text'])
        comment.save()
        return Response(
            'Success',
            status=status.HTTP_201_CREATED
        )
    except Exception:
        return Response('Error', status.HTTP_401_UNAUTHORIZED)


@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    serializer = UserSerializer(data=request.data)
    users = User.objects.filter(username=request.data['username']).all()
    if users:
        return Response('Username already exists', status.HTTP_400_BAD_REQUEST)
    if not serializer.is_valid():
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
    user = serializer.save()
    refresh = RefreshToken.for_user(user)
    res = {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }
    return Response(res, status.HTTP_201_CREATED)


class LogInView(TokenObtainPairView):
    serializer_class = LoginSerializer
