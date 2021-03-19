import csv, os
from vincenty import vincenty
from decimal import Decimal


# function for reading files
def read_gtfs_table(path_file, parse_coords=False):
    with open(path_file, 'r', encoding="utf-8-sig") as table:
        csv_reader = csv.DictReader(table)
        table = list()
        for row in csv_reader:
            if parse_coords:
                row['stop_lat'] = float(row['stop_lat'])
                row['stop_lon'] = float(row['stop_lon'])
            table.append(row)
        print('Finished reading table:', path_file)
        return table

stops = ()

stops = read_gtfs_table('C:/Users/Xristina/PycharmProjects/pythonProject/data/stops.txt', parse_coords=True)
stop_times = read_gtfs_table('C:/Users/Xristina/PycharmProjects/pythonProject/data/stop_times.txt')
shapes = read_gtfs_table('C:/Users/Xristina/PycharmProjects/pythonProject/data/shapes.txt', parse_coords=True)
trips = read_gtfs_table('C:/Users/Xristina/PycharmProjects/pythonProject/data/trips.txt')

# for each point from stop times find the corresponding coordinates at stops
# find the coordinates at shapes
# save the dist_trav

for ii, stop_time in enumerate(stop_times):
    if stop_time['stop_sequence'] == '1':
        stop_time['shape_dist_traveled'] = 0
    else:

        # for each stop from stop times find the corresponding coordinates at stops
        for stop in stops:
            if stop_time['stop_id'] == stop['stop_id']:

                # for the stop that matches the stop_time identify the shape_id
                for trip in trips:
                    if stop_time['trip_id'] == trip['trip_id']:

                        temp_index = []
                        temp_distance_value = []

                        # for each shape in shapes (corresponding to the shape_id that was identified above) calculate the distance from the stop
                        for i, shape in enumerate(shapes):
                            distance = vincenty((stop['stop_lat'], stop['stop_lon']), (shape['shape_pt_lat'], shape['shape_pt_lon']))*1000
                            if distance < 100:
                                temp_index.append(i)
                                temp_distance_value.append(distance)

                        # Find the shortest distance from the "temp" dict
                        minimum_distance = min(temp_distance_value)
                        minimum_distance_index = [j for j, x in enumerate(temp_distance_value) if x == minimum_distance]
                        stop_time['shape_dist_traveled'] = shapes[temp_index[minimum_distance_index[-1]]]['shape_dist_traveled']


keys = stop_times[0].keys()
with open(os.getcwd() + r'/results/new_test.csv', 'w', encoding="utf-8-sig", newline='') as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(stop_times)



