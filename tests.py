
import os
from unittest import TestCase
from unittest.mock import patch

from testfixtures import Replace

from requests import Response

import caching

from app import route



class TestRouter(TestCase):
    @patch("app.requests")
    @patch("app.URLS")
    def test_caching(self,mock_urls,mock_requests):
        """
        This tests the caching behaviour of the router.
        This test should avoid any problems with externalities,
        specifically HTTP requests and any IO operations related
        to the caching by patching out the relevant functionality.
        """
        test_content = b"yeehaw"
        test_identifiers = ("foo","bar","baz")

        # Replace the cache with one that uses a simple dict backend
        dc = caching.DictCache()
        with Replace("app.cache",dc):

            mock_urls.__getitem__.return_value = "http://yee.biz"

            rsp = Response
            rsp.content = test_content 
            rsp.status_code = 200
            mock_requests.get.return_value = rsp

            response = route(*test_identifiers)

            storage_path = dc._resolve(*test_identifiers)
            self.assertEqual(dc.storage[storage_path],test_content)
            self.assertEqual(response.body,test_content)

            response = route(*test_identifiers)
            self.assertEqual(response.body,test_content)
            self.assertEqual(len(dc.storage),1)

    
