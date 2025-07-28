from app.utils.desensitize import remove_sensitive_data
import pandas as pd

def process_csv_hardcoded():
    infile = './_docs/2024sorted_man_7.csv'
    outfile = './_docs/2024sorted_man_7_clean.csv'

    df = pd.read_csv(infile, dtype=str)  # read all as string
    for col in ['spm', 'svar']:
        if col in df.columns:
            df[col] = df[col].fillna('')\
                .apply(remove_sensitive_data)
    df.to_csv(outfile, index=False)
    print(f"Processed {infile} → {outfile}")

if __name__ == '__main__':
    process_csv_hardcoded()