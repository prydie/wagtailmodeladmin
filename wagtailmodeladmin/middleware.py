from django.utils.six.moves.urllib.parse import urlparse
from django.http import HttpResponseRedirect
from django.core.urlresolvers import resolve, reverse, Resolver404


class ModelAdminMiddleware(object):
    """
    Whenever loading wagtail's wagtailadmin_explore url, we check the session
    for a `return_to_list_url` value (set by some views), to see if the user
    should be redirected to a custom list view instead, and if so, redirect
    them to it.
    """

    def process_request(self, request):
        """
        Ignore unnecessary actions for static file requests, posts, or ajax
        requests. We're only interested in redirecting following a 'natural'
        request redirection to the `wagtailadmin_explore_root` or
        `wagtailadmin_explore` views.
        """
        referer_url = request.META.get('HTTP_REFERER')
        return_to_index_url = request.session.get('return_to_index_url')

        if all((
            return_to_index_url,
            referer_url,
            request.method == 'GET',
            not request.is_ajax(),
            request.path.startswith(reverse('wagtailadmin_explore_root')),
        )):
            try:
                perform_redirection = False
                referer_match = resolve(urlparse(referer_url).path)
                if all((
                    referer_match.namespace == 'wagtailadmin_pages',
                    referer_match.url_name in (
                        'add',
                        'edit',
                        'delete',
                        'unpublish',
                        'copy'
                    ),
                )):
                    perform_redirection = True
                elif all((
                    not referer_match.namespace,
                    referer_match.url_name in (
                        'wagtailadmin_pages_create',
                        'wagtailadmin_pages_edit',
                        'wagtailadmin_pages_delete',
                        'wagtailadmin_pages_unpublish'
                    ),
                )):
                    perform_redirection = True
                if perform_redirection:
                    del request.session['return_to_index_url']
                    return HttpResponseRedirect(return_to_index_url)

            except Resolver404:
                pass

        return None
