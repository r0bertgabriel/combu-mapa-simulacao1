# 🗺️ Aplicação Web Interativa - Mapa OSM

Aplicação web interativa para visualização e análise de dados OpenStreetMap (OSM).

## 🎯 Funcionalidades

### ✅ Visualização Interativa
- Mapa interativo com zoom e navegação
- Visualização de áreas (polígonos) do arquivo OSM filtrado
- Grade de coordenadas com valores de latitude e longitude
- Bounding box destacado da área de interesse

### ✅ Gerenciamento de Pontos
- **Adicionar pontos**: Clique no mapa para adicionar pontos personalizados
- **Nomear pontos**: Cada ponto pode ter um nome personalizado
- **Visualizar coordenadas**: Latitude e longitude de cada ponto
- **Selecionar pontos**: Clique nos pontos para selecioná-los
- **Excluir pontos**: Remova pontos individuais ou todos de uma vez
- **Zoom para ponto**: Navegue rapidamente até um ponto específico

### ✅ Cálculo de Distâncias
- Selecione dois pontos quaisquer no mapa
- Calcule a distância em metros e quilômetros
- Visualização de linha conectando os dois pontos
- Fórmula de Haversine para cálculo preciso

### ✅ Exportação de Dados
- **Exportar JSON**: Salve todos os pontos em formato JSON
- **Exportar CSV**: Salve todos os pontos em formato CSV
- Inclui ID, nome, latitude e longitude de cada ponto

### ✅ Interface Amigável
- Barra de status mostrando coordenadas do mouse em tempo real
- Indicador de nível de zoom atual
- Sidebar com todas as ferramentas organizadas
- Design responsivo e moderno
- Atalhos de teclado (ESC para cancelar, Enter para confirmar)

## 🚀 Como Usar

### 1. Inicie o servidor
```bash
python app.py
```

### 2. Acesse no navegador
Abra: http://localhost:5000

### 3. Interaja com o mapa

#### Adicionar Pontos:
1. Clique em "Ativar Modo de Adição"
2. Clique no mapa onde deseja adicionar o ponto
3. Digite um nome para o ponto
4. Clique em "Salvar"

#### Calcular Distância:
1. Clique em dois pontos na lista lateral (botão "Selecionar")
2. Clique em "Calcular Distância"
3. Veja o resultado e a linha conectando os pontos

#### Exportar Dados:
1. Adicione os pontos desejados
2. Clique em "Exportar Pontos (JSON)" ou "Exportar Pontos (CSV)"
3. O arquivo será baixado automaticamente

## 📋 Requisitos

- Python 3.x
- Flask
- geopandas
- Arquivo `map_filtered.osm` no diretório

## 🛠️ Tecnologias Utilizadas

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript
- **Mapas**: Leaflet.js
- **Dados**: GeoJSON, OpenStreetMap

## 📦 Estrutura de Arquivos

```
.
├── app.py                    # Servidor Flask
├── map_filtered.osm          # Dados OSM filtrados
├── templates/
│   └── index.html            # Interface web
└── README_APP.md             # Este arquivo
```

## 🎨 Características da Interface

- **Design moderno**: Gradientes e sombras suaves
- **Cores intuitivas**: Verde para áreas, azul para pontos, vermelho para bbox
- **Responsivo**: Funciona em desktop e mobile
- **Acessível**: Botões grandes e labels claros

## 🔧 API Endpoints

- `GET /` - Página principal
- `GET /api/map-data` - Retorna dados do mapa em GeoJSON
- `POST /api/calculate-distance` - Calcula distância entre dois pontos

## 💡 Dicas

- Use o scroll do mouse para zoom
- Arraste o mapa para navegar
- Pressione ESC para cancelar ações
- Coordenadas são mostradas na barra inferior
- Pontos selecionados ficam amarelos

## 🐛 Solução de Problemas

**Mapa não carrega?**
- Verifique se o arquivo `map_filtered.osm` existe
- Verifique a conexão com a internet (para tiles do OSM)

**Erro ao calcular distância?**
- Certifique-se de ter selecionado exatamente 2 pontos

**Servidor não inicia?**
- Verifique se a porta 5000 está disponível
- Instale as dependências: `pip install flask geopandas`

---

Desenvolvido com ❤️ para análise de dados geoespaciais
