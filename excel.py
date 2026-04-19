import os
import pandas as pd

def create_exel_file(percents,data_of_intervals,intervals,filename):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    folder_path = os.path.join(script_dir, 'excel_files')
    numbers=[]
    gaps_thing=[]
    gaps_percents=[]
    intervals_angles =[]
    intervals_beta = []
    orig_gaps = list(data_of_intervals.values())
    orig_percents = list(percents.values())
    for i in range(1,len(intervals)*2-1):
        numbers.append(i)

    for i in range(1, len(intervals)):
        intervals_angles.append(f"{intervals[i - 1] + 1}-{intervals[i]}")
        intervals_beta.append(f"{(90 - intervals[i - 1]) % 360}-{(90 - intervals[i]) % 360}")
        gaps_thing.append(orig_gaps[i - 1])
        gaps_percents.append(orig_percents[i - 1])


    for i in range(1, len(intervals)):


        intervals_angles.append(f"{(intervals[i - 1] + 180) + 1}-{(intervals[i] + 180)}")
        intervals_beta.append(f"{(90 - (intervals[i - 1] + 180)) % 360}-{(90 - (intervals[i] + 180)) % 360}")
        gaps_thing.append(orig_gaps[i - 1])
        gaps_percents.append(orig_percents[i - 1])


    print(numbers)
    data = {'№ п/п': numbers,
            'интервал в азимутах': intervals_angles,
            'интервал в бета': intervals_beta,
            'количество разрывов(шт)': gaps_thing,
            'количество разрывов(%)':gaps_percents}

    df = pd.DataFrame(data)
    full_path = os.path.join(folder_path, f"{filename}.xlsx")
    df.to_excel(full_path, index=False)