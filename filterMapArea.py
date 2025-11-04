"""filterMapArea.py

Filtra dados de um arquivo OSM por uma área geográfica específica (bounding box).
Cria um novo arquivo OSM filtrado e gera uma visualização.

Uso:
	python filterMapArea.py
"""

import argparse
import os
import sys
import warnings
import xml.etree.ElementTree as ET

import matplotlib.pyplot as plt

try:
	import geopandas as gpd
except Exception as e:
	print("Erro: geopandas não está instalado ou falhou ao importar:", e)
	print("Instale com: pip install geopandas")
	raise

import pandas as pd
from shapely.geometry import Point, box


def filter_osm_by_bbox(input_osm, output_osm, min_lon, max_lon, min_lat, max_lat):
	"""
	Filtra um arquivo OSM XML mantendo apenas os elementos dentro da bounding box especificada.
	
	Args:
		input_osm: Caminho do arquivo OSM de entrada
		output_osm: Caminho do arquivo OSM de saída
		min_lon, max_lon: Longitude mínima e máxima
		min_lat, max_lat: Latitude mínima e máxima
	"""
	print(f"\nFiltrando arquivo OSM...")
	print(f"Bounding Box: lon[{min_lon}, {max_lon}], lat[{min_lat}, {max_lat}]")
	
	# Parse do XML
	tree = ET.parse(input_osm)
	root = tree.getroot()
	
	# Atualiza o elemento bounds
	bounds = root.find('bounds')
	if bounds is not None:
		bounds.set('minlat', str(min_lat))
		bounds.set('maxlat', str(max_lat))
		bounds.set('minlon', str(min_lon))
		bounds.set('maxlon', str(max_lon))
	
	# Coleta IDs dos nós que estão dentro da bbox
	valid_node_ids = set()
	nodes_to_remove = []
	
	for node in root.findall('node'):
		node_id = node.get('id')
		lat = float(node.get('lat'))
		lon = float(node.get('lon'))
		
		if min_lon <= lon <= max_lon and min_lat <= lat <= max_lat:
			valid_node_ids.add(node_id)
		else:
			nodes_to_remove.append(node)
	
	# Remove nós fora da bbox
	for node in nodes_to_remove:
		root.remove(node)
	
	print(f"Nós dentro da área: {len(valid_node_ids)}")
	
	# Filtra ways e relations que usam apenas nós válidos
	ways_to_remove = []
	valid_way_ids = set()
	
	for way in root.findall('way'):
		way_id = way.get('id')
		node_refs = [nd.get('ref') for nd in way.findall('nd')]
		
		# Mantém o way se pelo menos 50% dos seus nós estão na bbox
		valid_refs = [ref for ref in node_refs if ref in valid_node_ids]
		if len(valid_refs) >= len(node_refs) * 0.5:
			valid_way_ids.add(way_id)
		else:
			ways_to_remove.append(way)
	
	for way in ways_to_remove:
		root.remove(way)
	
	print(f"Ways dentro da área: {len(valid_way_ids)}")
	
	# Filtra relations
	relations_to_remove = []
	
	for relation in root.findall('relation'):
		members = relation.findall('member')
		valid_members = []
		
		for member in members:
			member_type = member.get('type')
			member_ref = member.get('ref')
			
			if member_type == 'node' and member_ref in valid_node_ids:
				valid_members.append(member)
			elif member_type == 'way' and member_ref in valid_way_ids:
				valid_members.append(member)
		
		# Mantém relation se tiver membros válidos
		if len(valid_members) == 0:
			relations_to_remove.append(relation)
	
	for relation in relations_to_remove:
		root.remove(relation)
	
	# Salva o arquivo filtrado
	tree.write(output_osm, encoding='UTF-8', xml_declaration=True)
	print(f"\nArquivo filtrado salvo em: {output_osm}")
	
	return output_osm


