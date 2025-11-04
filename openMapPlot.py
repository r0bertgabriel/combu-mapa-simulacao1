"""openMapPlot.py

Carrega um arquivo OSM (XML) e plota suas geometrias usando geopandas/matplotlib.

Funcionamento:
- Tenta ler camadas suportadas pelo driver OSM do Fiona/GDAL via geopandas.read_file.
- Se falhar, tenta usar osmnx (ox.geometries_from_xml) como fallback.

Uso:
	python openMapPlot.py --file "map (2).osm" --out map_plot.png

Requisitos: geopandas, matplotlib. Para melhor compatibilidade recomenda-se instalar also osmnx.
"""

import argparse
import os
import sys
import warnings

import matplotlib.pyplot as plt

try:
	import geopandas as gpd
except Exception as e:
	print("Erro: geopandas não está instalado ou falhou ao importar:", e)
	print("Instale com: pip install geopandas")
	raise

import pandas as pd


def try_geopandas_read(osm_path):
	"""Tenta ler várias camadas do driver OSM via geopandas/fiona.
	Retorna um GeoDataFrame combinado ou raise se não conseguir.
	Foca apenas em áreas (polígonos).
	"""
	layers = [
		"multipolygons",
	]
	gdfs = []
	for layer in layers:
		try:
			g = gpd.read_file(osm_path, layer=layer)
			if g is None or len(g) == 0:
				continue
			# normalize geometry column name if needed
			if "geometry" not in g.columns and hasattr(g, 'geometry'):
				g.set_geometry('geometry', inplace=True)
			gdfs.append(g)
		except Exception:
			# leitura dessa layer falhou; ignora e tenta a próxima
			continue

	if not gdfs:
		raise RuntimeError("Nenhuma camada OSM foi lida via geopandas/gdal.")

	# concatena todos em um único GeoDataFrame (pode ter colunas diferentes)
	try:
		combined = pd.concat(gdfs, ignore_index=True, sort=False)
		combined = gpd.GeoDataFrame(combined, geometry='geometry')
		return combined
	except Exception as e:
		raise RuntimeError(f"Falha ao combinar GeoDataFrames: {e}")


def try_osmnx_read(osm_path):
	"""Tenta usar osmnx.geometries_from_xml como fallback.
	Retorna GeoDataFrame ou raise se não estiver disponível.
	Foca apenas em áreas (polígonos).
	"""
	try:
		import osmnx as ox
	except Exception as e:
		raise RuntimeError("osmnx não instalado ou falhou ao importar: " + str(e))

	# usa tags para obter áreas naturais, edificações e outras áreas
	tags = {
		'natural': True,
		'landuse': True,
		'building': True,
		'leisure': True,
		'amenity': True,
	}

	try:
		g = ox.geometries_from_xml(osm_path, tags)
		if g is None or len(g) == 0:
			raise RuntimeError("osmnx não produziu geometrias a partir do XML")
		return g
	except Exception as e:
		raise RuntimeError(f"osmnx falhou ao ler XML: {e}")


def plot_gdf(gdf, out_path=None, title=None):
	if gdf is None or len(gdf) == 0:
		raise ValueError("GeoDataFrame vazio; nada para plotar.")

	# Filtra apenas polígonos e multipolígonos (áreas)
	area_types = ['Polygon', 'MultiPolygon']
	gdf_areas = gdf[gdf.geometry.type.isin(area_types)].copy()
	
	if len(gdf_areas) == 0:
		print("Aviso: Nenhuma área (polígono) encontrada. Plotando todas as geometrias.")
		gdf_areas = gdf
	else:
		print(f"Plotando {len(gdf_areas)} áreas (polígonos)")

	# evita warnings de geometria inválida na plotagem
	with warnings.catch_warnings():
		warnings.simplefilter("ignore")
		# cria figura
		fig, ax = plt.subplots(figsize=(14, 14))
		
		# Plota as áreas
		gdf_areas.plot(ax=ax, facecolor='lightgreen', edgecolor='darkgreen', 
					   alpha=0.6, linewidth=1.5)

		# Obtém os limites do mapa
		bounds = gdf_areas.total_bounds  # [minx, miny, maxx, maxy]
		minx, miny, maxx, maxy = bounds
		
		# Adiciona grid com coordenadas
		ax.grid(True, linestyle='--', alpha=0.7, color='gray', linewidth=0.5)
		
		# Configura os ticks para mostrar coordenadas
		ax.set_xlabel('Longitude', fontsize=12, fontweight='bold')
		ax.set_ylabel('Latitude', fontsize=12, fontweight='bold')
		
		# Formata os ticks para mostrar coordenadas com precisão adequada
		ax.ticklabel_format(useOffset=False, style='plain')
		ax.tick_params(axis='both', which='major', labelsize=10)
		
		# Rotaciona os labels do eixo x para melhor legibilidade
		plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
		
		if title:
			ax.set_title(title, fontsize=14, fontweight='bold', pad=20)

		# Adiciona margem ao redor do plot
		x_margin = (maxx - minx) * 0.02
		y_margin = (maxy - miny) * 0.02
		ax.set_xlim(minx - x_margin, maxx + x_margin)
		ax.set_ylim(miny - y_margin, maxy + y_margin)

		if out_path:
			fig.savefig(out_path, dpi=300, bbox_inches='tight')
			print(f"Plot salvo em: {out_path}")
		else:
			plt.show()


def main():
	parser = argparse.ArgumentParser(description='Lê um arquivo OSM (XML) e plota geometrias usando geopandas.')
	parser.add_argument('--file', '-f', help='Caminho para o arquivo OSM (XML).', default='map (2).osm')
	parser.add_argument('--out', '-o', help='Caminho do arquivo de saída PNG. Se omitido, exibe na tela.', default='map_plot.png')
	args = parser.parse_args()

	osm_path = args.file
	out_path = args.out

	if not os.path.exists(osm_path):
		print(f"Arquivo não encontrado: {osm_path}")
		print("Arquivos no diretório atual:", os.listdir('.'))
		sys.exit(1)

	gdf = None
	# 1) tenta geopandas/fiona/gdal
	try:
		print("Tentando ler com geopandas/fiona (GDAL OSM driver)...")
		gdf = try_geopandas_read(osm_path)
		print(f"Lido com sucesso via geopandas: {len(gdf)} geometrias")
	except Exception as e:
		print("Leitura via geopandas falhou:", e)
		print("Tentando fallback com osmnx...")
		try:
			gdf = try_osmnx_read(osm_path)
			print(f"Lido com sucesso via osmnx: {len(gdf)} geometrias")
		except Exception as e2:
			print("Fallback osmnx também falhou:", e2)
			print("Por favor instale geopandas (e opcionalmente osmnx) ou converta o arquivo para um formato suportado.")
			sys.exit(1)

	# simplifica e garante GeoDataFrame
	if not isinstance(gdf, gpd.GeoDataFrame):
		try:
			gdf = gpd.GeoDataFrame(gdf, geometry='geometry')
		except Exception:
			pass

	title = f"Mapa: {os.path.basename(osm_path)}"
	plot_gdf(gdf, out_path=out_path, title=title)


if __name__ == '__main__':
	main()

