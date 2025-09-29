import cv2
import time
from flask import Flask, Response, render_template, jsonify

# --- Links RTSP das suas câmeras (JÁ CONFIGURADOS) ---
CAM1_RTSP = "rtsp://192.168.0.1/user=admin&password=admin&channel=0&stream=1.sdp"
CAM2_RTSP = "rtsp://192.168.0.2/user=admin&password=admin&channel=0&stream=1.sdp"
# -----------------------------------------------------

app = Flask(__name__)

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

if __name__ == "__main__":
    # Use 0.0.0.0 para ser acessível na sua rede local
    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)

