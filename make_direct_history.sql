CREATE TABLE direct_history (
timecode bigint,
ground_floor_requesting boolean, ground_floor_heating boolean, ground_floor_time_heating integer, ground_floor_delay smallint, 
bathroom_requesting boolean, bathroom_heating boolean, bathroom_time_heating integer, bathroom_delay smallint, 
blue_room_requesting boolean, blue_room_heating boolean, blue_room_time_heating integer, blue_room_delay smallint, 
j_bedroom_requesting boolean, j_bedroom_heating boolean, j_bedroom_time_heating integer, j_bedroom_delay smallint, 
km_bedroom_requesting boolean, km_bedroom_heating boolean, km_bedroom_time_heating integer, km_bedroom_delay smallint, 
top_floor_requesting boolean, top_floor_heating boolean, top_floor_time_heating integer, top_floor_delay smallint
);