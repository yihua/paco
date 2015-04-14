import timestream

#  Rules:
#    A packet embedded in time within another one has zero cost
#    The last packet is responsible for the tail time

DEMOTE_TIMER = 10

idle_threshold = 10

uplink_power = 1.189
downlink_power = 0.43778

connected_power = 1.450
baseline_power = 0.800

ACTIVE_COST = connected_power - baseline_power + downlink_power
PASSIVE_COST = connected_power - baseline_power

def find_power_cost(timeline):
    timeline.sortme()

    i = 0
    tl_len = len(timeline)

    last_packet = None
    for packet in timeline:

        if last_packet == None:
            last_packet = packet
            continue

        if packet.start_time > last_packet.end_time + DEMOTE_TIMER:
            last_packet_power = (last_packet.end_time - \
                    last_packet.start_time) * ACTIVE_COST + DEMOTE_TIMER * PASSIVE_COST
        elif  packet.start_time > last_packet.end_time:
            last_packet_power = (last_packet.end_time - \
                    last_packet.start_time) * ACTIVE_COST + \
                    (packet.start_time - last_packet.end_time) * PASSIVE_COST
        elif packet.end_time < last_packet.end_time:
            # If the previous packet encompasses this one, ignore this one.
            continue
        else:
            last_packet_power = ACTIVE_COST * (packet.start_time - last_packet.start_time)

        last_packet.data_start_attributes["flow_power"] = last_packet_power

        last_packet = packet

    return timeline

def find_power_cost_all(timeline_all):
    new_timeline = {}
    for user, timeline in timeline_all.iteritems():
        new_timeline[user] = find_power_cost_timeline(timeline)
