import logging
import time
import psutil

CPU_USAGE_THRESHOLD=80
MEMORY_USAGE_THRESHOLD=50
DISK_SPACE_THRESHOLD=80
RUNNING_PROCESSES=10

# Setup logging
logging.basicConfig(filename='system_health.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def check_cpu_usage():
    cpu_usage=psutil.cpu_percent(interval=1)
    print(f"CPU usage: {cpu_usage}")
    if cpu_usage > CPU_USAGE_THRESHOLD:
        logging.warning(f"CPU usage is above threshold! Current usage: {cpu_usage}%")
        print(f"CPU usage is above threshold! Current usage: {cpu_usage}%")
    return cpu_usage

def check_memory_usage():
    memory_usage=psutil.virtual_memory()
    print(f"Memory usage: {memory_usage.percent}")
    if memory_usage.percent > MEMORY_USAGE_THRESHOLD:
        logging.warning(f"Memory usage is above threshold! Current usage: {memory_usage.percent}%")
        print(f"Memory usage is above threshold! Current usage: {memory_usage.percent}%")
    return memory_usage.percent

def check_disk_space_usage():
    disk_space_usage=psutil.disk_usage(path="/")
    print(f"Disk space usage: {disk_space_usage.percent}")
    if disk_space_usage.percent > DISK_SPACE_THRESHOLD:
        logging.warning(f"Disk space usage is above threshold! Current usage: {disk_space_usage.percent}%")
        print(f"Disk space usage is above threshold! Current usage: {disk_space_usage.percent}%")
    return disk_space_usage.percent
    
def check_running_processes():
    processes = list(psutil.process_iter(['pid', 'name', 'cpu_percent']))

    for process in processes:
        try:
            process.cpu_percent(interval=0.1)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    processes = [p for p in processes if p.info['cpu_percent'] is not None]
    sorted_processes = sorted(processes, key=lambda p: p.info['cpu_percent'], reverse=True)
    
    top_processes = sorted_processes[:RUNNING_PROCESSES]
    for proc in top_processes:
        print(f"PID: {proc.info['pid']}, Name: {proc.info['name']}, CPU Usage: {proc.info['cpu_percent']}%")
        logging.info(f"PID: {proc.info['pid']}, Name: {proc.info['name']}, CPU Usage: {proc.info['cpu_percent']}%")
    
    return top_processes
def monitor_system():
    check_cpu_usage()
    check_memory_usage()
    check_disk_space_usage()
    check_running_processes()


if __name__ == "__main__":
    try:
        while True:
            monitor_system()
            time.sleep(5)  # Monitor every 5 seconds
    except KeyboardInterrupt:
        print("System health monitoring stopped.")
        logging.info("System health monitoring stopped.")