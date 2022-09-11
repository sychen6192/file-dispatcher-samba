import scapy.all as scapy
import socket
from concurrent.futures import ThreadPoolExecutor


def scan(ip):
    arp_request = scapy.ARP(pdst=ip)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast/arp_request
    answered_list = scapy.srp(arp_request_broadcast, timeout=1, verbose=False)[0]

    print("IP\t\t\tMAC Address\n-------------------------------------------")
    IPs = []
    for element in answered_list:
        print(element[1].psrc + "\t\t" + element[1].hwsrc)
        IPs.append(element[1].psrc)
    return IPs


def get_banner(s):
    return s.recv(1024)


def scan_port(ipaddress, port=139):
    try:
        sock = socket.socket()
        sock.settimeout(0.5)
        sock.connect((ipaddress, port))
        try:
            banner = get_banner(sock)
            print('[+] Open Port ' + str(port) + ' : ' + str(banner.decode().strip('\n').strip('\r')))
        except:
            print('[+] Open Port ' + str(port))
        return (socket.gethostbyaddr(ipaddress)[0], ipaddress)
    except:
        return False

if __name__ == "__main__":
    results = scan("192.168.1.1/24")
    with ThreadPoolExecutor(max_workers=6) as executor:
        executor.map(scan_port, results)