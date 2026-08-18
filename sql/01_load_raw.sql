CREATE OR REPLACE TABLE raw_accepted AS
SELECT * FROM read_csv_auto('data/raw/accepted_2007_to_2018Q4.csv.gz',
sample_size = -1,
types = {'id': 'VARCHAR'})
WHERE loan_amnt IS NOT NULL;

CREATE OR REPLACE TABLE raw_rejected AS
SELECT * FROM read_csv_auto('data/raw/rejected_2007_to_2018Q4.csv.gz',
sample_size = -1);

