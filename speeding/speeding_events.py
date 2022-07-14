import json
from shapely.geometry import LineString
import pandas as pd
import geopandas as gpd
import argparse

def define_over_speed_class(over_speed):
    if over_speed < 0:
        return 'under_min_speed_limit'
    elif 0 < over_speed <= 20:
        return '+(0-20]'
    elif 20 < over_speed <= 40:
        return '+(20-40]'
    elif 40 < over_speed <= 60:
        return '+(40-60]'
    elif 60 < over_speed <= 80:
        return '+[60-80]'
    elif over_speed > 80:
        return '+[80+]'
    
def save_to_file(output_fname, events):
    with open(output_fname, 'w') as outfile:
        json.dump(events, outfile)
    
def read_route_file(route_fname):
    route_df = pd.read_json(route_fname)
    route_gdf = gpd.GeoDataFrame(route_df, geometry=gpd.points_from_xy(route_df.longitude, route_df.latitude))
    route_gdf = route_gdf.loc[:, ['timestamp', 'azimuth', 'speed', 'geometry']]
    return route_gdf

def read_road_graph_file(road_graph_fname):
    edges = []
    with open(road_graph_fname) as road_graph_file:
        road_graph = json.load(road_graph_file)

    for node in road_graph['nodes']:
        for neighbour in node['neighbours']:
            edges.append({
                'start_node_id': node['node_id'],
                'end_node_id': neighbour['id'],
                'azimuth': neighbour['azimuth'],
                'speed_limit': neighbour['speed_limit'],
                'min_speed_limit': neighbour['min_speed_limit']
            })
            
    edges_df = pd.DataFrame(edges)
        
    road_graph_df = pd.DataFrame({
        'node_id': [node['node_id'] for node in road_graph['nodes']],
        'latitude': [node['latitude'] for node in road_graph['nodes']],
        'longitude': [node['longitude'] for node in road_graph['nodes']],
    })
    
    edges_df = pd.merge(edges_df, road_graph_df, left_on='start_node_id', right_on='node_id')
    edges_df = edges_df.loc[:, ['start_node_id', 'latitude', 'longitude', 'end_node_id', 'azimuth', 'speed_limit', 'min_speed_limit']]
    edges_df.rename(columns={'latitude': 'start_lat', 'longitude': 'start_lon'}, inplace = True) 
    edges_df = pd.merge(edges_df, road_graph_df, left_on='end_node_id', right_on='node_id')
    edges_df = edges_df.loc[:, ['start_node_id', 'end_node_id', 'start_lat', 'start_lon', \
                                'latitude', 'longitude', 'azimuth', 'speed_limit', 'min_speed_limit']]
    edges_df.rename(columns={'latitude': 'end_lat', 'longitude': 'end_lon'}, inplace = True)
    edges_df = edges_df.assign(geometry=edges_df.apply( \
        lambda x: LineString([(x['start_lon'], x['start_lat']), (x['end_lon'], x['end_lat'])]), axis=1))
    edges_df = edges_df.loc[:, ['start_node_id', 'end_node_id', 'geometry', 'azimuth', 'speed_limit', 'min_speed_limit']]

    edges_gdf = gpd.GeoDataFrame(edges_df, geometry=edges_df.geometry)
    return edges_gdf

def combine_data_frames(route_gdf, edges_gdf, max_distance=5):
    joined_gdf = gpd.sjoin_nearest(route_gdf, edges_gdf, max_distance)
    
    def define_over_or_under_speed(row):
        if row['speed'] > row['speed_limit']:
            return row['speed'] - row['speed_limit']
        elif row['speed'] < row['min_speed_limit']:
            return row['speed'] - row['min_speed_limit']
        else:
            return None
    
    joined_gdf = joined_gdf \
                     .assign(over_speed=joined_gdf \
                     .apply(lambda x: define_over_or_under_speed(x), axis=1))
    joined_gdf = joined_gdf.assign(over_speed_class=joined_gdf.apply(lambda x: define_over_speed_class(x['over_speed']), axis=1))
    joined_gdf = joined_gdf.where(pd.notnull(joined_gdf), None)

    joined_gdf['timestamp'] = joined_gdf['timestamp'].astype(str)
    joined_gdf['geometry'] = joined_gdf['geometry'].astype(str)
    return joined_gdf
    
def speeding_events(route_fname, road_graph_fname, output_fname):
    route_gdf = read_route_file(route_fname)
    edges_gdf = read_road_graph_file(road_graph_fname)
    
    joined_gdf = combine_data_frames(route_gdf, edges_gdf)
    events = []
    for i, row in joined_gdf.iterrows():
        if row['over_speed_class'] != joined_gdf.iloc[i-1]['over_speed_class'] and row['over_speed_class'] != None:
            events.append(({'timestamp': row['timestamp'],\
                            'azimuth': row['azimuth_left'],\
                            'point': row['geometry'],\
                            'over_speed_class': row['over_speed_class']},\
                           joined_gdf \
                             .loc[:, ['timestamp', 'azimuth_left', 'speed', \
                                      'speed_limit', 'min_speed_limit', 'geometry', 'over_speed_class']] \
                             .rename(columns={'azimuth_left': 'azimuth'}) \
                             .iloc[i-5:i+1] \
                             .to_dict(orient="records")))

    save_to_file(output_fname, events)

def main():
    parser = argparse.ArgumentParser(description='Generate speeding events')
    parser.add_argument('route_fname', type=str, help='Input file with route of the car')
    parser.add_argument('road_graph_fname', type=str, help='Input file with road_graph of some area')
    parser.add_argument('output_fname', type=str, help='Output filename without file extension')
    args = parser.parse_args()
    speeding_events(args.route_fname, args.road_graph_fname, args.output_fname)
    
if __name__ == "__main__":
        main()