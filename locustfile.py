from locust import HttpUser, TaskSet, task, between

class UserBehavior(TaskSet):
    @task
    def get_api(self):
        self.client.get("http://51.21.129.246:8000/service_provider/get/all")  # Adjust this to your API endpoint

    # @task
    # def post_api(self):
    #     self.client.post("/api/your-endpoint/", json={"key": "value"}) 

class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(1, 5)  # Wait time between tasks
