# Description

The ```decoy.c``` program can be used by a Blue agent to deploy a decoy service on a specified port.

# Building

```gcc decoy.c -o decoy```

# Usage

To listen on the default port (5001):

```./decoy```

To listen on a non-privileged port:

```./decoy 5002```

To listen on a privileged port:

```sudo ./decoy 22```

Connection attempts are logged to a file named ```decoy_connections.log``` that includes the date, source IP address, and port. It looks like the following:

```
2024-02-21 10:30:55, 127.0.0.1, 5001
2024-02-21 10:43:12, 127.0.0.1, 29
```

