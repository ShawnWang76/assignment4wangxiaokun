import os
import math
import pandas as pd
from datetime import datetime, timedelta
from pyecharts import charts, options

STR_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"

def save_csv_tosql(filename, Entity, db):
	path = os.path.join(os.getcwd(), 'FilePlace', filename)
	entity_list = []

	for _, row in pd.read_csv(path, encoding='iso8859_2').iterrows():
		time = datetime.strptime(row['time'], STR_DATETIME_FORMAT)
		updated = datetime.strptime(row['updated'], STR_DATETIME_FORMAT)
		entity_list.append(Entity(time = time,
		                          latitude = row['latitude'],
		                          longitude = row['longitude'],
		                          depth = row['depth'],
		                          mag = row['mag'],
		                          magType = row['magType'],
		                          nst = row['nst'],
		                          gap = row['gap'],
		                          dmin = row['dmin'],
		                          rms = row['rms'],
		                          net = row['net'],
		                          id = row['id'],
		                          updated = updated,
		                          place = row['place'],
		                          type = row['type'],
		                          horizontalError = row['horizontalError'],
		                          depthError = row['depthError'],
		                          magError = row['magError'],
		                          magNst = row['magNst'],
		                          status = row['status'],
		                          locationSource = row['locationSource'],
		                          magSource = row['magSource']))
	for entity in entity_list:
		result = Entity.query.filter_by(id=entity.id).first()
		if result:
			pass
		else:
			db.session.add(entity)
	return db.session.commit()

def cal_distence(x, y, r=6371.0):
	lat1 = math.radians(x[0])
	lon1 = math.radians(x[1])
	lat2 = math.radians(y[0])
	lon2 = math.radians(y[1])

	dlon = lon2 - lon1
	dlat = lat2 - lat1

	a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
	c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
	return c * r

def get_viz(method, label, data):
	if method == 'bar':
		viz = charts.Bar()
		viz.add_xaxis(label)
		viz.add_yaxis('', data)
	elif method == 'pie':
		data = [list(d) for d in zip(label, data)]
		viz = charts.Pie()
		viz.add('', data)
	return viz

def get_sca(results):
	viz = charts.Scatter()
	x_data = [res.mag for res in results]
	y_data = [res.depth for res in results]
	viz.add_xaxis(x_data)
	viz.add_yaxis('xaxis:mag yaxis:depth', y_data)
	return viz