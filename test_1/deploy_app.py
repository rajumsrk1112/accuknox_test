import git
from kubernetes import client,config
import os
import subprocess
import shutil
import time
import yaml

def clone_git_repo(url):
    """
    Function to clone the git repository to the current working directory
    """
    print(f"Cloning github repo: {url}")
    git.Git().clone(url)

def deploy_app(namespace):
    """
    Function to deploy the frontend and backend deployments in the cluster in given namespace
    """
    config.load_kube_config()
    
    ns_v1=client.CoreV1Api()
    apps_v1 = client.AppsV1Api()
    core_v1 = client.CoreV1Api()

    namespace_body = {
        "apiVersion": "v1",
        "kind": "Namespace",
        "metadata": {
            "name": namespace
        }
    }

    # Create namespace
    print(f"Creating namspace: {namespace}")
    ns_v1.create_namespace(body=namespace_body)
    deploy_path=f"{os.getcwd()}/qa-test/Deployment"
    for filename in os.listdir(deploy_path):
        print(f"Filename: {filename}")
        with open(f"{deploy_path}/{filename}") as stream:
            try:
                documents = yaml.safe_load_all(stream)
                for doc in documents:
                    print(f"Deployment file: {doc}")
                    kind = doc.get('kind')
                    # Create deployment in given namespace
                    if kind=="Deployment":
                        print(f"creating deployment {filename} in namespace {namespace}")
                        apps_v1.create_namespaced_deployment(namespace,body=doc)
                    # Create Service in given namespace
                    elif kind=="Service":
                        print(f"Creating service of {filename} in namespace {namespace}")
                        core_v1.create_namespaced_service(namespace,body=doc)
            except yaml.YAMLError as exc:
                print(exc)

    # List the deployments in namespace
    apps_v1.list_namespaced_deployment(namespace)
    wait_for_pods_to_be_running(namespace_name=namespace)

def wait_for_pods_to_be_running(namespace_name, timeout=300, interval=10):
    """
    Wait for all Pods in the namespace to be in Running state.
    """
    core_v1 = client.CoreV1Api()
    end_time = time.time() + timeout

    while time.time() < end_time:
        pods = core_v1.list_namespaced_pod(namespace=namespace_name)
        all_pods_running = all(pod.status.phase == 'Running' for pod in pods.items)

        if all_pods_running:
            print(f"All Pods are in the Running state in namespace '{namespace_name}'.")
            return

        print(f"Not all Pods are Running yet. Waiting for {interval} seconds...")
        time.sleep(interval)

    print(f"Timeout reached. Not all Pods are in the Running state in namespace '{namespace_name}'.Issue with deployments s")

def port_forward(service_name, namespace_name, local_port, remote_port):
    """
    Port forward process
    """
    command = [
            "kubectl",
            "port-forward",
            f"svc/{service_name}",
            f"{local_port}:{remote_port}",
            "-n", namespace_name  
        ]
    print(f"Command: {command}")
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(f"Port forwarding from {local_port} to {remote_port} for service {service_name}")
    time.sleep(10)
    return process

def cleanup_namespace(namespace):
    """
    Cleanup the created namespace
    """
    config.load_kube_config()
    ns_v1 = client.CoreV1Api()
    ns_v1.delete_namespace(name=namespace)


def cleanup_repo(directory):
    """
    Function to delete the cloned repository directory
    """
    if os.path.exists(directory):
        shutil.rmtree(directory)
