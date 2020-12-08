__all__ = [
    "CobaltStrikeCampaignsContentHandler",
    "CobaltStrikeTokensContentHandler",
    "CobaltStrikeSentEmailsContentHandler",
    "CobaltStrikeWebHitsContentHandler",
    "CobaltStrikeApplicationsContentHandler",
]

from xml.sax import ContentHandler, parse, SAXNotRecognizedException
from xml.parsers.expat import ExpatError
from pca.util import copy_attrs
import datetime
import hashlib
import ipaddress


class CobaltStrikeCampaignsContentHandler(ContentHandler):
    def __init__(self, campaign_callback, end_callback):
        ContentHandler.__init__(self)
        self.campaign_callback = campaign_callback
        self.end_callback = end_callback
        self.is_campaignsFile = False
        self.currentCampaign = None
        self.chars = ""

    def startElement(self, name, attrs):
        # clear characters buffer
        self.chars = ""
        if not self.is_campaignsFile:
            if name == "campaigns":
                self.is_campaignsFile = True
            else:
                raise SAXNotRecognizedException(
                    "XML does not look like Cobalt Strike campaigns.xml data."
                )
        elif name == "entry":
            self.currentCampaign = dict()

    def endElement(self, name):
        if name == "entry":
            self.campaign_callback(self.currentCampaign)
        elif name == "cid":
            self.currentCampaign["_id"] = self.chars
        elif name == "when":
            self.currentCampaign["start_time"] = datetime.datetime.utcfromtimestamp(
                int(self.chars) / 1000.0
            )
        elif name == "url":
            self.currentCampaign["url"] = self.chars
        # We now ignore the template name that Cobalt Strike provides; instead we use the data in TemplateDoc
        # elif name == 'template':
        elif name == "subject":
            self.currentCampaign["subject"] = self.chars
        elif name == "campaigns":
            self.end_callback()

    def characters(self, content):
        self.chars += content


class CobaltStrikeTokensContentHandler(ContentHandler):
    def __init__(self, token_callback, end_callback):
        ContentHandler.__init__(self)
        self.token_callback = token_callback
        self.end_callback = end_callback
        self.is_tokensFile = False
        self.currentToken = None
        self.chars = ""

    def startElement(self, name, attrs):
        # clear characters buffer
        self.chars = ""
        if not self.is_tokensFile:
            if name == "tokens":
                self.is_tokensFile = True
            else:
                raise SAXNotRecognizedException(
                    "XML does not look like Cobalt Strike tokens.xml data."
                )
        elif name == "entry":
            self.currentToken = dict()

    def endElement(self, name):
        if name == "entry":
            self.token_callback(self.currentToken)
        elif name == "token":
            self.currentToken["token"] = self.chars
        elif name == "email":
            self.currentToken["email_hash"] = hashlib.sha256(
                (self.chars).encode("utf-8")
            ).hexdigest()
        elif name == "cid":
            self.currentToken["campaign"] = self.chars
        elif name == "tokens":
            self.end_callback()

    def characters(self, content):
        self.chars += content


class CobaltStrikeSentEmailsContentHandler(ContentHandler):
    def __init__(self, email_callback, end_callback):
        ContentHandler.__init__(self)
        self.email_callback = email_callback
        self.end_callback = end_callback
        self.is_sentemailsFile = False
        self.currentEmail = None
        self.chars = ""

    def startElement(self, name, attrs):
        # clear characters buffer
        self.chars = ""
        if not self.is_sentemailsFile:
            if name == "sentemails":
                self.is_sentemailsFile = True
            else:
                raise SAXNotRecognizedException(
                    "XML does not look like Cobalt Strike sentemails.xml data."
                )
        elif name == "entry":
            self.currentEmail = dict()

    def endElement(self, name):
        if name == "entry":
            self.email_callback(self.currentEmail)
        elif name == "token":
            self.currentEmail["token"] = self.chars
        elif name == "cid":
            self.currentEmail["campaign"] = self.chars
        elif name == "when":
            self.currentEmail["time"] = datetime.datetime.utcfromtimestamp(
                int(self.chars) / 1000.0
            )
        elif name == "status":
            self.currentEmail["status"] = self.chars
        elif name == "sentemails":
            self.end_callback()

    def characters(self, content):
        self.chars += content


class CobaltStrikeWebHitsContentHandler(ContentHandler):
    def __init__(self, webhits_callback, end_callback):
        ContentHandler.__init__(self)
        self.webhits_callback = webhits_callback
        self.end_callback = end_callback
        self.is_webhitsFile = False
        self.currentWebhit = None
        self.chars = ""

    def startElement(self, name, attrs):
        # clear characters buffer
        self.chars = ""
        if not self.is_webhitsFile:
            if name == "webhits":
                self.is_webhitsFile = True
            else:
                raise SAXNotRecognizedException(
                    "XML does not look like Cobalt Strike webhits.xml data."
                )
        elif name == "entry":
            self.currentWebhit = dict()

    def endElement(self, name):
        if name == "entry":
            self.webhits_callback(self.currentWebhit)
        elif name == "token":
            self.currentWebhit["token"] = self.chars
        elif name == "when":
            self.currentWebhit["time"] = datetime.datetime.utcfromtimestamp(
                int(self.chars) / 1000.0
            )
        elif name == "data":
            # Currently expects source_ip to be last item in data
            # TODO make searching for source_ip more bulletproof (regex?)
            self.currentWebhit["source_ip"] = self.chars.split(" ")[-1]
        elif name == "webhits":
            self.end_callback()

    def characters(self, content):
        self.chars += content


class CobaltStrikeApplicationsContentHandler(ContentHandler):
    def __init__(self, applications_callback, end_callback):
        ContentHandler.__init__(self)
        self.applications_callback = applications_callback
        self.end_callback = end_callback
        self.is_applicationsFile = False
        self.currentApplication = None
        self.chars = ""

    def startElement(self, name, attrs):
        # clear characters buffer
        self.chars = ""
        if not self.is_applicationsFile:
            if name == "applications":
                self.is_applicationsFile = True
            else:
                raise SAXNotRecognizedException(
                    "XML does not look like Cobalt Strike applications.xml data."
                )
        elif name == "entry":
            self.currentApplication = dict()

    def endElement(self, name):
        if name == "entry":
            self.applications_callback(self.currentApplication)
        elif name == "id":
            self.currentApplication["token"] = self.chars
        elif name == "date":
            self.currentApplication["time"] = datetime.datetime.utcfromtimestamp(
                int(self.chars) / 1000.0
            )
        elif name == "application":
            self.currentApplication["name"] = self.chars
        elif name == "version":
            self.currentApplication["version"] = self.chars
        elif name == "external":
            self.currentApplication["external_ip"] = self.chars
        elif name == "internal":
            try:  # internal_ip is not guaranteed to be present or may be 'unknown'/'null'
                internal_ip = ipaddress.ip_address(self.chars)
                self.currentApplication["internal_ip"] = self.chars
            except:
                self.currentApplication["internal_ip"] = None
        elif name == "applications":
            self.end_callback()

    def characters(self, content):
        self.chars += content
