import re
from imapclient import IMAPClient
from paste.deploy.converters import asbool
from email.parser import HeaderParser, Parser as MessageParser
from email.header import decode_header
from email.utils import parseaddr

class ImapStorage(object):

    _MESSAGES_NEW = 1
    _MESSAGES_MORE = 2
    _MESSAGES_REFRESH = 3
    _PAGE_SIZE = 25

    def __init__(self, config, data):
        folder = data.get('folder', 'INBOX')
        username = data.get('username', config.get('mail.username', ''))
        password = data.get('password', config.get('mail.password', ''))

        self.connect(config, folder, username, password)

    def connect(self, config, mailbox, username, password):
        self.mailbox = mailbox
        self.server = IMAPClient(config.get('mail.host'),
                                 use_uid=asbool(config.get('mail.uid', True)),
                                 ssl=asbool(config.get('mail.ssl', True)))
        self.server.login(username, password)
        self.server.select_folder(mailbox)
    
    def close(self):
        self.server.logout()

    def list_folders(self):
        l = self.server.list_folders()
        return [f[-1] for f in l]

    def _decodeMimeStr(self, str, charset="UTF-8" ):
        newString = u''
        elements=decode_header(str)
        for t, c in elements:
            if c == 'default':
                c = 'iso-8859-1'
            newString += unicode(t, c or charset)
        return newString

    def _decode_headers(self, headers):
        msg = {}
        #echo json_encode(headers)
        for k, v in headers.items():
            k = k.lower()
            if isinstance(v, str):
                u = self._decodeMimeStr(v)
                #u = imap_utf8(v)
            #echo "k [v].[u]\n"
                if u:
                    msg[k] = u
                else:
                    msg[k] = v
            elif isinstance(v, tuple):
                msg[k] = [self._decodeMimeStr(v) for v in v]
            elif isinstance(v, (int, unicode)):
                msg[k] = v
            else:
                msg[k] = self._decode_headers(v)
            #echo k." --. ". json_encode(msg[k])."\n"
        
        return msg

    def _parse_address(self, addr):
        paddr = parseaddr(addr)
        return {
            "personal": paddr[0],
            "mailbox": paddr[1] and paddr[1].split('@')[0] or None,
            "host": paddr[1] and paddr[1].split('@')[1] or None
        }
    _newline = re.compile('\r\n?|\s+', re.U)
    def _parse_msg_headers(self, uid, msg):
        
        headers = self._decode_headers(msg)
        for addrh in ['to', 'cc', 'bcc']:
            if headers.get(addrh):
                headers['%saddress' % addrh] = self._newline.subn(' ', headers[addrh])[0]
                headers[addrh] = [a.strip() for a in headers[addrh].split(',')] 
                headers[addrh] = [self._parse_address(a) for a in headers[addrh]] 
        
        if headers.get('from'):
            headers['fromaddress'] = headers['from']
            headers['from'] = [self._parse_address(headers['from'])]

        return headers

    def list_messages(self, start=0, num_msgs=25, flags=0, search=None):
        boxinfo = self.server.select_folder(self.mailbox)
        r = boxinfo
        
        if num_msgs == 0:
            num_msgs = self.PAGE_SIZE; #boxinfo.Nmsgs
        
        criteria = ["NOT UNDELETED"]
        if search:
            criteria.append('TEXT "search"')

        sorted_mbox = set(self.server.sort(['ARRIVAL']))
        found = set(self.server.search(['NOT DELETED']))
        found_sorted = list(sorted_mbox.intersection(found))
        msgs = found_sorted[start:start+num_msgs]
        
        r['mailbox'] = self.mailbox
        r['entries'] = []

        ml = {}
        entries = self.server.fetch(msgs, ['FLAGS','RFC822.SIZE','RFC822.HEADER'])
        for uid,e in entries.items():
            msg = HeaderParser().parsestr(e['RFC822.HEADER'])
            msg['uid'] = uid
            msg['size'] = e['RFC822.SIZE']
            msg['flags'] = e.get('FLAGS')
            msg['seen'] = '\\Seen' in msg['flags']
            msg['flagged'] = '\\Flagged' in msg['flags']
            msg['deleted'] = '\\Deleted' in msg['flags']
            msg['draft'] = '\\Draft' in msg['flags']
            msg['answered'] = '\\Answered' in msg['flags']
            ml[uid] = self._parse_msg_headers(uid, msg)
        
        for msgno in msgs:
            r['entries'].append(ml[msgno])
        return r

    def get_message(self, msguid):
        # input mbox = IMAP stream, mid = message id
        # output all the following:
        # the message may in htmlmsg, plainmsg, or both
        data = self.server.fetch([msguid], ['RFC822'])
        msg_data = data[int(msguid)]
        message = MessageParser().parsestr(msg_data['RFC822'])
        msg = {}
        msg['headers'] = self._parse_msg_headers(msguid, message)
        msg['uid'] = msguid
        msg['parts'] = parts = []
        default_charset = 'utf-8'
        for p in message.walk():
            if p.is_multipart():
                default_charset = p.get_content_charset() or default_charset
                continue
            part = {}
            charset = p.get_content_charset() or default_charset
            type = p.get_content_maintype()
            part['type'] = type
            part['subtype'] = p.get_content_subtype()
            if type == 'text':
                part['charset'] = charset
                part['body'] = unicode(p.get_payload(decode=True), charset)
            parts.append(part)
        return msg

    def send_message():
        fullname = request.POST['fullname']
        to = request.POST['to']
        from_ = request.POST['email']
        subject = request.POST['subject']
        message = request.POST['message']
        
        if fullname:
            address = "\"fullname\" <from>"
        else:
            address = from_

        headers = "From: address\r\nReply-To: address"

        if mail(to, subject, message, headers):
            return "ok"

        raise Exception("sending email failed")

