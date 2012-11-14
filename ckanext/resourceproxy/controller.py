import urllib2
import shutil
from logging import getLogger

from pylons.controllers.util import abort as abort

import ckan.logic as logic
import ckan.lib.base as base

log = getLogger(__name__)


@logic.side_effect_free
def proxy_resource(context, data_dict):
        resource_id = data_dict['resource_id']
        log.info('Proxify resource {id}'.format(id=resource_id))
        resource = logic.get_action('resource_show')(context, {'id': resource_id})
        url = resource['url']
        had_http_error = False
        try:
            res = urllib2.urlopen(url)
        except urllib2.HTTPError, error:
            res = error
            had_http_error = True
        except urllib2.URLError, error:
            details = "Could not proxy resource. " + str(error.reason)
            abort(500, detail=details)
        base.response.headers = res.headers

        shutil.copyfileobj(res, base.response)

        if had_http_error and hasattr(res, 'code'):
            abort(res.code)


class ProxyController(base.BaseController):
    def proxy_resource(self, resource_id):
        data_dict = {'resource_id': resource_id}
        context = {'model': base.model, 'session': base.model.Session,
                   'user': base.c.user or base.c.author}
        return proxy_resource(context, data_dict)