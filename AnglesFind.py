import math
import json


def calculate_beta(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    if dx == 0:
        return 180
    if dy == 0:
        return 90
    tan = dy / dx
    tangle = abs(math.degrees(math.atan(tan)))
    return math.floor(tangle)


def process_gaps(raw_data, filename="gaps.json"):
    final_json = {}

    for gap_id, segments in raw_data.items():
        if not segments:
            continue
        betas = []
        gap_num = int(gap_id.split('_')[1])

        gap_entry = {
            "number_of_the_gap": gap_num,
            "final_beta": 0
        }

        for i, seg in enumerate(segments, 1):
            beta = calculate_beta(seg['x1'], seg['y1'], seg['x2'], seg['y2'])
            betas.append(beta)
            gap_entry[f"segment{i}"] = {
                "number": i,
                "beta": beta,
                "x_1": seg['x1'],
                "y_1": seg['y1'],
                "x_2": seg['x2'],
                "y_2": seg['y2']
            }

        gap_entry["final_beta"] = math.floor(sum(betas) / len(betas))
        ordered_gap = {
            "number_of_the_gap": gap_entry["number_of_the_gap"],
            "final_beta": gap_entry["final_beta"]
        }
        ordered_gap.update({k: v for k, v in gap_entry.items() if k.startswith("segment")})

        final_json[gap_id] = ordered_gap

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(final_json, f, indent=2, ensure_ascii=False)
