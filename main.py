import time
import os
import sys
import json
from datetime import datetime
from onvif import ONVIFCamera
from plyer import notification
from colorama import Fore, Style, init

init(autoreset=True)

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

WSDL_PATH = os.path.join(BASE_DIR, 'wsdl')
CONFIG_FILE = os.path.join(BASE_DIR, 'config.json')
LOG_FILE = os.path.join(BASE_DIR, 'log_eventos.txt')

def carregar_configuracao():
    """Lê o arquivo JSON externo para identificar as câmeras manualmente."""
    if not os.path.exists(CONFIG_FILE):
        exemplo = [
            {
                "nome": "NOME_DA_CAMERA_SETOR",
                "ip": "192.168.0.191",
                "porta": 80,
                "user": "admin",
                "pass": "senha"
            }
        ]
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(exemplo, f, indent=4)
        print(f"{Fore.YELLOW}Arquivo config.json criado. Adicione as câmeras nele.")
        return exemplo
    
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def registrar_log(mensagem):
    timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"[{timestamp}] {mensagem}\n")

def enviar_alerta(titulo, msg):
    try:
        notification.notify(
            title=titulo,
            message=msg,
            app_name="Monitor CFTV Hospital",
            timeout=10
        )
    except:
        pass

def monitorar():
    print(f"{Fore.CYAN}=== MONITORAMENTO CFTV HOSPITALAR INICIADO ===")
    print(f"Configuração: {CONFIG_FILE}")
    print(f"Logs: {LOG_FILE}\n")

    cameras = carregar_configuracao()
    status_anterior = {cam['ip']: "online" for cam in cameras}

    while True:
        try:
            cameras = carregar_configuracao()
        except:
            print(f"{Fore.RED}Erro ao ler config.json. Verifique a sintaxe.")

        for cam in cameras:
            ip_atual = cam['ip']
            try:
                mycam = ONVIFCamera(
                    ip_atual, cam['porta'], cam['user'], cam['pass'], 
                    wsdl_dir=WSDL_PATH
                )
                device_info = mycam.devicemgmt.GetDeviceInformation()
                
                if status_anterior.get(ip_atual) == "offline":
                    msg_volta = f"RECUPERADA: {cam['nome']} ({ip_atual})"
                    print(f"{Fore.GREEN}[OK] {msg_volta}")
                    registrar_log(msg_volta)
                    enviar_alerta(f"{cam['nome']} ONLINE", "Conexão restabelecida.")
                    status_anterior[ip_atual] = "online"
                
                print(f"{Fore.GREEN}[ONLINE] {cam['nome']} | Modelo: {device_info.Model}")

            except Exception as e:
                if status_anterior.get(ip_atual, "online") == "online":
                    msg_erro = f"FALHA: {cam['nome']} ({ip_atual}) ficou offline."
                    print(f"{Fore.RED}[ERRO] {msg_erro}")
                    registrar_log(f"{msg_erro} | Detalhe: {e}")
                    enviar_alerta(
                        f"{cam['nome']} OFFLINE", 
                        f"Checklist L1: Verificar Switch e Cabo no IP {ip_atual}"
                    )
                    status_anterior[ip_atual] = "offline"
                else:
                    print(f"{Fore.YELLOW}[OFFLINE] {cam['nome']} - Aguardando reparo...")


if __name__ == "__main__":
    if not os.path.exists(WSDL_PATH):
        print(f"{Fore.RED}ERRO: Pasta WSDL não encontrada em {WSDL_PATH}")
    else:
        try:
            monitorar()
        except KeyboardInterrupt:
            sys.exit()
