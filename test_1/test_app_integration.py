from deploy_app import clone_git_repo,deploy_app,port_forward,cleanup_namespace,cleanup_repo
import requests

REPO_URL="https://github.com/Vengatesh-m/qa-test"
SERVICE_NAME="frontend-service"
NAMESPACE_NAME = "accuknox"
LOCAL_PORT=8080
REMOTE_PORT=80
FRONTEND_URL=f"http://localhost:{LOCAL_PORT}"
EXPCTED_RESPONSE="Hello from the Backend!"

def test_integration(frontend_url):
    """
    Test the integration between frontend and backend services.
    Args:
        frontend_url (str): The URL of the frontend service.
    """
    try:
        response = requests.get(frontend_url)
        response.raise_for_status()
        print(f"HTTP Status code: {response.status_code}")
        assert(response.status_code==200)
        print(f"Response from frontend service: {response.text}") 
        if EXPCTED_RESPONSE in response.text:
            print("Integration test passed: Frontend displays message from backend")
        else:
            print("Integration test failed: Message from backend not found in frontend response")
    except requests.RequestException as e:
        print(f"Integration test failed: {e}")


def main():
    # Clone github repo which contains the deployment files
    clone_git_repo(url=REPO_URL)
    # Deploy the app in accuknox namespace & wait for the pods to be up and running
    deploy_app(namespace=NAMESPACE_NAME)
    # From kind cluser, loadBalancer cant be accessed from localhost so we are port-forwarding to port 8080 of localhost
    port_forward_process = port_forward(
        service_name=SERVICE_NAME,
        namespace_name=NAMESPACE_NAME,
        local_port=LOCAL_PORT,
        remote_port=REMOTE_PORT
        )
    # Run the integration test
    test_integration(frontend_url=FRONTEND_URL)
    
    # Terminate the port forwarding process
    if port_forward_process:
        port_forward_process.terminate()
        port_forward_process.wait() 
    
    # Cleanup the namespace & cloned-repo
    cleanup_namespace(namespace=NAMESPACE_NAME)
    cleanup_repo(directory="qa-test")

if __name__ == "__main__":
    main()