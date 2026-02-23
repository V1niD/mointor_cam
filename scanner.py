import socket
from datetime import datetime
from colorama import Fore, init

init(autoreset=True)

def scan_network(network_prefix, start, end, port):
    print(f"{Fore.CYAN}Buscando dispositivos na porta {port} ({network_prefix}.{start}-{end})...")
    print("Isso pode levar alguns instantes.\n")
    
    found_devices = []

    for i in range(start, end + 1):
        ip = f"{network_prefix}.{i}"
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.1)
        
        result = sock.connect_ex((ip, port))
        
        if result == 0:
            print(f"{Fore.GREEN}[ACHADO] Dispositivo em {ip}:{port}")
            found_devices.append({"ip": ip, "porta": port})
        
        sock.close()

    return found_devices

if __name__ == "__main__":
    meu_prefixo = "000.000.0" 
    portas_comuns = [80, 8000, 8080]

    todas_cameras = []
    for p in portas_comuns:
        todas_cameras.extend(scan_network(meu_prefixo, 1, 254, p))

    print(f"\n{Fore.CYAN}=== RESUMO PARA CONFIG.JSON ===")
    for cam in todas_cameras:
        print(f"IP: {cam['ip']} | Porta: {cam['porta']}")
