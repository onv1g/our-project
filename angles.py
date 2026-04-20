import math


def calculate_beta(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    radians = math.atan2(-dy, dx)
    degrees = math.degrees(radians)
    beta = degrees % 180
    return beta


def process_gaps_to_list(raw_data):
    final_list = []
    for gap_id, segments in raw_data.items():
        if not segments: continue

        betas = []
        try:
            gap_num = int(gap_id.split('_')[1])
        except:
            gap_num = 1

        gap_entry = {"number_of_the_gap": gap_num, "final_beta": 0, "segments": []}

        for i, seg in enumerate(segments, 1):
            beta = calculate_beta(seg['x1'], seg['y1'], seg['x2'], seg['y2'])
            betas.append(beta)

            gap_entry["segments"].append({
                "number": i,
                "beta": round(beta, 1),
                "x_1": seg['x1'], "y_1": seg['y1'],
                "x_2": seg['x2'], "y_2": seg['y2']
            })

        if betas:
            avg_beta = sum(betas) / len(betas)
            gap_entry["final_beta"] = int(round(avg_beta))

        final_list.append(gap_entry)
    return final_list
