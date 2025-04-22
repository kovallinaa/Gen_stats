import pandas as pd
import re

df = pd.read_excel("Gender_StatsEXCEL.xlsx",sheet_name="Data")

df_long = df.melt(
    id_vars=["Country Name", "Country Code", "Indicator Name", "Indicator Code"],
    var_name="Year",
    value_name="Value"
)


YEARS = ['2018', '2019', '2020', '2021', '2022']
COUNTRIES = ['Ukraine','Poland','Germany','France','Italy','Spain','Netherlands','Sweden','Norway']
metric_codes = [
    "SP.POP.1564.FE.IN", "SP.POP.1564.MA.IN",
    "SL.TLF.CACT.FE.ZS", "SL.TLF.CACT.MA.ZS",
    "SL.UEM.TOTL.FE.ZS", "SL.UEM.TOTL.MA.ZS",
    "SE.TER.ENRR.FE", "SE.TER.ENRR.MA"
]
df_filtered_all = df_long[
    df_long["Year"].astype(str).isin(YEARS) &
    df_long["Country Name"].isin(COUNTRIES)]

df_filt_1 = df_filtered_all[df_filtered_all["Indicator Code"].astype(str).isin(metric_codes)].copy()
df_filt_2 = df_filtered_all[df_filtered_all["Indicator Code"].astype(str).isin(["SP.POP.TOTL"])].copy()
df_filt_3 = df_filtered_all[df_filtered_all["Indicator Code"].str.contains(r"SP\.POP\.\d{4}\.")].copy()

def extract_gender(code):
    if ".FE" in code:
        return "Female"
    elif ".MA" in code:
        return "Male"
    else:
        return "Total"
df_filt_1["Gender"] = df_filt_1["Indicator Code"].apply(extract_gender)
df_filt_3["Gender"] = df_filt_3["Indicator Code"].apply(extract_gender)

def extract_age_group(code):
    if "SP.POP.1564" in code:
        return None
    match = re.search(r'SP\.POP\.(\d{4})\.', code)
    if match:
        start = int(match.group(1)[:2])
        end = int(match.group(1)[2:])
        if start >= 15 and end <= 64:
            return f"{start}–{end}"
    return None
df_filt_3["Age Group"] = df_filt_3["Indicator Code"].apply(extract_age_group)


df_age = df_filt_3[df_filt_3["Age Group"].notnull()]
df_age_result = df_age[["Country Name", "Year", "Gender", "Age Group", "Value"]]
df_age_result.to_csv("population_15_64_1_clean.csv", index=False, encoding="utf-8-sig")

def classify_code(code):
    if 'SP.POP.1564' in code:
        return 'Population (15-64)'
    elif 'SL.TLF.CACT' in code:
        return 'Labor Force'
    elif 'SL.UEM.TOTL' in code:
        return 'Unemployment'
    elif 'SE.TER.ENRR' in code:
        return 'Education'
    elif "SP.POP.TOTL" in code:
        return "Total Population"
    else:
        return "Other"

df_filt_1['Indicarors'] = df_filt_1["Indicator Code"].apply(classify_code)
df_filt_2['Total Population'] = df_filt_2['Indicator Code'].apply(classify_code)
# pivot основних метрик
df_pivot = df_filt_1.pivot_table(
    index=["Country Name", "Year", "Gender"],
    columns="Indicarors",
    values="Value"
).reset_index()
left_table = df_pivot[['Country Name','Year','Gender','Education','Labor Force', 'Population (15-64)','Unemployment']]
right_table = df_filt_2[['Country Name','Year','Value']]
final_df = left_table.merge(right_table, on=["Country Name", "Year"], how="left")
final_df.to_csv("gender_metrics_clean.csv", index=False, encoding="utf-8-sig")

