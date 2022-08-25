import time
from locust import HttpUser, task, between


class QuickstartUser(HttpUser):
    host = "http://localhost"
    def __init__(self, parent):
        super(QuickstartUser, self).__init__(parent)
        self.token = ""

    wait_time = between(1, 2)

    def on_start(self):
        with self.client.post(url="api/user/login",data=
            {
                "email": "correo@operador123.com",
                "password": "I5J4xxnjXQ"
            }
         ) as response:
            self.token = {
                "auth-user":response,
                "user-id":59,
                "role_key": "Operator"
            }.json()
            

    @task
    def secret_page(self):
        self.client.get(url="/front/order", headers={"authorization": self.token})