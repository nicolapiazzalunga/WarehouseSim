## warehouse_sim/core/reservation.py
"""
Reservation table for time-extended spatial and edge conflict avoidance.
"""

class ReservationTable:
    def __init__(self):
        self.cell_reservations = {}  # (x, y) -> {time: robot_id}
        self.edge_reservations = set()  # ((from_x, from_y), (to_x, to_y), time)

    def is_reserved(self, x, y, time):
        return time in self.cell_reservations.get((x, y), {})

    def is_edge_reserved(self, from_pos, to_pos, time):
        return (to_pos, from_pos, time) in self.edge_reservations

    def reserve_cell(self, x, y, time, robot_id=None):
        self.cell_reservations.setdefault((x, y), {})[time] = robot_id

    def reserve_path(self, path, robot_id=None):
        for t, (x, y) in enumerate(path):
            self.reserve_cell(x, y, t, robot_id)

    def reserve_goal(self, x, y, t_start, duration, robot_id=None):
        for t in range(t_start, t_start + duration):
            self.reserve_cell(x, y, t, robot_id)

    def reserve_goal_forever(self, x, y, start_time, robot_id=None):
        for t in range(start_time, start_time + 50):  # Default duration = 50
            self.reserve_cell(x, y, t, robot_id)

    def reserve_edges(self, path):
        for t in range(1, len(path)):
            from_pos = path[t - 1]
            to_pos = path[t]
            self.edge_reservations.add((from_pos, to_pos, t))

    def reserve_edge(self, from_pos, to_pos, time, robot_id=None):
        self.edge_reservations.add((from_pos, to_pos, time))