
from apibase.baseapp import *
from routes import Mapper
from storage import Storage

map = Mapper()

map.connect('message', '/message/{mid}', controller=Storage, action='get_message');
map.connect('message_list', '/folder/{name}', controller=Storage, action='list_messages');
map.connect('folder_list', '/folder', controller=Storage, action='list_folders');
map.connect('message_send', '/send', controller=Storage, action='send_message');

make_app = set_app(map)
