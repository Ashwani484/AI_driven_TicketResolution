from nodes.cachedelete import cachedeletion
from nodes.network import network_node
from nodes.server_reboot import server_reboot
from nodes.sys_optimization import sys_optimization

def route_node(node_name):
    print(f"Routing to node: {node_name}")

    if node_name == "cachedeletion":
        
        cachedeletion()

    elif node_name == "network":
        network_node()
    
    elif node_name == "server_reboot":
        server_reboot()
    elif node_name == "sys_optimization":
        sys_optimization()
    else:
        print(f"Node not found: {node_name}")