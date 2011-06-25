import copy
from apibase.baseapp import BaseController, api
from apibase.schema import api_entry, api_param, api_validate
from lib.imap import ImapStorage

class Storage(BaseController):

    @api
    @api_validate
    @api_entry(
        description="get a list of messages in a folder",
        parameters={
            'mid': api_param('string', True, None, None, 'path', 'Message ID for message to retreive'),
            'username': api_param('string', True, None, None, 'query', 'User to login as'),
            'password': api_param('string', True, None, None, 'query', 'Users password'),
        },
        response={'type': 'array',
                  'description': ('list of message headers (array of strings)')})
    def get_message(self, mid):
        imap = ImapStorage(self.config, self.request.POST)
        return {
            'result': imap.get_message(mid),
            'error': None
        }


    @api
    @api_validate
    @api_entry(
        description="get a list of messages in a folder",
        parameters={
            'name': api_param('string', True, None, None, 'path', 'Folder to get a list from'),
            'username': api_param('string', True, None, None, 'query', 'User to login as'),
            'password': api_param('string', True, None, None, 'query', 'Users password'),
        },
        response={'type': 'array',
                  'description': ('list of message headers')})
    def list_messages(self, name):
        data = {'folder': name}
        data.update(self.request.POST)
        print data
        imap = ImapStorage(self.config, data)
        return {
            'result': imap.list_messages(),
            'error': None
        }

    @api
    @api_validate
    @api_entry(
        description="get a list of messages in a folder",
        parameters={
            'username': api_param('string', True, None, None, 'query', 'User to login as'),
            'password': api_param('string', True, None, None, 'query', 'Users password'),
        },
        response={'type': 'array',
                  'description': ('list of folders')})
    def list_folders(self):
        imap = ImapStorage(self.config, self.request.POST)
        f = imap.list_folders()
        return {
            'result': f,
            'error': None
        }

    @api
    @api_validate
    @api_entry(description="NOT IMPLEMENTED")
    def send_message(self):
        raise Exception("FAIL WHALE")


