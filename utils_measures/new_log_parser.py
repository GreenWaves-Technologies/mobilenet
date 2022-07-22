import os
from glob import glob
import pandas as pd

MEAS_SETTINGS = {
    "CH_A_Avg": ["SoC Before DCDC [mW]", 1.8, 1],
    "CH_B_Avg": ["SoC After DCDC [mW]", None, 0.5],
    #"CH_C_Avg": ["Trigger", None, 0.5],
    "CH_D_Avg": ["IO [mW]", 1.8, 0.25],
}

def convert_meas_to_mW(dataframe: pd.DataFrame, settings):
    for name, set in settings.items():
        voltage = set[1] if set[1] is not None else dataframe["Voltage [V]"]
        dataframe[name] = dataframe[name] * voltage / set[2]
        dataframe = dataframe.rename(columns={name: set[0]})
    dataframe.insert(dataframe.columns.get_loc("SoC After DCDC [mW]")+1, "Efficiency DCDC", dataframe["SoC After DCDC [mW]"] / dataframe["SoC Before DCDC [mW]"])
    dataframe.insert(dataframe.columns.get_loc("Latency [ms]")+1, "Energy [uJ]", dataframe["Latency [ms]"] * dataframe["SoC Before DCDC [mW]"])
    return dataframe

MODEL_LIST = {
    0 :"MobV1-224-1",
    1 :"MobV1-192-1",
    2 :"MobV1-160-1",
    3 :"MobV1-128-1",
    4 :"MobV1-224-075",
    5 :"MobV1-192-075",
    6 :"MobV1-160-075",
    7 :"MobV1-128-075",
    8 :"MobV1-224-05",
    9 :"MobV1-192-05",
    10:"MobV1-160-05",
    11:"MobV1-128-05",
    12:"MobV1-224-025",
    13:"MobV1-192-025",
    14:"MobV1-160-025",
    15:"MobV1-128-025",
    16:"MobV2-224-14",
    17:"MobV2-224-1",
    18:"MobV2-192-1",
    19:"MobV2-160-1",
    20:"MobV2-128-1",
    21:"MobV2-96-1",
    22:"MobV2-224-075",
    23:"MobV2-192-075",
    24:"MobV2-160-075",
    25:"MobV2-128-075",
    26:"MobV2-96-075",
    27:"MobV2-224-05",
    28:"MobV2-192-05",
    29:"MobV2-160-05",
    30:"MobV2-128-05",
    31:"MobV2-96-05",
    32:"MobV3-Min",
    33:"MobV3-Small"
    }

LOG_DIR = "logs"
df = None
for log_file in glob(LOG_DIR + "/log_*"):
    filename = os.path.splitext(log_file)[0]
    model_id = int(filename.split("_")[1])
    model_name = MODEL_LIST[model_id]
    freq = int(filename.split("_")[-2])
    voltage = int(filename.split("_")[-1]) / 1000
    mode = "NE16" if "NE16" in filename else ("FP16" if "FP16" in filename else "SQ8")
    mode += "_HWC" if "HWC" in filename else ""
    row = pd.read_csv(log_file, sep="\t", header=None, index_col=0).transpose()
    row.insert(0, "Model_id", model_id)
    row.insert(1, "Model", model_name)
    row.insert(2, "Mode", mode)
    row.insert(2, "Frequency [MHz]", freq)
    row.insert(2, "Voltage [V]", voltage)
    row.reset_index(drop=True, inplace=True)
    if df is None:
        df = row
    else:
        df = df.append(row)

df = df.sort_values(["Model_id", "Mode", "Voltage [V]"])
df = df.rename(
    columns={
        "n_Points": "Latency [ms]"})
df["Latency [ms]"] /= 1000
total_cyc = df["Latency [ms]"] * df["Frequency [MHz]"] * 1000
ops_over_cyc = df["Sum of all Kernels operations"] / total_cyc
df.insert(df.columns.get_loc("Latency [ms]")+1, "Cyc", total_cyc)
df.insert(df.columns.get_loc("Cyc")+1, "Ops/Cyc", ops_over_cyc)
df = convert_meas_to_mW(df, MEAS_SETTINGS)
print(df)
df.to_csv("log_res.csv")
