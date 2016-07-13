from django.core.urlresolvers import reverse
from django.test import SimpleTestCase, TestCase

from . import models, views


class ViewsTestCase(TestCase):
    def test_api_root(self):
        response = self.client.get('/api/')
        self.assertEqual(response.status_code, 200)
