def get_host_info(node: str, true_obs: dict) -> str:
    if not true_obs:
        return "Not Supported in Emulation Mode"
        
    if '_router' in node:
        return ""

    hover_text = ""

    # true_obs = self._get_true_state()
    node_info = true_obs[node]

    hover_text += "System info:<br>"
    system_info = node_info.get('System info', {})
    os_info = f"{system_info.get('OSType', '').name} " \
      f"{system_info.get('OSDistribution', '').name} " \
      f"({system_info.get('Architecture', '').name})"

    hover_text += os_info + "<br><br>"

    hover_text += "Processes info:<br>"
    
    processes = node_info.get('Processes', [])
    for proc in processes:
        process_name = proc.get('Process Name', 'N/A')
        pid = proc.get('PID', 'N/A')
        username = proc.get('Username', 'N/A')
        port_info = ', '.join([f"Port: {conn['local_port']}" for conn in proc.get('Connections', [])])
        hover_text+=f"- {process_name} (PID: {pid}, User: {username}, {port_info})<br>"

    return hover_text

def get_node_color(node: str, discovered_subnets: set, discovered_systems: set, escalated_hosts: set, exploited_hosts: set) -> str:
    color = "green"
    
    if 'router' in node:
        if node in discovered_subnets:
            color = 'rosybrown'
    
    if node in discovered_systems:
        color = "pink"
    
    if node in escalated_hosts:
        color = "red"
        
    elif node in exploited_hosts:
        color = "orange"
    
    return color

def get_node_border(node, target_host=None) -> dict:
    if target_host and node in target_host:
        border = dict(width=2, color='black')
    else:
        border = dict(width=0, color='white')
    return border