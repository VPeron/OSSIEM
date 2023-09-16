import psutil

from utils.custom_logger import setup_custom_logger

sys_logger = setup_custom_logger('main_client')

def get_cpu_usage():
    return psutil.cpu_percent(interval=1, percpu=True)

def get_memory_usage():
    virtual_memory = psutil.virtual_memory()
    return {
        "total": int(virtual_memory.total),
        "available": int(virtual_memory.available),
        "used": virtual_memory.used,
        "free": virtual_memory.free,
        "percent": virtual_memory.percent
    }

def get_disk_usage():
    partitions = psutil.disk_partitions()
    disk_info = {}
    for partition in partitions:
        usage = psutil.disk_usage(partition.mountpoint)
        disk_info[partition.device] = {
            "total": usage.total,
            "used": usage.used,
            "free": usage.free,
            "percent": usage.percent
        }
    return disk_info

def get_system_stats():
    cpu_usage = get_cpu_usage()
    memory_usage = get_memory_usage()
    disk_usage = get_disk_usage()

    sys_logger.info("CPU Usage:")
    for i, core in enumerate(cpu_usage):
        sys_logger.info(f"Core {i + 1}: {core}%")

    sys_logger.info("Memory Usage:")
    sys_logger.info(f"Total: {memory_usage['total'] / (1024 ** 3):.2f} GB")
    sys_logger.info(f"Available: {memory_usage['available'] / (1024 ** 3):.2f} GB")
    sys_logger.info(f"Used: {memory_usage['used'] / (1024 ** 3):.2f} GB")
    sys_logger.info(f"Free: {memory_usage['free'] / (1024 ** 3):.2f} GB")
    sys_logger.info(f"Usage Percentage: {memory_usage['percent']}%")

    sys_logger.info("Disk Usage:")
    for device, info in disk_usage.items():
        if "/dev/loop" in device:
            continue
        sys_logger.info(f"Device: {device}")
        sys_logger.info(f"Total: {info['total'] / (1024 ** 3):.2f} GB")
        sys_logger.info(f"Used: {info['used'] / (1024 ** 3):.2f} GB")
        sys_logger.info(f"Free: {info['free'] / (1024 ** 3):.2f} GB")
        sys_logger.info(f"Usage Percentage: {info['percent']}%")
        sys_logger.info("")

if __name__ == "__main__":
    get_system_stats()
