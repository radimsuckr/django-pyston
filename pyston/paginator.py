from django.utils.translation import ugettext
from django.db.models.query import QuerySet

from .exception import RESTException


class BasePaginator:

    @property
    def page_qs(self):
        raise NotImplementedError

    @property
    def headers(self):
        return {}


class Paginator(BasePaginator):
    """
    REST paginator for list and querysets
    """

    MAX_BIG_INT = pow(2, 63) - 1

    def __init__(self, qs, request):
        self.qs = qs
        self.offset = self._get_offset(request)
        self.base = self._get_base(request)
        self.total = self._get_total()

    def _get_total(self):
        if isinstance(self.qs, QuerySet):
            return self.qs.count()
        else:
            return len(self.qs)

    def _get_offset(self, request):
        offset = request._rest_context.get('offset', '0')
        if offset.isdigit():
            offset_int = int(offset)
            if offset_int > self.MAX_BIG_INT:
                raise RESTException(ugettext('Offset must be lower or equal to {}').format(self.MAX_BIG_INT))
            else:
                return offset_int
        else:
            raise RESTException(ugettext('Offset must be natural number'))

    def _get_base(self, request):
        base = request._rest_context.get('base')
        if not base:
            return None
        elif base.isdigit():
            base_int = int(base)
            if base_int > self.MAX_BIG_INT:
                raise RESTException(ugettext('Base must lower or equal to {}').format(self.MAX_BIG_INT))
            else:
                return base_int
        else:
            raise RESTException(ugettext('Base must be natural number or empty'))

    @property
    def page_qs(self):
        if self.base is not None:
            return self.qs[self.offset:(self.offset + self.base)]
        else:
            return self.qs[self.offset:]

    @property
    def headers(self):
        return {'X-Total': self.total}
