import os.path
import unittest
from unittest.mock import patch, Mock
import pandas as pd
import requests.exceptions
from pandas.testing import assert_frame_equal
from server import oauth
from server.modules.googlesheets import GoogleSheets
from server.modules.types import ProcessResult
from .util import MockParams, fetch_factory

# example_csv, example_tsv, example_xls, example_xlsx: same spreadsheet, four
# binary representations
example_csv = b'foo,bar\n1,2\n2,3'
example_tsv = b'foo\tbar\n1\t2\n2\t3'
with open(os.path.join(os.path.dirname(__file__), '..', 'test_data',
                       'example.xls'), 'rb') as f:
    example_xls = f.read()
with open(os.path.join(os.path.dirname(__file__), '..', 'test_data',
                       'example.xlsx'), 'rb') as f:
    example_xlsx = f.read()

expected_table = pd.DataFrame({
    'foo': [1, 2],
    'bar': [2, 3],
})


class MockResponse:
    def __init__(self, status_code, text):
        self.status_code = status_code

        if isinstance(text, str):
            self.text = text
            self.content = text.encode('utf-8')
        else:
            self.content = text


default_secret = {'refresh_token': 'a-refresh-token'}
default_googlefileselect = {
    "id": "aushwyhtbndh7365YHALsdfsdf987IBHJB98uc9uisdj",
    "name": "Police Data",
    "url": "http://example.org/police-data",
    "mimeType": "application/vnd.google-apps.spreadsheet",
}


P = MockParams.factory(google_credentials=default_secret,
                       googlefileselect=default_googlefileselect,
                       has_header=True)

fetch = fetch_factory(GoogleSheets.fetch, P)


class GoogleSheetsTests(unittest.TestCase):
    def setUp(self):
        super().setUp()

        # Set up auth
        self.requests = Mock()
        self.requests.get = Mock(
            return_value=MockResponse(404, 'Test not written')
        )
        self.oauth_service = Mock()
        self.oauth_service.requests_or_str_error = Mock(
            return_value=self.requests
        )
        self.oauth_service_lookup_patch = patch.object(
            oauth.OAuthService,
            'lookup_or_none',
            return_value=self.oauth_service
        )
        self.oauth_service_lookup_patch.start()

    def tearDown(self):
        self.oauth_service_lookup_patch.stop()

        super().tearDown()

    def test_render_no_file(self):
        wf_module = fetch(googlefileselect='')
        self.assertEqual(wf_module.fetch_result.error, '')
        self.assertTrue(wf_module.fetch_result.dataframe.empty)

    def _assert_happy_path(self, wf_module):
        self.requests.get.assert_called_with(
            'https://www.googleapis.com/drive/v3/files/'
            'aushwyhtbndh7365YHALsdfsdf987IBHJB98uc9uisdj?alt=media'
        )

        self.assertEqual(wf_module.fetch_result.error, '')
        assert_frame_equal(wf_module.fetch_result.dataframe, expected_table)

    def test_fetch_csv(self):
        self.requests.get.return_value = MockResponse(200, example_csv)
        wf_module = fetch(googlefileselect={**default_googlefileselect,
                                            'mimeType': 'text/csv'})
        self._assert_happy_path(wf_module)

    def test_fetch_tsv(self):
        self.requests.get.return_value = MockResponse(200, example_tsv)
        wf_module = fetch(googlefileselect={
            **default_googlefileselect,
            'mimeType': 'text/tab-separated-values',
        })
        self._assert_happy_path(wf_module)

    def test_fetch_xls(self):
        self.requests.get.return_value = MockResponse(200, example_xls)
        wf_module = fetch(googlefileselect={
            **default_googlefileselect,
            'mimeType': 'application/vnd.ms-excel',
        })
        self._assert_happy_path(wf_module)

    def test_fetch_xlsx(self):
        self.requests.get.return_value = MockResponse(200, example_xlsx)
        wf_module = fetch(googlefileselect={
            **default_googlefileselect,
            'mimeType':
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        })
        self._assert_happy_path(wf_module)

    def test_no_first_row_header(self):
        self.requests.get.return_value = MockResponse(200, example_csv)
        wf_module = fetch(googlefileselect={**default_googlefileselect,
                                            'mimeType': 'text/csv'},
                          has_header=False)
        result = GoogleSheets.render(wf_module.params, pd.DataFrame(),
                                     fetch_result=wf_module.fetch_result)
        result.sanitize_in_place()  # TODO fix header-shift code; nix this
        assert_frame_equal(result.dataframe, pd.DataFrame({
            '0': ['foo', '1', '2'],
            '1': ['bar', '2', '3'],
        }))

    def test_no_table_on_missing_auth(self):
        wf_module = fetch(google_credentials=None)
        self.assertTrue(wf_module.fetch_result.dataframe.empty)
        self.assertEqual(wf_module.fetch_result.error,
                         'Not authorized. Please connect to Google Drive.')

    def test_no_table_on_http_error(self):
        self.requests.get.side_effect = \
            requests.exceptions.ReadTimeout('read timeout')
        wf_module = fetch()
        self.assertTrue(wf_module.fetch_result.dataframe.empty)
        self.assertEqual(wf_module.fetch_result.error, 'read timeout')

    def test_no_table_on_missing_table(self):
        self.requests.get.return_value = MockResponse(404, 'not found')
        wf_module = fetch()
        self.assertTrue(wf_module.fetch_result.dataframe.empty)
        self.assertEqual(wf_module.fetch_result.error,
                         'HTTP 404 from Google: not found')

    def test_render(self):
        self.requests.get.return_value = MockResponse(200, example_csv)
        wf_module = fetch(googlefileselect={**default_googlefileselect,
                                            'mimeType': 'text/csv'})
        result = GoogleSheets.render(wf_module.params, pd.DataFrame(),
                                     fetch_result=wf_module.fetch_result)
        self.assertEqual(result, ProcessResult(expected_table))
