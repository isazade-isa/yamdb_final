from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import (
    IsAdminUser, IsAuthenticated, IsAuthenticatedOrReadOnly
)
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework import filters, viewsets, status

from users.models import CustomUser
from reviews.models import Category, Genre, Review, Title
from reviews.filters import TitleFilterSet
from api.permissions import (
    IsAuthorOrStaffOrReadOnly, IsAdmin, IsAuthorAdminOrModeratorPermission
)
from api.mixins import MixViewSet
from api.serializers import (
    CategorySerializer, GenreSerializer, TitleReadSerializer,
    TitleWriteSerializer, UserSerializer, CommentSerializer,
    ReviewSerializer, TokenSerializer, SingUpSerializer
)


class CategoryViewSet(MixViewSet):
    """
    Категории (типы) произведений.
    """
    queryset = Category.objects.all()
    lookup_field = 'slug'
    serializer_class = CategorySerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    permission_classes = [IsAuthorOrStaffOrReadOnly, ]


class GenreViewSet(MixViewSet):
    """
    Категории жанров.
    """
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    permission_classes = [IsAuthorOrStaffOrReadOnly, ]


class TitleViewSet(viewsets.ModelViewSet):
    """
    Произведения, к которым пишут отзывы
    (определённый фильм, книга или песенка).
    """
    queryset = Title.objects.annotate(Avg('reviews__score')).all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilterSet
    permission_classes = [IsAuthorOrStaffOrReadOnly, ]

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleReadSerializer
        return TitleWriteSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    Ресурсы API YaMDb
    Ресурс auth: аутентификация.
    Ресурс users: пользователи.
    Ресурс titles: произведения, к которым пишут отзывы
        (определённый фильм, книга или песенка).
    Ресурс categories: категории (типы) произведений
        («Фильмы», «Книги», «Музыка»).
    Ресурс genres: жанры произведений. Одно произведение может
        быть привязано к нескольким жанрам.
    Ресурс reviews: отзывы на произведения.
        Отзыв привязан к определённому произведению.
    Ресурс comments: комментарии к отзывам.
        Комментарий привязан к определённому отзыву.
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'
    permission_classes = [IsAdmin | IsAdminUser]

    @action(detail=False,
            permission_classes=[IsAuthenticated],
            methods=['get']
            )
    def me(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @me.mapping.patch
    def update_user(self, request):
        serializer = self.get_serializer(
            self.request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(role=self.request.user.role)
        return Response(serializer.data)


class ReviewsViewSet(viewsets.ModelViewSet):

    serializer_class = ReviewSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = [
        IsAuthorAdminOrModeratorPermission,
        IsAuthenticatedOrReadOnly
    ]

    def _get_title(self):
        return get_object_or_404(Title, id=self.kwargs['title_id'])

    def perform_create(self, serializer):
        title = self._get_title()
        serializer.save(author=self.request.user, title=title)

    def get_queryset(self):
        title = self._get_title()
        return title.reviews.all()


class CommentsViewSet(viewsets.ModelViewSet):
    """
    отзывы на произведения. Отзыв привязан к определённому произведению.
    """
    queryset = Review.objects.all()
    serializer_class = CommentSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = [
        IsAuthorAdminOrModeratorPermission,
        IsAuthenticatedOrReadOnly
    ]

    def _get_review(self):
        return get_object_or_404(Review, id=self.kwargs['review_id'])

    def perform_create(self, serializer):
        review = self._get_review()
        serializer.save(author=self.request.user, review=review)

    def get_queryset(self):
        review = self._get_review()
        return review.comments.all()


class APIGetConfirmationCode(APIView):
    """
    Регистрация нового пользователя
    Получить код подтверждения на переданный email
    Использовать имя 'me' в качестве username запрещено.
    """

    def post(self, request):
        serializer = SingUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.data['username']
        email = serializer.data['email']
        user, _created = CustomUser.objects.get_or_create(
            username=username, email=email
        )

        try:
            send_mail(
                settings.DEFAULT_FROM_SUBJECT,
                f'code: {default_token_generator.make_token(user=user)}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email, ]
            )
        except BadHeaderError:
            Response(
                {'error': 'failed to send message.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class APIGetToken(APIView):
    """
    Получение JWT-токена в обмен на username и confirmation code.
    """

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        user = get_object_or_404(
            CustomUser, username=serializer.validated_data.get('username'))
        if default_token_generator.check_token(
                user, serializer.validated_data.get(
                    'confirmation_code'
                )
        ):
            token = AccessToken.for_user(user)
            return Response(
                {'token': f'{token}'},
                status=status.HTTP_200_OK
            )
        return Response(
            {'confirmation_code': 'incorrect'},
            status=status.HTTP_400_BAD_REQUEST
        )
