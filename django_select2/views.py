import json

from django.http import HttpResponse
from django.views.generic import View
from django.core.exceptions import PermissionDenied
from django.http import Http404

from utils import get_field, is_valid_id

NO_ERR_RESP = 'nil'
"""
Equals to 'nil' constant.

Use this in :py:meth:`.Select2View.get_results` to mean no error, instead of hardcoding 'nil' value.
"""

class JSONResponseMixin(object):
    """
    A mixin that can be used to render a JSON response.
    """
    response_class = HttpResponse

    def render_to_response(self, context, **response_kwargs):
        """
        Returns a JSON response, transforming 'context' to make the payload.
        """
        response_kwargs['content_type'] = 'application/json'
        return self.response_class(
            self.convert_context_to_json(context),
            **response_kwargs
        )

    def convert_context_to_json(self, context):
        "Convert the context dictionary into a JSON object"
        return json.dumps(context)

class Select2View(JSONResponseMixin, View):
    """
    Base view designed to respond with JSON to Ajax queries from heavy widgets/fields.

    Although the widgets won't enforce the type of data_view it gets,
    it is recommended to sub-class this view instead of creating a Django view from scratch.

    This view takes care of pagination and return a json in the format:

        {
            results: [list],
            err: 'error message',
            more: 'more results available in other pages',
            page: 'current page',
        }

    .. note:: Only `GET <http://www.w3.org/Protocols/rfc2616/rfc2616-sec9.html#sec9.3>`_ Http requests are supported.
    """
    PAGE_SIZE = 100     # default number of results per page
    skip_empty = False  # by default, perform a search even when no key is specified
                        # - since select2 is paginated, this is a sensible default imho

    def __init__(self, skip_empty=False):
        self.skip_empty = skip_empty

    def dispatch(self, request, *args, **kwargs):
        try:
            self.check_all_permissions(request, *args, **kwargs)
        except Exception as e:
            print "Exception:", e, e.__dict__
            return self.respond_with_exception(e)
        return super(Select2View, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if request.method == 'GET':
            term = request.GET.get('term', request.GET.get('q', None))
            page_size = int(request.GET.get('max', request.GET.get('page_size', self.PAGE_SIZE)))
            if self.skip_empty:
                if term is None:
                    return self.render_to_response(self._results_to_context('missing term'))
                if not term:
                    return self.render_to_response(self._results_to_context(NO_ERR_RESP, False, [], ))
            try:
                page = int(request.GET.get('page', None))
                if page <= 0:
                    page = -1
            except TypeError:
                # if there's no page, let start from page 1
                page = 1
            except ValueError:
                page = -1
            if page == -1:
                return self.render_to_response(self._results_to_context('bad page no.'))
            context = request.GET.get('context', None)
        else:
            return self.render_to_response(self._results_to_context('not a get request'))

        return self.render_to_response(
            self._results_to_context(
                *self.get_results(request, term, page, context, page_size), page = page  # netbeans does not like it, but it's legal python
                )
            )

    def respond_with_exception(self, e):
        """
        :param e: Exception object.
        :type e: Exception
        :return: Response with status code of 404 if e is ``Http404`` object,
            else 400.
        :rtype: HttpResponse
        """
        msg = str(e)
        if isinstance(e, Http404):
            status = 404
            msg = msg or "Not Found"
        elif isinstance(e, PermissionDenied):
            status = 403
            msg = msg or "Permission Denied"
        else:
            status = getattr(e, 'status_code', 400)
        return self.render_to_response(
#            self._results_to_context(str(e)),  # looks like there's no message in the exception!
            self._results_to_context(msg),
            status=status
            )

    def _results_to_context(self, err, has_more=False, results=[], page=None):

        if err != NO_ERR_RESP:
            results = locals().copy()
            del results['self']
            return results

        res = []

        for result in results:
            id_, text = result[:2]
            if len(result)>2:
                extra_data = result[2]
            else:
                extra_data = {}
            res.append(dict(id=id_, text=text, **extra_data))
        return {
            'err': err,
            'more': has_more,
            'results': res,
            'page': page,
        }

    def check_all_permissions(self, request, *args, **kwargs):
        """
        Sub-classes can use this to raise exception on permission check failures,
        or these checks can be placed in ``urls.py``, e.g. ``login_required(SelectClass.as_view())``.

        :param request: The Ajax request object.
        :type request: :py:class:`django.http.HttpRequest`

        :param args: The ``*args`` passed to :py:meth:`django.views.generic.View.dispatch`.
        :param kwargs: The ``**kwargs`` passed to :py:meth:`django.views.generic.View.dispatch`.

        .. warning:: Sub-classes should override this. You really do not want random people making
            Http reqeusts to your server, be able to get access to sensitive information.
        """
        pass

    def get_results(self, request, term, page, context, page_size):
        """
        Returns the result for the given search ``term``.

        :param request: The Ajax request object.
        :type request: :py:class:`django.http.HttpRequest`

        :param term: The search term.
        :type term: :py:obj:`str`

        :param page: The page number. If in your last response you had signalled that there are more results,
            then when user scrolls more a new Ajax request would be sent for the same term but with next page
            number. (Page number starts at 1)
        :type page: :py:obj:`int`

        :param context: Can be anything which persists across the lifecycle of queries for the same search term.
            It is reset to ``None`` when the term changes.

            .. note:: Currently this is not used by ``heavy_data.js``.
        :type context: :py:obj:`str` or None

        Expected output is of the form::

            (err, has_more, [results])

        Where ``results = [(id1, text1), (id2, text2), ...]``

        For example::

            ('nil', False,
                [
                (1, 'Value label1'),
                (20, 'Value label2'),
                ])

        When everything is fine then the `err` must be 'nil'.
        `has_more` should be true if there are more rows.
        """
        raise NotImplementedError


class AutoResponseView(Select2View):
    """
    A central view meant to respond to Ajax queries for all Heavy widgets/fields.
    Although it is not mandatory to use, but is immensely helpful.

    .. tip:: Fields which want to use this view must sub-class :py:class:`~.widgets.AutoViewFieldMixin`.
    """
    def check_all_permissions(self, request, *args, **kwargs):
        id_ = request.GET.get('field_id', None)
        if id_ is None or not is_valid_id(id_):
            raise Http404('field_id not found or is invalid')
        field = get_field(id_)
        if field is None:
            raise Http404('field_id not found')

        if not field.security_check(request, *args, **kwargs):
            raise PermissionDenied('permission denied')

        request.__django_select2_local = field

    def get_results(self, request, term, page, context):
        field = request.__django_select2_local
        del request.__django_select2_local
        return field.get_results(request, term, page, context)