def load_and_plot_filtered_osm(osm_path, output_image, bbox):
	"""
	Carrega o arquivo OSM filtrado e gera uma visualização focada em áreas.
	"""
	min_lon, max_lon, min_lat, max_lat = bbox
	
	print(f"\nCarregando dados do arquivo filtrado...")
	
	# Tenta ler multipolygons
	layers = ["multipolygons"]
	gdfs = []
	
	for layer in layers:
		try:
			g = gpd.read_file(osm_path, layer=layer)
			if g is None or len(g) == 0:
				continue
			if "geometry" not in g.columns and hasattr(g, 'geometry'):
				g.set_geometry('geometry', inplace=True)
			gdfs.append(g)
			print(f"Camada '{layer}': {len(g)} geometrias")
		except Exception as e:
			print(f"Falha ao ler camada '{layer}': {e}")
			continue
	
	if not gdfs:
		print("Nenhuma geometria encontrada. Tentando ler todas as camadas disponíveis...")
		try:
			# Tenta ler qualquer camada disponível
			from fiona import listlayers
			available_layers = listlayers(osm_path)
			print(f"Camadas disponíveis: {available_layers}")
			
			for layer in available_layers:
				try:
					g = gpd.read_file(osm_path, layer=layer)
					if g is not None and len(g) > 0:
						gdfs.append(g)
						print(f"Camada '{layer}': {len(g)} geometrias")
				except:
					continue
		except Exception as e:
			print(f"Erro ao listar camadas: {e}")
	
	if not gdfs:
		print("AVISO: Nenhuma geometria encontrada no arquivo filtrado.")
		print("Criando visualização da bounding box...")
		gdf = gpd.GeoDataFrame({'geometry': [box(min_lon, min_lat, max_lon, max_lat)]}, 
								crs='EPSG:4326')
	else:
		# Combina todas as geometrias
		combined = pd.concat(gdfs, ignore_index=True, sort=False)
		gdf = gpd.GeoDataFrame(combined, geometry='geometry')
		print(f"\nTotal de geometrias carregadas: {len(gdf)}")
	
	# Filtra apenas polígonos
	area_types = ['Polygon', 'MultiPolygon']
	gdf_areas = gdf[gdf.geometry.type.isin(area_types)].copy()
	
	if len(gdf_areas) == 0:
		print("Nenhum polígono encontrado. Usando todas as geometrias.")
		gdf_areas = gdf
	else:
		print(f"Plotando {len(gdf_areas)} áreas (polígonos)")
	
	# Cria a visualização
	with warnings.catch_warnings():
		warnings.simplefilter("ignore")
		fig, ax = plt.subplots(figsize=(14, 14))
		
		if len(gdf_areas) > 0:
			# Plota as áreas
			gdf_areas.plot(ax=ax, facecolor='lightgreen', edgecolor='darkgreen', 
						   alpha=0.6, linewidth=1.5)
		
		# Define os limites exatos da bbox
		ax.set_xlim(min_lon, max_lon)
		ax.set_ylim(min_lat, max_lat)
		
		# Adiciona grid com coordenadas
		ax.grid(True, linestyle='--', alpha=0.7, color='gray', linewidth=0.5)
		
		# Configura os eixos
		ax.set_xlabel('Longitude', fontsize=12, fontweight='bold')
		ax.set_ylabel('Latitude', fontsize=12, fontweight='bold')
		ax.ticklabel_format(useOffset=False, style='plain')
		ax.tick_params(axis='both', which='major', labelsize=10)
		plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
		
		# Título
		title = f"Área Filtrada\nLon: [{min_lon}, {max_lon}] | Lat: [{min_lat}, {max_lat}]"
		ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
		
		# Adiciona retângulo da bounding box
		from matplotlib.patches import Rectangle
		rect = Rectangle((min_lon, min_lat), max_lon - min_lon, max_lat - min_lat,
						 linewidth=2, edgecolor='red', facecolor='none', linestyle='--',
						 label='Bounding Box')
		ax.add_patch(rect)
		ax.legend(loc='upper right')
		
		# Salva
		fig.savefig(output_image, dpi=300, bbox_inches='tight')
		print(f"\nImagem salva em: {output_image}")
		plt.close()


def main():
	# Parâmetros
	input_osm = "map (2).osm"
	output_osm = "map_filtered.osm"
	output_image = "map_filtered_areas.png"
	
	# Bounding box: lon[-48.47, -48.43], lat[-1.52, -1.47]
	min_lon = -48.47
	max_lon = -48.43
	min_lat = -1.52
	max_lat = -1.47
	bbox = (min_lon, max_lon, min_lat, max_lat)
	
	if not os.path.exists(input_osm):
		print(f"Arquivo não encontrado: {input_osm}")
		sys.exit(1)
	
	# Filtra o arquivo OSM
	filtered_osm = filter_osm_by_bbox(input_osm, output_osm, min_lon, max_lon, min_lat, max_lat)
	
	# Gera a visualização
	load_and_plot_filtered_osm(filtered_osm, output_image, bbox)
	
	print("\n✅ Processo concluído!")
	print(f"   - Dataset filtrado: {output_osm}")
	print(f"   - Imagem gerada: {output_image}")


if __name__ == '__main__':
	main()
