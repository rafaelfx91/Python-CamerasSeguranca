import cv2
import time
from flask import Flask, Response, render_template, jsonify

# --- Links RTSP das suas câmeras (JÁ CONFIGURADOS) ---
CAM1_RTSP = "rtsp://192.168.0.1/user=admin&password=admin&channel=0&stream=1.sdp"
CAM2_RTSP = "rtsp://192.168.0.2/user=admin&password=admin&channel=0&stream=1.sdp"
# -----------------------------------------------------

app = Flask(__name__)

def get_cpu_temperature():
    """
    Lê a temperatura da CPU do Orange Pi.
    Retorna a temperatura em Celsius ou None em caso de erro.
    """
    try:
        # Lê o arquivo de temperatura da CPU (caminho comum em Orange Pi/ARM)
        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
            temp = f.read().strip()
        
        # Converte de millicelsius para Celsius
        temp_celsius = float(temp) / 1000.0
        return temp_celsius
    
    except Exception as e:
        print(f"Erro ao ler temperatura: {e}")
        return None

def generate_frames(camera_url):
    """
    Gerador de frames para uma câmera específica.
    Tenta reconectar em caso de falha e exibe um placeholder.
    """
    print(f"Iniciando stream para: {camera_url}")
    while True:
        cap = cv2.VideoCapture(camera_url)
        if not cap.isOpened():
            print(f"Erro: Não foi possível abrir o stream da câmera: {camera_url}. Tentando reconectar em 5s...")
            # Gera uma imagem de placeholder indicando erro de conexão
            # Cria uma imagem preta com texto de erro
            placeholder_img = cv2.UMat(480, 640, cv2.CV_8UC3, (0, 0, 0))
            cv2.putText(placeholder_img, "CAMERA OFFLINE", (150, 240), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3, cv2.LINE_AA)
            _, buffer = cv2.imencode(".jpg", placeholder_img)
            placeholder_bytes = buffer.tobytes()
            
            # Envia o placeholder repetidamente
            while True:
                yield (b"--frame\r\n"
                       b"Content-Type: image/jpeg\r\n\r\n" + placeholder_bytes + b"\r\n")
                time.sleep(5) # Espera 5 segundos antes de tentar de novo
            # Não deve chegar aqui, o loop interno deve continuar enviando o placeholder

        # Loop de captura de frames enquanto a câmera estiver aberta
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                print(f"Erro: Falha ao ler o frame da câmera: {camera_url}. Tentando reconectar...")
                break  # Sai do loop interno para tentar reconectar

            # Codifica o frame para JPEG
            ret, buffer = cv2.imencode(".jpg", frame)
            if not ret:
                continue # Pula para o próximo frame se a codificação falhar

            frame_bytes = buffer.tobytes()

            # Envia o frame no formato multipart/x-mixed-replace
            yield (b"--frame\r\n"
                   b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n")
        
        cap.release()
        print(f"Stream da câmera {camera_url} fechado. Tentando reconectar em 5 segundos...")
        time.sleep(5) # Espera 5 segundos antes de tentar reconectar

@app.route("/")
def index():
    """Rota principal que renderiza a página HTML."""
    return render_template("index.html")

@app.route("/video_feed/<camera_id>")
def video_feed(camera_id):
    """Rota que fornece o stream de vídeo para uma câmera específica."""
    if camera_id == "1":
        url = CAM1_RTSP
    elif camera_id == "2":
        url = CAM2_RTSP
    else:
        return "Câmera não encontrada", 404
    
    return Response(generate_frames(url),
                    mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/temperature")
def temperature():
    """
    Nova rota para medir a temperatura do Orange Pi em tempo real.
    Retorna JSON com a temperatura atual.
    """
    temp = get_cpu_temperature()
    
    if temp is not None:
        return jsonify({
            "temperature": temp,
            "unit": "celsius",
            "status": "success",
            "timestamp": time.time()
        })
    else:
        return jsonify({
            "temperature": None,
            "unit": "celsius",
            "status": "error",
            "message": "Não foi possível ler a temperatura",
            "timestamp": time.time()
        }), 500

@app.route("/temperature_page")
def temperature_page():
    """
    Rota que retorna uma página HTML simples para exibir a temperatura.
    """
    temp = get_cpu_temperature()
    
    if temp is not None:
        status = f"Temperatura atual: {temp:.1f}°C"
        color = "red" if temp > 70 else "orange" if temp > 60 else "green"
    else:
        status = "Erro ao ler temperatura"
        color = "gray"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Temperatura Orange Pi</title>
        <meta http-equiv="refresh" content="5">
        <style>
            body {{
                font-family: Arial, sans-serif;
                text-align: center;
                padding: 50px;
                background-color: #f0f0f0;
            }}
            .temperature {{
                font-size: 2.5em;
                color: {color};
                font-weight: bold;
                margin: 20px 0;
            }}
            .container {{
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
                display: inline-block;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Temperatura do Orange Pi</h1>
            <div class="temperature">{status}</div>
            <p>Atualizado a cada 5 segundos</p>
            <p><a href="/">Voltar para câmeras</a></p>
        </div>
    </body>
    </html>
    """
    return html_content

if __name__ == "__main__":
    # Use 0.0.0.0 para ser acessível na sua rede local
    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)