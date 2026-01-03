import ipaddress
import subprocess
import platform
import concurrent.futures

def ping(ip):
    # Bestimme den richtigen Parameter je nach Betriebssystem:
    # - Windows: -n 1 (eine Anfrage) und -w (Timeout in Millisekunden)
    # - Linux/Mac: -c 1 (eine Anfrage) und -W (Timeout in Sekunden)
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    # Führe den Ping-Befehl aus. Hier wird die Ausgabe unterdrückt.
    command = ['ping', param, '1', str(ip)]
    result = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return ip, result.returncode == 0

def scan_network(network):
    online_devices = []
    net = ipaddress.ip_network(network, strict=False)
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        # Starte parallel Pings für alle Hosts im Subnetz
        results = executor.map(ping, net.hosts())
    for ip, status in results:
        if status:
            online_devices.append(str(ip))
    return online_devices

if __name__ == '__main__':
    # Beispiel: Scanne das Netzwerk 192.168.8.0/24 (achte auf die korrekte Netzadresse)
    network = '192.168.1.0/24'
    online = scan_network(network)
    print("Online Geräte:")
    for device in online:
        print(device)
