import argparse
import getpass
import os
import socket
import select
import sys
import threading

import paramiko

SSH_PORT = 22
DEFAULT_PORT = 4000

def handler(chan, host, port):
    try:
        with socket.socket() as sock:
            sock.connect((host, port))
            print(f"Connected! Tunnel open {chan.origin_addr} -> {chan.getpeername()} -> {(host, port)}")
            while True:
                r, _, _ = select.select([sock, chan], [], [])
                if sock in r:
                    data = sock.recv(1024)
                    if not data:
                        break
                    chan.send(data)
                if chan in r:
                    data = chan.recv(1024)
                    if not data:
                        break
                    sock.send(data)
    except Exception as e:
        print(f"Forwarding request to {host}:{port} failed: {e}")
    finally:
        try:
            chan.close()
        except Exception:
            pass # channel might already be closed.
        print(f"Tunnel closed from {chan.origin_addr}")

def reverse_forward_tunnel(server_port, remote_host, remote_port, transport):
    transport.request_port_forward("", server_port)
    while True:
        chan = transport.accept(1000)
        if chan is None:
            continue
        thr = threading.Thread(target=handler, args=(chan, remote_host, remote_port), daemon=True)
        thr.start()

def main():
    parser = argparse.ArgumentParser(description="Reverse SSH tunnel.")
    parser.add_argument("server", help="SSH server [host:port]")
    parser.add_argument("-q", "--quiet", action="store_true", help="Squelch all informational output")
    parser.add_argument("-p", "--remote-port", type=int, default=DEFAULT_PORT, help=f"Port on server to forward (default: {DEFAULT_PORT})")
    parser.add_argument("-u", "--user", default=getpass.getuser(), help=f"Username for SSH authentication (default: {getpass.getuser()})")
    parser.add_argument("-K", "--key", help="Private key file to use for SSH authentication")
    parser.add_argument("--no-key", action="store_false", dest="look_for_keys", default=True, help="Don't look for or use a private key file")
    parser.add_argument("-P", "--password", action="store_true", help="Read password (for key or password auth) from stdin")
    parser.add_argument("-r", "--remote", required=True, metavar="host:port", help="Remote host and port to forward to")

    args = parser.parse_args()

    server_host, server_port = args.server.split(":", 1) if ":" in args.server else (args.server, SSH_PORT)
    server_port = int(server_port)
    remote_host, remote_port = args.remote.split(":", 1) if ":" in args.remote else (args.remote, SSH_PORT)
    remote_port = int(remote_port)

    password = getpass.getpass("Enter SSH password: ") if args.password else None

    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy()) # Add this line
    try:
        client.connect(
            server_host,
            server_port,
            username=args.user,
            key_filename=args.key,
            look_for_keys=args.look_for_keys,
            password=password,
            timeout=10, # Add timeout to connect.
            banner_timeout=10, # Add banner timeout to connect.
            auth_timeout=10, # Add auth timeout to connect.
            allow_agent=True, #allow ssh-agent
            )

        transport = client.get_transport()
        transport.set_keepalive(30) #send keepalive every 30 seconds.

        print(f"Now forwarding remote port {args.remote_port} to {remote_host}:{remote_port} ...")
        reverse_forward_tunnel(args.remote_port, remote_host, remote_port, transport)

    except Exception as e:
        print(f"*** Failed: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("C-c: Port forwarding stopped.")
    finally:
        client.close()

if __name__ == "__main__":
    main()
