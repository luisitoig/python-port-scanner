import socket
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
 
TIMEOUT = 0.5      # seconds to wait for each connection
MAX_THREADS = 100  # how many ports to check at once
 
 
def scan_port(host, port):
    """Return the port number if it's open, otherwise None."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(TIMEOUT)

        if s.connect_ex((host, port)) == 0:
            return port
    return None
 
 
def get_service_name(port):
    try:
        return socket.getservbyport(port, "tcp")
    except OSError:
        return "unknown"
 
 
def main():
    if len(sys.argv) > 1:
        target = sys.argv[1]
        start_port = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        end_port = int(sys.argv[3]) if len(sys.argv) > 3 else 1024
    else:
        target = input("Host to scan (e.g. 127.0.0.1): ").strip() or "127.0.0.1"
        start_port = int(input("Start port [1]: ").strip() or 1)
        end_port = int(input("End port [1024]: ").strip() or 1024)
 
    try:
        host = socket.gethostbyname(target)
    except socket.gaierror:
        print(f"Couldn't resolve hostname: {target}")
        sys.exit(1)
 
    print(f"Scanning {target} ({host}) ports {start_port}-{end_port}")
    print(f"Started at {datetime.now():%H:%M:%S}\n")
 
    ports = range(start_port, end_port + 1)
    try:
        with ThreadPoolExecutor(max_workers=MAX_THREADS) as pool:
            results = pool.map(lambda p: scan_port(host, p), ports)
            open_ports = [p for p in results if p is not None]
    except KeyboardInterrupt:
        print("\nScan cancelled.")
        sys.exit(0)
 
    if open_ports:
        for port in open_ports:
            print(f"  Port {port:<6} OPEN   ({get_service_name(port)})")
    else:
        print("  No open ports found.")
 
    print(f"\nDone at {datetime.now():%H:%M:%S} - {len(open_ports)} open port(s).")
 
 
if __name__ == "__main__":
    main()
