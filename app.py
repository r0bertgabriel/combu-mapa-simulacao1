"""app.py

Aplicação web interativa para visualização e análise de mapas OSM.
Permite zoom, adicionar pontos, calcular distâncias e exportar dados.

Uso:
	python app.py

Acesse: http://localhost:5000
"""

import json
import math

import geopandas as gpd
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

# Carrega o GeoDataFrame global
gdf_global = None

def load_osm_data(osm_file='map_filtered.osm'):
	"""Carrega dados OSM filtrados"""
	global gdf_global
	try:
		gdf = gpd.read_file(osm_file, layer='multipolygons')
		gdf_global = gdf
		return gdf
	except Exception as e:
		print(f"Erro ao carregar OSM: {e}")
		return None

def calculate_distance(lat1, lon1, lat2, lon2):
	"""
	Calcula distância entre dois pontos usando a fórmula de Haversine.
	Retorna distância em metros.
	"""
	R = 6371000  # Raio da Terra em metros
	
	phi1 = math.radians(lat1)
	phi2 = math.radians(lat2)
	delta_phi = math.radians(lat2 - lat1)
	delta_lambda = math.radians(lon2 - lon1)
	
	a = math.sin(delta_phi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda/2)**2
	c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
	
	distance = R * c
	return distance

@app.route('/')
def index():
	"""Página principal"""
	return render_template('index.html')

@app.route('/api/map-data')
def get_map_data():
	"""Retorna dados do mapa em formato GeoJSON"""
	if gdf_global is None:
		load_osm_data()
	
	if gdf_global is not None and len(gdf_global) > 0:
		# Converte para GeoJSON
		geojson = json.loads(gdf_global.to_json())
		return jsonify({
			'status': 'success',
			'data': geojson,
			'bounds': {
				'min_lon': -48.47,
				'max_lon': -48.43,
				'min_lat': -1.52,
				'max_lat': -1.47
			}
		})
	else:
		return jsonify({
			'status': 'error',
			'message': 'Não foi possível carregar os dados do mapa'
		})

@app.route('/api/calculate-distance', methods=['POST'])
def calculate_distance_api():
	"""Calcula distância entre dois pontos"""
	data = request.json
	
	if not data:
		return jsonify({
			'status': 'error',
			'message': 'Dados não fornecidos'
		})
	
	try:
		lat1 = float(data['lat1'])
		lon1 = float(data['lon1'])
		lat2 = float(data['lat2'])
		lon2 = float(data['lon2'])
		
		distance = calculate_distance(lat1, lon1, lat2, lon2)
		
		return jsonify({
			'status': 'success',
			'distance_meters': round(distance, 2),
			'distance_km': round(distance / 1000, 3)
		})
	except Exception as e:
		return jsonify({
			'status': 'error',
			'message': str(e)
		})

if __name__ == '__main__':
	print("🗺️  Carregando dados do mapa...")
	load_osm_data()
	print("✅ Dados carregados!")
	print("\n🌐 Iniciando servidor web...")
	print("📍 Acesse: http://localhost:5000")
	print("\nPressione CTRL+C para parar o servidor.\n")
	app.run(debug=True, host='0.0.0.0', port=5000)
