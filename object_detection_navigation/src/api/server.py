import socket
import qrcode
from flask import Flask
from flask_cors import CORS
from src.api.routes import api_blueprint, init_cors

try:
    from waitress import serve
except ImportError:
    serve = None

def get_wifi_ip():
    try:
        import subprocess
        result = subprocess.run(["ipconfig"], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        
        wifi_section = False
        for line in lines:
            if 'Wi-Fi' in line and 'adapter' in line:
                wifi_section = True
            elif wifi_section and 'IPv4 Address' in line:
                ip = line.split(':')[-1].strip()
                if not ip.startswith('127.') and not ip.startswith('169.254'):
                    return ip
            elif wifi_section and 'adapter' in line and 'Wi-Fi' not in line:
                wifi_section = False
        
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
        except Exception:
            ip = "127.0.0.1"
        finally:
            s.close()
        return ip
    except Exception:
        return "192.168.43.221"

def create_app():
    app = Flask(__name__, static_folder="../..", template_folder="../..")
    init_cors(app)
    app.register_blueprint(api_blueprint)
    return app

def start_server():
    app = create_app()
    local_ip = get_wifi_ip()
    local_url = f"http://{local_ip}:5000"

    print("=" * 60)
    print("  SMART PATH SUGGESTOR SERVER (MODULAR)")
    print("=" * 60)
    print(f"\n  IP Detected:  {local_ip}")
    print(f"  Mobile app:   {local_url}/\n")

    print("  [ SCAN THIS QR CODE ON YOUR PHONE TO CONNECT ]")
    print("-" * 60)
    qr = qrcode.QRCode(version=1, box_size=1, border=2)
    qr.add_data(f"{local_url}/")
    qr.make(fit=True)
    qr.print_ascii()
    print("-" * 60)

    if serve:
        print(f"  Serving with WAITRESS")
        serve(app, host="0.0.0.0", port=5000, threads=6)
    else:
        app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)

if __name__ == "__main__":
    start_server()
