from django_filters import FilterSet, CharFilter, NumberFilter

from reviews.models import Title


class TitleFilterSet(FilterSet):
    category = CharFilter(field_name='category__slug')
    genre = CharFilter(field_name='genre__slug')
    name = CharFilter(field_name='name', lookup_expr='icontains')
    year = NumberFilter(field_name='year')

    class Meta:
        model = Title
        fields = ('id', 'category', 'genre', 'name', 'year')
