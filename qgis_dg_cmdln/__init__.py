from pathlib import Path

from qgis.core import QgsProject, QgsVectorLayer

from .dg_cmdln import handle # currently not used; transparently made available from here (qgis_dg_cmdln)


def stub(iface, data):
	# iface.addVectorLayer(data, 'layer', 'ogr')
	return str(data)
	if data['type'] == 'add layers from file':
		# return data['title']
		# root = QgsProject.instance().layerTreeRoot()
		# group = root.addGroup(data['title'])
		# return 'Fine'
		# for layer in data['layers']:
		# vl = QgsVectorLayer(str(
		# 	Path(r'D:\iitbgis\work\Transport\data\workspace') / data['title']
		# ), data['title'], 'ogr')
			# return str(','.join([f.name() for f in vl.fields()]))
		# group.addLayer(vl)
		for layer in data['layers']:
			# vl = QgsVectorLayer(layer['filepath'], layer['title'], 'ogr')
			# root.addLayer(vl)
			iface.addVectorLayer(layer['filepath'], layer['title'], 'ogr')