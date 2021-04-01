#!/usr/bin/env py.test -vs

import os
import sys

me = os.path.realpath(__file__)
myDir = os.path.dirname(me)
sys.path.append(os.path.join(myDir, ".."))

import pytest
from pca.util import util
from pca.handlers.cobaltstrike_handler import *
from xml.sax import parse
import datetime

TEST_CS_CAMPAIGNS_FILENAME = "test_XMLData/campaigns.xml"
TEST_CS_TOKENS_FILENAME = "test_XMLData/tokens.xml"
TEST_CS_SENT_EMAILS_FILENAME = "test_XMLData/sentemails.xml"
TEST_CS_WEB_HITS_FILENAME = "test_XMLData/webhits.xml"
TEST_CS_APPLICATIONS_FILENAME = "test_XMLData/applications.xml"


def pytest_runtest_makereport(item, call):
    if "incremental" in item.keywords:
        if call.excinfo is not None:
            parent = item.parent
            parent._previousfailed = item


def pytest_runtest_setup(item):
    if "incremental" in item.keywords:
        previousfailed = getattr(item.parent, "_previousfailed", None)
        if previousfailed is not None:
            pytest.xfail("previous test failed (%s)" % previousfailed.name)


class YourMom(object):
    """You should call back your Mom.  This test does."""

    def __init__(self):
        self.elements = []
        self.end_callback_call_count = 0

    def element_callback(self, parsed_element):
        # print 'X' * 80            # Enable these lines for visibility into each parsed element
        # util.pp(parsed_element)   # Enable these lines for visibility into each parsed element
        self.elements.append(parsed_element)

    def end_callback(self):
        self.end_callback_call_count += 1


@pytest.fixture(scope="session")
def your_moms_campaigns():
    return YourMom()


@pytest.mark.incremental
class TestCSCampaignsHandler:
    def test_parse(self, your_moms_campaigns):
        # py.test doesn't allow __init__
        handler = CobaltStrikeCampaignsContentHandler(
            your_moms_campaigns.element_callback, your_moms_campaigns.end_callback
        )
        f = open(TEST_CS_CAMPAIGNS_FILENAME, "rb")
        parse(f, handler)
        f.close()

    def test_correct_number_of_end_callbacks(self, your_moms_campaigns):
        assert (
            your_moms_campaigns.end_callback_call_count == 1
        ), "unexpected number of end callbacks"

    def test_correct_number_of_elements(self, your_moms_campaigns):
        assert (
            len(your_moms_campaigns.elements) == 1
        ), "unexpected number of campaigns parsed"

    def test_first_element_data_check(self, your_moms_campaigns):
        assert (
            your_moms_campaigns.elements[0]["_id"]
            == "28fc34fa-51be-4518-a7be-656cbdf01ae7"
        ), "unexpected campaign_id for campaign 0"
        assert your_moms_campaigns.elements[0][
            "start_time"
        ] == datetime.datetime.utcfromtimestamp(
            1472066003992 / 1000.0
        ), "unexpected time for campaign 0"
        assert (
            your_moms_campaigns.elements[0]["url"]
            == "http://webmail.securitydept.org/joboffer/?id=%TOKEN%"
        ), "unexpected url for campaign 0"
        assert (
            your_moms_campaigns.elements[0]["subject"] == "Vacancy Job Offer For You!!"
        )


@pytest.fixture(scope="session")
def your_moms_tokens():
    return YourMom()


@pytest.mark.incremental
class TestCSTokensHandler:
    def test_parse(self, your_moms_tokens):
        # py.test doesn't allow __init__
        handler = CobaltStrikeTokensContentHandler(
            your_moms_tokens.element_callback, your_moms_tokens.end_callback
        )
        f = open(TEST_CS_TOKENS_FILENAME, "rb")
        parse(f, handler)
        f.close()

    def test_correct_number_of_end_callbacks(self, your_moms_tokens):
        assert (
            your_moms_tokens.end_callback_call_count == 1
        ), "unexpected number of end callbacks"

    def test_correct_number_of_elements(self, your_moms_tokens):
        assert (
            len(your_moms_tokens.elements) == 61
        ), "unexpected number of tokens parsed"

    def test_first_element_data_check(self, your_moms_tokens):
        assert (
            your_moms_tokens.elements[0]["campaign"]
            == "28fc34fa-51be-4518-a7be-656cbdf01ae7"
        ), "unexpected campaign for token 0"
        assert (
            your_moms_tokens.elements[0]["email_hash"]
            == "48868cd21562c70ae1087618e1de1bc5978089eb3500fea2e48852fb9e1f8feb"
        ), "unexpected email_hash for token 0"
        assert (
            your_moms_tokens.elements[0]["token"] == "04ea957ec11c"
        ), "unexpected token for token 0"


