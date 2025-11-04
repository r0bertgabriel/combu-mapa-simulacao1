#!/bin/bash
# Script para gerenciar a aplicação web do mapa interativo

case "$1" in
  start)
    echo "🚀 Iniciando servidor..."
    cd /home/br4b0/Desktop/research/CONTINUCAO-COMBU-PYTHON
    nohup python app.py > app.log 2>&1 &
    sleep 2
    echo "✅ Servidor iniciado!"
    echo "📍 Acesse: http://localhost:5000"
    ;;
  
  stop)
    echo "🛑 Parando servidor..."
    pkill -f "python app.py"
    echo "✅ Servidor parado!"
    ;;
  
  status)
    if pgrep -f "python app.py" > /dev/null; then
      echo "✅ Servidor está RODANDO"
      echo "📍 Acesse: http://localhost:5000"
    else
      echo "❌ Servidor está PARADO"
    fi
    ;;
  
  logs)
    echo "📋 Últimas linhas do log:"
    tail -f /home/br4b0/Desktop/research/CONTINUCAO-COMBU-PYTHON/app.log
    ;;
  
  restart)
    echo "🔄 Reiniciando servidor..."
    $0 stop
    sleep 1
    $0 start
    ;;
  
  *)
    echo "Uso: $0 {start|stop|status|logs|restart}"
    echo ""
    echo "Comandos:"
    echo "  start   - Inicia o servidor"
    echo "  stop    - Para o servidor"
    echo "  status  - Verifica se o servidor está rodando"
    echo "  logs    - Mostra os logs do servidor"
    echo "  restart - Reinicia o servidor"
    exit 1
    ;;
esac
