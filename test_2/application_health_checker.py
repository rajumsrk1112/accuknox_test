import requests
import time

TIME_INTERVAL = 5
FAILURE_THRESHOLD=3
APP_ENDPOINT="https://reqrest.in/api/users/1"
# APP_ENDPOINT="https://test123.in/api/users/1" #Invalid endpoint to check negative scenario


fail_count=0

def check_health(endpoint):
    """
    Checks the health of the application by sending an HTTP GET request to the specified endpoint.

    If the response status code is 200, it indicates that the application is up and running.
    Otherwise, it increments the failure count. If the failure count exceeds the threshold,
    the application is considered down.

    Args:
        endpoint (str): The URL of the application's health endpoint.
    """
    global fail_count
    try:
        response  = requests.get(endpoint)
        if response.status_code==200:
            print(f"Application is up and running")
            fail_count=0
        else:
            fail_count+=1
            print(f"HTTP Status code: {response.status_code}")
            if fail_count > FAILURE_THRESHOLD:
                print(f"Application is down. Consecutive failures: {fail_count}")
    except requests.RequestException as e:
        fail_count += 1
        print(f"Request failed: {e}")
        if fail_count > FAILURE_THRESHOLD:
            print(f"Application is down. Consecutive failures: {fail_count}")
        

if __name__=="__main__":
    while True:
        check_health(endpoint=APP_ENDPOINT)
        time.sleep(TIME_INTERVAL)
