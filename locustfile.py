from locust import HttpUser, User, task, between

class MyUser(HttpUser):

    @task
    def my_task(self):
        self.client.get("/api/user")

    