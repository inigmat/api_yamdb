from django.shortcuts import get_object_or_404
<<<<<<< HEAD
=======
from rest_framework import filters, viewsets
from reviews.models import Reviews, Comments, Titles, Categories, Genres, Titles, Rating
>>>>>>> review
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken

from api.permissions import (AdminModeratorAuthorPermission,
                             IsAdminUserOrReadOnly, IsSelfOrAdmins)
from api.serializers import (CategoriesSerializer, CommentsSerializer,
                             GenresSerializer, ReviewsSerializer,
                             TitlesSerializer)
from reviews.models import Categories, Comments, Genres, Reviews, Titles
from users.models import User
from api.serializers import (MeSerializer, SignUpSerializer, TokenSerializer,
                             UserSerializer)
from users.utils import generate_confirmation_code, send_mail_with_code


class AuthCreateUserView(APIView):
    permission_classes = (
        permissions.AllowAny,
    )

    def post(self, request):
        email = self.request.data.get('email')
        confirmation_code = generate_confirmation_code()
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(
            data=self.request.data,
            confirmation_code=confirmation_code
        )
        send_mail_with_code(email, confirmation_code)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TokenCreateView(CreateAPIView):
    permission_classes = (
        permissions.AllowAny,
    )

    def get_token(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(User, username=request.data.get('username'))
        if user.confirmation_code != request.data.get('confirmation_code'):
            response = {'confirmation_code': 'Неверный код'}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        response = {'token': self.get_token(user)}
        return Response(response, status=status.HTTP_200_OK)


class UsersViewSet(ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (IsSelfOrAdmins,)
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter, )
    search_fields = ('username', )
    lookup_field = 'username'

    @action(
        detail=False,
        permission_classes=(permissions.IsAuthenticated,),
        methods=['get', 'patch'],
        url_path='me'
    )
    def get_or_update(self, request):
        user = get_object_or_404(User, username=self.request.user)
        if request.method == 'GET':
            serializer = MeSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == 'PATCH':
            serializer = MeSerializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)


class CategoriesViewSet(viewsets.ModelViewSet):
    queryset = Categories.objects.all()
    serializer_class = CategoriesSerializer
    permission_classes = (IsAdminUserOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class GenresViewSet(viewsets.ModelViewSet):
    queryset = Genres.objects.all()
    serializer_class = GenresSerializer
    permission_classes = (IsAdminUserOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class TitlesViewSet(viewsets.ModelViewSet):
    queryset = Titles.objects.all()
    serializer_class = TitlesSerializer
    permission_classes = (IsAdminUserOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)


class ReviewsViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewsSerializer
    permission_classes = [AdminModeratorAuthorPermissionNew]

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        new_queryset = Reviews.objects.filter(title=title_id)
        return new_queryset

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        titles = get_object_or_404(Titles, id=title_id)
        serializer.save(author=self.request.user,
                        titles=titles)


class CommentsViewSet(viewsets.ModelViewSet):
    serializer_class = CommentsSerializer
    permission_classes = [AdminModeratorAuthorPermissionNew]

    def get_queryset(self):
        review_id = self.kwargs.get('review_id')
        new_queryset = Comments.objects.filter(review=review_id)
        return new_queryset

    def perform_create(self, serializer):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Reviews, id=review_id)
        serializer.save(author=self.request.user,
                        review=review)
