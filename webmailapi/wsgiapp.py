
from apibase.baseapp import *
from apibase.schema import APIDescription, api_entry, api_param, api_validate, generateSchema
from routes import Mapper
from webob.dec import wsgify

from storage import Storage

@api_entry(
    name='webmailapi',
    version='v1',
    description="A REST to IMAP proxy API",
    title="WebMailAPI",
    labels=['labs'],
    icons={'x16': 'https://mozillalabs.com/wp-content/themes/labs2.0/favicon.png'}
)
class WebMailAPI(BaseApplication):
    schema = None
    @wsgify
    def __call__(self, req):
        if not self.schema:
            generateSchema(self, req)
        return super(WebMailAPI, self).__call__(req)

map = Mapper()
with map.submapper(path_prefix='/v1') as v1:
    v1.connect('message', '/message/{mid}', controller=Storage, action='get_message', conditions=dict(method=["POST"]));
    v1.connect('message_list', '/folder/{name}', controller=Storage, action='list_messages', conditions=dict(method=["POST"]));
    v1.connect('folder_list', '/folder', controller=Storage, action='list_folders', conditions=dict(method=["POST"]));
    v1.connect('message_send', '/send', controller=Storage, action='send_message', conditions=dict(method=["POST"]));

map.connect('message', '/message/{mid}', controller=Storage, action='get_message');
map.connect('message_list', '/folder/{name}', controller=Storage, action='list_messages');
map.connect('folder_list', '/folder', controller=Storage, action='list_folders');
map.connect('message_send', '/send', controller=Storage, action='send_message');

map.connect('/schema', controller=APIDescription, action='schema')

make_app = set_app(map, appKlass=WebMailAPI)
