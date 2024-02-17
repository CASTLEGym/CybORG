from collections import defaultdict


file_path = './assets/packet.log'  # Log file location

try:
    with open(file_path, 'r') as file:
        content = file.read()
        #print(content)
except FileNotFoundError:
    print(f"File not found: {file_path}")
except Exception as e:
    print(f"An error occurred: {e}")
    
log_data=content.split('\n')
log_data=log_data[:-1]
#print(log_data)


# Dictionary to store counts for each IP address
ip_counts = defaultdict(lambda: {'incoming': 0, 'outgoing': 0})

# Analyze the log data
for log_entry in log_data:
    parts = log_entry.split()
    #print(parts)
    src_ip_port, dest_ip_port = parts[-3],parts[-1]
    #print(src_ip_port, dest_ip_port)

    src_ip, src_port = src_ip_port.split(":")
    dest_ip, dest_port = dest_ip_port.split(":")

    # Increment counts based on the direction of the packet
    ip_counts[src_ip]['outgoing'] += 1
    ip_counts[dest_ip]['incoming'] += 1

# Print the results
for ip, counts in ip_counts.items():
    print(f"IP Address: {ip}, Incoming: {counts['incoming']}, Outgoing: {counts['outgoing']}")

