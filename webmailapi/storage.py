import copy
from apibase.baseapp import BaseController, api
from lib.imap import ImapStorage

class Storage(BaseController):

    @api
    def get_message(self, mid):
        imap = ImapStorage(self.config, self.request.POST)
        return {
            'result': imap.get_message(mid),
            'error': None
        }


    @api
    def list_messages(self, name):
        data = {'folder': name}
        data.update(self.request.POST)
        imap = ImapStorage(self.config, data)
        return {
            'result': imap.list_messages(),
            'error': None
        }

    @api
    def list_folders(self):
        imap = ImapStorage(self.config, self.request.POST)
        f = imap.list_folders()
        return {
            'result': f,
            'error': None
        }

    @api
    def send_message(self):
        raise Exception("FAIL WHALE")


