# Sistema de Monitoramento com Câmeras RTSP e Métricas do Sistema

Sistema Flask para streaming de múltiplas câmeras RTSP com monitoramento completo do Orange Pi em tempo real.


## DESCRIÇÃO
- Transmite vídeo de duas câmeras RTSP simultaneamente
- Monitora temperatura, uso de CPU e memória RAM do Orange Pi em tempo real
- Interface web responsiva com design dark mode
- Sistema de reconexão automática para câmeras offline
- Indicadores visuais coloridos para cada métrica do sistema

# TECNOLOGIAS
- Python 3 + Flask 3.0.3
- OpenCV para captura de vídeo
- psutil para métricas do sistema
- HTML5 + CSS3 + JavaScript para interface
- Systemd para inicialização automática

## ESTRUTURA DO PROJETO
project/<br>
├── app.py                 # Aplicação Flask principal<br>
├── requirements.txt       # Dependências do Python<br>
├── start.sh              # Script de inicialização<br>
├── templates/<br>
│   └── index.html        # Interface web<br>
└── README.md<br>

## CONFIGURAÇÃO


## 1. INSTALAÇÃO DAS DEPENDÊNCIAS
    # Criar ambiente virtual
    python -m venv venv
    source venv/bin/activate
    
    # Instalar dependências
    pip install -r requirements.txt   

## 2. CONFIGURAR URLs DAS CÂMERAS
    Edite o arquivo app.py e atualize as variáveis:
    CAM1_RTSP = "rtsp://seu_ip_camera1/stream"
    CAM2_RTSP = "rtsp://seu_ip_camera2/stream"

## 3. CONFIGURAR INICIALIZAÇÃO AUTOMÁTICA
      # Tornar o script executável
      chmod +x start.sh
      
      # Criar serviço systemd
      sudo nano /etc/systemd/system/flask_camera.service


## Cole este conteúdo:
      [Unit]
      Description=Servidor de Streaming de Câmeras Flask
      After=network.target
      
      [Service]
      User=orangepi
      WorkingDirectory=/home/orangepi/Desktop/python
      ExecStart=/home/orangepi/Desktop/python/start.sh
      Restart=always
      
      [Install]
      WantedBy=multi-user.target

## Ativar o serviço:
    sudo systemctl daemon-reload
    sudo systemctl enable flask_camera.service
    sudo systemctl start flask_camera.service

## USO

## EXECUÇÃO MANUAL
    python app.py

O servidor estará disponível em: http://seu_ip:5000

## COMANDOS DO SERVIÇO
    # Iniciar serviço
    sudo systemctl start flask_camera.service
    
    # Parar serviço
    sudo systemctl stop flask_camera.service
    
    # Ver status
    sudo systemctl status flask_camera.service
    
    # Ver logs
    journalctl -u flask_camera.service -f


## MONITORAMENTO DE TEMPERATURA
INDICADORES VISUAIS - CORES E LIMITES

🌡️ TEMPERATURA DA CPU
-    NORMAL (Verde): < 60°C
-    ALERTA (Laranja): 60°C - 70°C
-    CRÍTICO (Vermelho): > 70°C

⚙️ USO DA CPU
-    NORMAL (Verde): < 50%
-    ALERTA (Laranja): 50% - 80%
-    CRÍTICO (Vermelho): > 80%

💾 USO DA MEMÓRIA RAM
-    NORMAL (Verde): < 50%
-    ALERTA (Laranja): 50% - 80%
-    CRÍTICO (Vermelho): > 80%

Atualização automática a cada 5 segundos

## ROTAS DA API
- GET / - Interface principal com câmeras e temperatura
- GET /video_feed/<camera_id> - Stream de vídeo (1 ou 2)
- GET /temperature - JSON com dados de temperatura
- GET /temperature_page - Página dedicada de temperatura

## CARACTERÍSTICAS DA INTERFACE
- Design responsivo (mobile-friendly)
- Dark mode para melhor visualização
- Layout flexível para diferentes tamanhos de tela
- Indicadores visuais de status das câmeras
- Placeholder quando câmeras estão offline

## SOLUÇÃO DE PROBLEMAS

CÂMERAS OFFLINE:
- Verifique a conexão de rede e URLs RTSP
- As câmeras exibirão placeholder "CAMERA OFFLINE"
- Reconexão automática a cada 5 segundos

TEMPERATURA NÃO LIDA:
- Verifique permissões no arquivo /sys/class/thermal/thermal_zone0/temp
- Execute com privilégios se necessário

SERVIÇO NÃO INICIA:
- Verifique logs: journalctl -u flask_camera.service -f
- Confirme paths no arquivo de serviço systemd
- Valide permissões do script start.sh

## NOTAS
- Configure adequadamente as credenciais e URLs das câmeras
- Projeto para uso educacional e pessoal

## DEPENDÊNCIAS PRINCIPAIS
    Flask==3.0.3
    opencv-python==4.9.0.80
    psutil==5.9.6

## SEGURANÇA
-    Não exponha o serviço diretamente na internet sem proteção adequada
-    Utilize HTTPS em produção
-    Mantenha credenciais das câmeras em variáveis de ambiente
-    Atualize regularmente as dependências

