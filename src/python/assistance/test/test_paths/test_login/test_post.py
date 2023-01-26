"""


    Generated by: https://openapi-generator.tech
"""

import unittest
from unittest.mock import patch

import _client
import urllib3
from _client import api_client, configuration, schemas
from _client.paths.login import post  # noqa: E501

from .. import ApiTestMixin


class TestLogin(ApiTestMixin, unittest.TestCase):
    """
    Login unit test stubs
        Login For Access Token  # noqa: E501
    """

    _configuration = configuration.Configuration()

    def setUp(self):
        used_api_client = api_client.ApiClient(configuration=self._configuration)
        self.api = post.ApiForpost(api_client=used_api_client)  # noqa: E501

    def tearDown(self):
        pass

    response_status = 200


if __name__ == "__main__":
    unittest.main()
