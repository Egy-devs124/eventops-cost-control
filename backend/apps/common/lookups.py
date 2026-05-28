from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.constants import ALL_ROLES
from apps.common.permissions import RoleScopedPermission


class LookupView(APIView):
    permission_classes = [RoleScopedPermission]
    allowed_roles = ALL_ROLES
    model = None
    search_fields = ("name",)
    limit = 50

    def get_queryset(self):
        return self.model.objects.all()

    def get_label(self, obj):
        return getattr(obj, "name", str(obj))

    def get(self, request):
        query = (request.query_params.get("search") or "").strip()
        qs = self.get_queryset()
        if query:
            from django.db.models import Q

            condition = Q()
            for field in self.search_fields:
                condition |= Q(**{f"{field}__icontains": query})
            qs = qs.filter(condition)
        data = [
            {"id": obj.pk, "value": obj.pk, "label": self.get_label(obj)}
            for obj in qs[: self.limit]
        ]
        return Response(data)


def lookup_view(model, label_func=None, search_fields=("name",), queryset_func=None):
    class ConcreteLookupView(LookupView):
        pass

    ConcreteLookupView.model = model
    ConcreteLookupView.search_fields = search_fields
    if label_func:
        ConcreteLookupView.get_label = staticmethod(label_func)
    if queryset_func:
        ConcreteLookupView.get_queryset = lambda self: queryset_func()
    return ConcreteLookupView.as_view()
