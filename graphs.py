import time
import zoneinfo
from classes import *
import sqlalchemy as sql
import getpass
import numpy as np
import drawsvg as draw


TZ = zoneinfo.ZoneInfo("Europe/Amsterdam")
MINUTE = 60
HOUR = MINUTE * MINUTE
PARTITIONS = 360
DISCONNECTED = "#717171"
INACTIVE = "#CCCCCC"
REQUESTING = "#C017B5"
HEATING = "#D78200"
ROOM_LIST = ["top_floor", "km_bedroom", "bathroom", "j_bedroom", "blue_room", "ground_floor"]
DAY_COLUMNS_RETURNED = "timecode, \
ground_floor_requesting, ground_floor_heating, \
bathroom_requesting, bathroom_heating, \
blue_room_requesting, blue_room_heating, \
j_bedroom_requesting, j_bedroom_heating, \
km_bedroom_requesting, km_bedroom_heating, \
top_floor_requesting, top_floor_heating"


def one_hour_history(room: str, engine: sql.Engine) -> str:
    start = time.time()
    with engine.begin() as db:
        command = sql.text("SELECT {DAY_COLUMNS_RETURNED} FROM direct_history ORDER BY timecode DESC LIMIT 3600")
        output = db.execute(command).all()
    end = time.time()
    print(f"Took {end - start:.3f} s to get {len(output)} entries.")

    output = [row._asdict() for row in output]

    now = time.time()
    past_hour = now - HOUR
    times = [row["timecode"]/10 for row in output]
    requests = [int(row[f"{room}_requesting"]) for row in output]
    heating = [int(row[f"{room}_heating"]) for row in output]

    time_hist, _ = np.histogram(times, PARTITIONS, (past_hour, now))
    req_hist, _  = np.histogram(times, PARTITIONS, (past_hour, now), weights=requests)
    heat_hist, _ = np.histogram(times, PARTITIONS, (past_hour, now), weights=heating)

    graph = draw.Drawing(360, 20)
    for number, timestamp, request, heat in zip(range(len(time_hist)), time_hist, req_hist, heat_hist):
        if not timestamp:
            graph.append(draw.Rectangle(number, 0, 1, 20, fill=DISCONNECTED, stroke=DISCONNECTED))
        elif heat:
            graph.append(draw.Rectangle(number, 0, 1, 20, fill=HEATING, stroke=HEATING))
        elif request:
            graph.append(draw.Rectangle(number, 0, 1, 20, fill=REQUESTING, stroke=REQUESTING))
        else:
            graph.append(draw.Rectangle(number, 0, 1, 20, fill=INACTIVE, stroke=INACTIVE))
    
    svg_output = graph.as_svg(header="")
    if not svg_output:
        raise ValueError("Drawing failed")
    return svg_output


def day_history(engine: sql.Engine) -> dict[str, str]:
    start = time.time()
    with engine.begin() as db:
        command = sql.text(f"SELECT {DAY_COLUMNS_RETURNED} FROM direct_history ORDER BY timecode DESC LIMIT 86400")
        output = db.execute(command).all()
    end = time.time()
    print(f"Took {end - start:.3f} s to get {len(output)} entries.")

    output = [row._asdict() for row in output]

    now = time.time()
    past_day = now - HOUR * 25
    times = [row["timecode"]/10 for row in output]
    output_list: dict[str, str] = {}
    for room in ROOM_LIST:
        requests = [int(row[f"{room}_requesting"]) for row in output]
        heating = [int(row[f"{room}_heating"]) for row in output]

        time_hist, _ = np.histogram(times, PARTITIONS, (past_day, now))
        req_hist, _  = np.histogram(times, PARTITIONS, (past_day, now), weights=requests)
        heat_hist, _ = np.histogram(times, PARTITIONS, (past_day, now), weights=heating)

        graph = draw.Drawing(360, 20)
        for number, timestamp, request, heat in zip(range(len(time_hist)), time_hist, req_hist, heat_hist):
            if not timestamp:
                graph.append(draw.Rectangle(number, 0, 1, 20, fill=DISCONNECTED, stroke=DISCONNECTED))
            elif heat:
                graph.append(draw.Rectangle(number, 0, 1, 20, fill=HEATING, stroke=HEATING))
            elif request:
                graph.append(draw.Rectangle(number, 0, 1, 20, fill=REQUESTING, stroke=REQUESTING))
            else:
                graph.append(draw.Rectangle(number, 0, 1, 20, fill=INACTIVE, stroke=INACTIVE))
        
        svg_output = graph.as_svg(header="")
        if not svg_output:
            raise ValueError("Drawing failed")
        output_list[room] = svg_output
    return output_list


if __name__ == '__main__':
    username = getpass.getuser()
    password = getpass.getpass("Database password: ")
    engine = sql.create_engine(f"postgresql+psycopg2://{username}:{password}@localhost/heating")
    roomname = "km_bedroom"
    print(one_hour_history(roomname, engine))



# print(time.localtime(output[0]["timecode"]/10))
# dt = datetime.datetime.fromtimestamp(output[0]["timecode"]/10)
# now = datetime.datetime.now(tz=TZ)
# delta = datetime.timedelta(hours=1)
# minushour = now.replace(hour=0, minute=0, second=0, microsecond=0)
# print(time1)
# # delta = datetime.timedelta(minutes=24*60*57+14*60)
# # newdt = dt - delta
# time2 = time1.replace(month=3, day=26)
# print(time2)
# delta = time1 - time2
# print(delta)
# timestamp1 = time1.timestamp()
# print(timestamp1)
# timestamp2 = time2.timestamp()
# print(timestamp2)
# delta2 = datetime.timedelta(seconds=timestamp1-timestamp2)
# print(delta2)