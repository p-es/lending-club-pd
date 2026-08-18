SELECT loan_status, count(*) AS n
FROM raw_accepted
GROUP BY loan_status
ORDER BY n DESC;

SELECT min(strptime(issue_d, '%b-%Y')) AS first_loan,
       max(strptime(issue_d, '%b-%Y')) AS last_loan
FROM raw_accepted;

SUMMARIZE raw_accepted;


SELECT date_trunc('quarter', issue_date) AS vintage,
       count(*) AS n_loans,
       round(avg(default_flag) * 100, 2) AS default_rate_pct
FROM cohort
GROUP BY vintage
ORDER BY vintage;


SELECT grade,
       count(*) AS n_loans,
       round(avg(default_flag) * 100, 2) AS default_rate_pct
FROM cohort
GROUP BY grade
ORDER BY grade;