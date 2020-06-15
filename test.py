from influxdb import InfluxDBClient
influx_client = InfluxDBClient('localhost',8086)
influx_client.query('show databases')

influx_client.query('show measurements', database='arista')

points = influx_client.query("""SELECT "in_octets" FROM "ifcounters" WHERE ("source" = 'ceos2' AND "name"='Ethernet2') ORDER BY DESC LIMIT 3""", database='arista').get_points()
for point in points:
    print(point['in_octets'])

