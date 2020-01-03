from django.test import TestCase


class LoginViewTests(TestCase):
    def test_register(self):
        """先看看能不能打开注册界面"""
        response = self.client.get("/register/")
        self.assertEqual(response.status_code, 200)

    def test_login(self):
        """先看看能不能打开登录界面"""
        response = self.client.get("/login/")
        self.assertEqual(response.status_code, 200)
