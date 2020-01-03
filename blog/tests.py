from django.test import TestCase
from django.urls import reverse


class BlogViewTests(TestCase):
    def test_index(self):
        """先看看能不能打开主界面"""
        response = self.client.get(reverse("blog:index"))
        self.assertEqual(response.status_code, 200)
