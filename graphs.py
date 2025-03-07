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
ROOM_LIST = [
    "ground_floor",
    "bathroom",
    "blue_room",
    "j_bedroom",
    "km_bedroom",
    "top_floor",
]
ROOM_LIST_NUMBERS = [1, 3, 5, 7, 9, 11]
DAY_COLUMNS_RETURNED = "timecode, \
ground_floor_requesting, ground_floor_heating, \
bathroom_requesting, bathroom_heating, \
blue_room_requesting, blue_room_heating, \
j_bedroom_requesting, j_bedroom_heating, \
km_bedroom_requesting, km_bedroom_heating, \
top_floor_requesting, top_floor_heating"


def one_hour_history(room: str, engine: sql.Engine) -> str:
    """
    Graph the past one hour of activity of a room and return it as an svg.
    """
    start = time.time()
    with engine.begin() as db:
        command = sql.text(
            "SELECT * FROM direct_history ORDER BY timecode DESC LIMIT 3600"
        )
        output = db.execute(command)
    end = time.time()

    output = output.mappings().all()
    print(f"Took {end - start:.3f} s to get {len(output)} entries.")

    now = time.time()
    past_hour = now - HOUR
    times = [row["timecode"] / 10 for row in output]
    # boolean values are stored as int (0 or 1)
    requests = [int(row[f"{room}_requesting"]) for row in output]
    heating = [int(row[f"{room}_heating"]) for row in output]

    # db entries are in a histogram of the past hour
    # timestamps more than an hour old don't get used in the graph
    time_hist, _ = np.histogram(times, PARTITIONS, (past_hour, now))
    req_hist, _ = np.histogram(times, PARTITIONS, (past_hour, now), weights=requests)
    heat_hist, _ = np.histogram(times, PARTITIONS, (past_hour, now), weights=heating)

    graph = draw.Drawing(360, 20)
    # draw 360 colored rectangles
    for number, timestamp, request, heat in zip(
        range(len(time_hist)), time_hist, req_hist, heat_hist
    ):
        if not timestamp:
            graph.append(
                draw.Rectangle(number, 0, 1, 20, fill=DISCONNECTED, stroke=DISCONNECTED)
            )
        elif heat:
            graph.append(draw.Rectangle(number, 0, 1, 20, fill=HEATING, stroke=HEATING))
        elif request:
            graph.append(
                draw.Rectangle(number, 0, 1, 20, fill=REQUESTING, stroke=REQUESTING)
            )
        else:
            graph.append(
                draw.Rectangle(number, 0, 1, 20, fill=INACTIVE, stroke=INACTIVE)
            )

    svg_output = graph.as_svg(header="")
    if not svg_output:
        raise ValueError("Drawing failed")
    return svg_output


def day_history(engine: sql.Engine) -> dict[str, str]:
    """
    Graph the past day of activity of all rooms and return them as a dict of svgs.
    """
    start = time.time()
    with engine.begin() as db:
        command = sql.text(
            f"SELECT {DAY_COLUMNS_RETURNED} FROM direct_history ORDER BY timecode DESC LIMIT 86400"
        )
        output = db.execute(command)
    end = time.time()

    output = output.all()
    print(f"Took {end - start:.3f} s to get {len(output)} entries.")

    now = time.time()
    past_day = now - HOUR * 25
    times = [row[0] / 10 for row in output]
    output_list: dict[str, str] = {}
    for room, roomname in zip(ROOM_LIST_NUMBERS, ROOM_LIST):
        requests = [int(row[room]) for row in output]
        heating = [int(row[room + 1]) for row in output]

        time_hist, _ = np.histogram(times, PARTITIONS, (past_day, now))
        req_hist, _ = np.histogram(times, PARTITIONS, (past_day, now), weights=requests)
        heat_hist, _ = np.histogram(times, PARTITIONS, (past_day, now), weights=heating)

        graph = draw.Drawing(360, 20)
        for number, timestamp, request, heat in zip(
            range(len(time_hist)), time_hist, req_hist, heat_hist
        ):
            if not timestamp:
                graph.append(
                    draw.Rectangle(
                        number, 0, 1, 20, fill=DISCONNECTED, stroke=DISCONNECTED
                    )
                )
            elif heat:
                graph.append(
                    draw.Rectangle(number, 0, 1, 20, fill=HEATING, stroke=HEATING)
                )
            elif request:
                graph.append(
                    draw.Rectangle(number, 0, 1, 20, fill=REQUESTING, stroke=REQUESTING)
                )
            else:
                graph.append(
                    draw.Rectangle(number, 0, 1, 20, fill=INACTIVE, stroke=INACTIVE)
                )

        svg_output = graph.as_svg(header="")
        if not svg_output:
            raise ValueError("Drawing failed")
        output_list[roomname] = svg_output
    print(f"Total time: {time.time() - start:.3f} s.")
    return output_list


# for testing:
# if __name__ == "__main__":
#     username = getpass.getuser()
#     password = getpass.getpass("Database password: ")
#     engine = sql.create_engine(
#         f"postgresql+psycopg2://{username}:{password}@localhost/heating"
#     )
