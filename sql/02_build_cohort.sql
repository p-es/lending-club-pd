CREATE OR REPLACE TABLE cohort AS
SELECT *,
       CASE WHEN loan_status = 'Charged Off' THEN 1 ELSE 0 END AS default_flag,
       strptime(issue_d, '%b-%Y') AS issue_date
FROM raw_accepted
WHERE trim(term) = '36 months'
  AND loan_status IN ('Fully Paid', 'Charged Off')
  AND strptime(issue_d, '%b-%Y')
      BETWEEN DATE '2012-01-01' AND DATE '2015-09-30';
