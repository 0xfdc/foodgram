from rest_framework import mixins, viewsets


class TagsIngridientsMixViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    pass
