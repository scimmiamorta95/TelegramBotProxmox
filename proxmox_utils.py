from proxmoxer import ProxmoxAPI
import time
import logging
from config import (
    PROXMOX_HOST, PROXMOX_USER, PROXMOX_TOKEN_NAME, PROXMOX_TOKEN_VALUE,
    VERIFY_SSL, TIMEOUT, MAX_RETRIES, RETRY_DELAY, CONNECTION_CACHE_DURATION
)

logger = logging.getLogger(__name__)

_proxmox_connection = None
_connection_time = 0


def get_proxmox_connection():
    global _proxmox_connection, _connection_time

    current_time = time.time()
    if _proxmox_connection is not None and current_time - _connection_time < CONNECTION_CACHE_DURATION:
        return _proxmox_connection

    try:
        logger.info("Creating new Proxmox connection...")
        _proxmox_connection = ProxmoxAPI(
            PROXMOX_HOST,
            user=PROXMOX_USER,
            token_name=PROXMOX_TOKEN_NAME,
            token_value=PROXMOX_TOKEN_VALUE,
            verify_ssl=VERIFY_SSL,
            timeout=TIMEOUT
        )
        _connection_time = current_time
        return _proxmox_connection
    except Exception as e:
        logger.error(f"Proxmox connection error: {e}")
        _proxmox_connection = None
        raise


def execute_with_retry(func, *args, **kwargs):
    last_exception = None
    for attempt in range(MAX_RETRIES):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.warning(f"Attempt {attempt+1}/{MAX_RETRIES} failed: {e}")
            last_exception = e
            time.sleep(RETRY_DELAY)
    raise last_exception


def test_connection():
    try:
        proxmox = get_proxmox_connection()
        nodes = execute_with_retry(proxmox.nodes.get)
        return True, f"Connection successful - Found {len(nodes)} nodes"
    except Exception as e:
        return False, f"Connection failed: {str(e)}"


def find_vm_node(vmid):
    proxmox = get_proxmox_connection()

    def _find():
        nodes = proxmox.nodes.get()
        for node in nodes:
            node_name = node['node']
            try:
                vm = proxmox.nodes(node_name).qemu(vmid).status.current.get()
                return node_name, 'qemu', vm
            except:
                pass
            try:
                vm = proxmox.nodes(node_name).lxc(vmid).status.current.get()
                return node_name, 'lxc', vm
            except:
                pass
        return None, None, None

    return execute_with_retry(_find)


def start_vm_or_container(vmid):
    try:
        node_name, vm_type, vm_info = find_vm_node(vmid)
        if not node_name:
            return False, "VM/LXC not found"

        if vm_info['status'] == 'running':
            return True, f"{vm_type.upper()} {vmid} already running"

        proxmox = get_proxmox_connection()

        def _start():
            if vm_type == 'qemu':
                return proxmox.nodes(node_name).qemu(vmid).status.start.post()
            else:
                return proxmox.nodes(node_name).lxc(vmid).status.start.post()

        execute_with_retry(_start)
        return True, f"Started {vm_type.upper()} {vmid} on node {node_name}"

    except Exception as e:
        return False, f"Error: {str(e)}"


def stop_vm_or_container(vmid, force=False):
    try:
        node_name, vm_type, vm_info = find_vm_node(vmid)
        if not node_name:
            return False, "VM/LXC not found"

        if vm_info['status'] == 'stopped':
            return True, f"{vm_type.upper()} {vmid} already stopped"

        proxmox = get_proxmox_connection()

        def _stop():
            if vm_type == 'qemu':
                return proxmox.nodes(node_name).qemu(vmid).status.stop.post(forceStop=int(force))
            else:
                return proxmox.nodes(node_name).lxc(vmid).status.stop.post(forceStop=int(force))

        execute_with_retry(_stop)
        time.sleep(8)
        _, _, new_info = find_vm_node(vmid)

        if new_info and new_info['status'] == 'stopped':
            return True, f"{vm_type.upper()} {vmid} stopped on node {node_name}"
        else:
            return False, f"{vm_type.upper()} {vmid} may still be running"

    except Exception as e:
        return False, f"Error: {str(e)}"


def restart_vm_or_container(vmid):
    try:
        node_name, vm_type, vm_info = find_vm_node(vmid)
        if not node_name:
            return False, "VM/LXC not found"

        proxmox = get_proxmox_connection()

        def _restart():
            if vm_type == 'qemu':
                return proxmox.nodes(node_name).qemu(vmid).status.restart.post()
            else:
                return proxmox.nodes(node_name).lxc(vmid).status.restart.post()

        execute_with_retry(_restart)
        return True, f"Restarted {vm_type.upper()} {vmid} on node {node_name}"

    except Exception as e:
        return False, f"Error: {str(e)}"


def get_all_vms_status():
    try:
        proxmox = get_proxmox_connection()

        def _get_status():
            all_vms = []
            nodes = proxmox.nodes.get()

            for node in nodes:
                node_name = node['node']
                try:
                    qemus = proxmox.nodes(node_name).qemu.get()
                    for vm in qemus:
                        vm['node_name'] = node_name
                        vm['vm_type'] = 'QEMU'
                        all_vms.append(vm)
                except:
                    pass
                try:
                    lxcs = proxmox.nodes(node_name).lxc.get()
                    for vm in lxcs:
                        vm['node_name'] = node_name
                        vm['vm_type'] = 'LXC'
                        all_vms.append(vm)
                except:
                    pass

            if not all_vms:
                return "No VMs found."

            all_vms.sort(key=lambda x: (x['node_name'], int(x['vmid'])))

            from collections import defaultdict
            vms_by_node = defaultdict(list)
            for vm in all_vms:
                vms_by_node[vm['node_name']].append(vm)

            reply = "🖥️ VM/LXC STATUS\n\n"
            for node in sorted(vms_by_node.keys()):
                reply += f"🖥️ Nodo: {node}\n"
                for vm in vms_by_node[node]:
                    icon = "🟢" if vm['status'] == 'running' else "🔴"
                    reply += f" {icon} {vm['name']} (ID: {vm['vmid']}, type: {vm['vm_type']}) - {vm['status']}\n"
                reply += "\n"
            return reply.strip()

        return execute_with_retry(_get_status)

    except Exception as e:
        return f"Error retrieving status: {str(e)}"
