import csv, os
from vincenty import vincenty


# function for reading files
def read_gtfs_table(path_file, stops=False, shapes=False):
    """This is the main function for reading the files stops, stop_tiems, shapes and trips for GTFS.
    :param path_file str: the path of the file
    :param stops bool: if the file is stops, the variable takes the value True. When reading the stops file, we convert the values of the fields stop_lat and stop_lon to floats.
    :param shapes bool: if the file is shapes, the variable takes the value True. When reading the shapes file, we convert the values of the fields stop_lat, stop_lon and shape_dist_traveledto floats.
    :return: this function returns a list of dictionaries. The dictionaries correspond to rows from the table.
    """
    with open(path_file, 'r', encoding="utf-8-sig") as table:
        csv_reader = csv.DictReader(table)
        table = list()
        for row in csv_reader:
            if stops:
                # convert latitude and longitude of stop coordinates to floats
                row['stop_lat'] = float(row['stop_lat'])
                row['stop_lon'] = float(row['stop_lon'])

            elif shapes:
                # convert latitude and longitude of coordinates of shape points to floats, as well as shape_dist_traveled from shapes
                row['shape_pt_lat'] = float(row['shape_pt_lat'])
                row['shape_pt_lon'] = float(row['shape_pt_lon'])
                row['shape_dist_traveled'] = float(row['shape_dist_traveled'])

            # each table is inserted in table lst variable, where in each index there is a dictionary with each row from the original table
            table.append(row)
        print('Finished reading table:', path_file)
        # the function returns the table list
        return table

# read files
stops = read_gtfs_table('C:/Users/aetho/OneDrive - AETHON Engineering/Data/Δήμος Βάρης-Βούλας-Βουλιαγμένης/VVV_GTFS/stops.txt', stops=True)
stop_times = read_gtfs_table('C:/Users/aetho/OneDrive - AETHON Engineering/Data/Δήμος Βάρης-Βούλας-Βουλιαγμένης/VVV_GTFS/stop_times.txt')
shapes = read_gtfs_table('C:/Users/aetho/OneDrive - AETHON Engineering/Data/Δήμος Βάρης-Βούλας-Βουλιαγμένης/VVV_GTFS/shapes.txt', shapes=True)
trips = read_gtfs_table('C:/Users/aetho/OneDrive - AETHON Engineering/Data/Δήμος Βάρης-Βούλας-Βουλιαγμένης/VVV_GTFS/tripsv.txt')

# first we find the first value of stop_sequence of each trip from stop_times
first_stop_sequence_per_trip = []
examined_trips = []
for stop_time in stop_times:
    if stop_time['trip_id'] not in examined_trips:
        # store each trip so that we do not examine it again
        # adn for that trip find all stop_sequences
        examined_trips.append(stop_time['trip_id'])
        stop_sequences = []
        for stop_time2 in stop_times:
            if stop_time2['trip_id'] == stop_time['trip_id']:
                # store all the stop_times.stop_sequences from each trip
                stop_sequences.append(stop_time['stop_sequence'])

        # we find the lowest value of all the stop_sequences of each trip and store them along with the corresponding trip_id
        min_stop_sequence = min(stop_sequences)
        first_stop_sequence_per_trip.append({'trip_id': stop_time['trip_id'], 'min_stop_sequence': min_stop_sequence})

for ii, stop_time in enumerate(stop_times):
    # find the minimum value of stop_sequence for the trip in the current row of stop_times
    # if the stop_sequence of that row is the minimum of the trip, shape_dist_traveled will be zero
    for value_first_stop_sequence_per_trip in first_stop_sequence_per_trip:
        if value_first_stop_sequence_per_trip['trip_id'] == stop_time['trip_id']:
            min_stop_sequence = value_first_stop_sequence_per_trip['min_stop_sequence']
    if stop_time['stop_sequence'] == min_stop_sequence:
        stop_time['shape_dist_traveled'] = 0
    else:
        for stop in stops:
            # for each stop from stop times find at stops table to get the coordinates
            if stop_time['stop_id'] == stop['stop_id']:
                for trip in trips:
                    # for the trip in the row at stop_times identify the shape_id
                    if stop_time['trip_id'] == trip['trip_id']:
                        temp_index = []
                        temp_distance_value = []
                        temp_dist_traveled = []
                        for i, shape in enumerate(shapes):
                            # for each shape in shapes find those with the shape_id corresponding to the trip of the row in stop_times
                            if shape['shape_id'] == trip['shape_id']:
                                # for each point with the corresponding shape_id calculate the distance from the stop
                                distance = vincenty((stop['stop_lat'], stop['stop_lon']), (shape['shape_pt_lat'], shape['shape_pt_lon']))*1000
                                # if the distance is smaller that 1 meter
                                if distance < 1:
                                    # temp_distance_value.append(distance)
                                    temp_dist_traveled.append(shape['shape_dist_traveled'])

                        # sort the above shape_dist_traveled
                        sorted_temp_dist_traveled = sorted(temp_dist_traveled)

                        # check the sorted_temp_dist_traveled (ascending order) and insert the smallest shape_dist_traveled, which is greater than the previous shapes.shape_dist_traveled
                        # we do this, because there are some cases where the bus stops in a stop that had stopped also before.
                        # the second time the shape_dist_traveled should be larger.
                        for dist in sorted_temp_dist_traveled:
                            if dist > stop_times[ii - 1]['shape_dist_traveled']:
                                stop_time['shape_dist_traveled'] = dist
                                break
# save the stop_times with the shape_dist_traveled field completed
keys = stop_times[0].keys()
with open(os.getcwd() + r'/results/stop_times_vvv.csv', 'w', encoding="utf-8-sig", newline='') as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(stop_times)