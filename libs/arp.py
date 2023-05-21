import socket
from concurrent.futures import ThreadPoolExecutor
from loguru import logger

def get_banner(s):
    return s.recv(1024)

def scan_port(ipaddress, port=139):
    try:
        sock = socket.socket()
        sock.settimeout(0.5)
        sock.connect((ipaddress, port))
        try:
            banner = get_banner(sock)
            logger.info('[+] Open Port ' + str(port) + ' : ' + str(banner.decode().strip('\n').strip('\r')))
        except Exception:
            logger.info(f'[+] Open Port {ipaddress}:{port}')
        return (socket.gethostbyaddr(ipaddress)[0], ipaddress, "")
    except Exception:
        return False

if __name__ == "__main__":
    results = [ f"192.168.1.{i}" for i in range(1, 255)]
    with ThreadPoolExecutor(max_workers=255) as executor:
        executor.map(scan_port, results)