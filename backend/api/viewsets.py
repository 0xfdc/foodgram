from rest_framework import mixins, viewsets


class TagsIngredientsMixViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    pass


class ListViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    pass