@pytest.fixture(scope="session")
def your_moms_emails():
    return YourMom()


@pytest.mark.incremental
class TestCSSentEmailsHandler:
    def test_parse(self, your_moms_emails):
        # py.test doesn't allow __init__
        handler = CobaltStrikeSentEmailsContentHandler(
            your_moms_emails.element_callback, your_moms_emails.end_callback
        )
        f = open(TEST_CS_SENT_EMAILS_FILENAME, "rb")
        parse(f, handler)
        f.close()

    def test_correct_number_of_end_callbacks(self, your_moms_emails):
        assert (
            your_moms_emails.end_callback_call_count == 1
        ), "unexpected number of end callbacks"

    def test_correct_number_of_elements(self, your_moms_emails):
        assert (
            len(your_moms_emails.elements) == 61
        ), "unexpected number of emails parsed"

    def test_first_element_data_check(self, your_moms_emails):
        assert (
            your_moms_emails.elements[0]["token"] == "25b0f8b5407f"
        ), "unexpected token for email 0"
        assert (
            your_moms_emails.elements[0]["campaign"]
            == "28fc34fa-51be-4518-a7be-656cbdf01ae7"
        ), "unexpected campaign_id for email 0"
        assert your_moms_emails.elements[0][
            "time"
        ] == datetime.datetime.utcfromtimestamp(
            1472066004428 / 1000.0
        ), "unexpected time for email 0"
        assert (
            your_moms_emails.elements[0]["status"] == "SUCCESS"
        ), "unexpected status for email 0"


@pytest.fixture(scope="session")
def your_moms_webhits():
    return YourMom()


@pytest.mark.incremental
class TestCSSWebhitsHandler:
    def test_parse(self, your_moms_webhits):
        # py.test doesn't allow __init__
        handler = CobaltStrikeWebHitsContentHandler(
            your_moms_webhits.element_callback, your_moms_webhits.end_callback
        )
        f = open(TEST_CS_WEB_HITS_FILENAME, "rb")
        parse(f, handler)
        f.close()

    def test_correct_number_of_end_callbacks(self, your_moms_webhits):
        assert (
            your_moms_webhits.end_callback_call_count == 1
        ), "unexpected number of end callbacks"

    def test_correct_number_of_elements(self, your_moms_webhits):
        assert (
            len(your_moms_webhits.elements) == 82
        ), "unexpected number of webhits parsed"

    def test_first_element_data_check(self, your_moms_webhits):
        assert your_moms_webhits.elements[0][
            "time"
        ] == datetime.datetime.utcfromtimestamp(
            1472066882463 / 1000.0
        ), "unexpected time for webhit 0"
        assert (
            your_moms_webhits.elements[0]["token"] == "71a6710a43d8"
        ), "unexpected token for webhit 0"
        assert (
            your_moms_webhits.elements[0]["source_ip"] == "192.168.195.201"
        ), "unexpected source_ip for webhit 0"


@pytest.fixture(scope="session")
def your_moms_applications():
    return YourMom()


@pytest.mark.incremental
class TestCSSApplicationsHandler:
    def test_parse(self, your_moms_applications):
        # py.test doesn't allow __init__
        handler = CobaltStrikeApplicationsContentHandler(
            your_moms_applications.element_callback, your_moms_applications.end_callback
        )
        f = open(TEST_CS_APPLICATIONS_FILENAME, "rb")
        parse(f, handler)
        f.close()

    def test_correct_number_of_end_callbacks(self, your_moms_applications):
        assert (
            your_moms_applications.end_callback_call_count == 1
        ), "unexpected number of end callbacks"

    def test_correct_number_of_elements(self, your_moms_applications):
        assert (
            len(your_moms_applications.elements) == 48
        ), "unexpected number of applications parsed"

    def test_first_element_data_check(self, your_moms_applications):
        assert (
            your_moms_applications.elements[0]["token"] == "d993a68bf4e7"
        ), "unexpected token for application 0"
        assert your_moms_applications.elements[0][
            "time"
        ] == datetime.datetime.utcfromtimestamp(
            1472069089113 / 1000.0
        ), "unexpected time for application 0"
        assert (
            your_moms_applications.elements[0]["name"] == "Internet Explorer"
        ), "unexpected name for application 0"
        assert (
            your_moms_applications.elements[0]["version"] == "10.0"
        ), "unexpected version for application 0"
        assert (
            your_moms_applications.elements[0]["external_ip"] == "192.168.168.254"
        ), "unexpected external_ip for application 0"
        assert (
            your_moms_applications.elements[0]["internal_ip"] == None
        ), "unexpected internal_ip for application 0"
