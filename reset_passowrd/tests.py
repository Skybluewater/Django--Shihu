from django.test import TestCase


class ResetPasswordViewTests(TestCase):
    def test_resetpassword(self):
        """先看看能不能打开重置密码界面"""
        response = self.client.get("/reset_passowrd/reset/")
        self.assertEqual(response.status_code, 200)
