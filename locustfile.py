from locust import HttpUser, User, task, between, stats

stats.CSV_STATS_INTERVAL_SEC = 5

class Docker(HttpUser):
    host = "http://localhost"

    @task
    def get_users(self):
        self.client.get("/api/user", name="users-docker")

    @task
    def get_orders(self):
        self.client.get("/api/orders", name="orders-docker")

class Pythonanywhere(HttpUser):
    host = "https://despachomotorizado.pythonanywhere.com/"

    @task
    def get_users(self):
        self.client.get("/api/user", name="users-pythonanywhere")
    
    @task
    def get_orders(self):
        self.client.get("/api/orders", name="orders-pythonanywhere")