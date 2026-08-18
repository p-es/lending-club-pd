SELECT loan_status, count(*) AS n
FROM raw_accepted
GROUP BY loan_status
ORDER BY n DESC;

SELECT min(strptime(issue_d, '%b-%Y')) AS first_loan,
       max(strptime(issue_d, '%b-%Y')) AS last_loan
FROM raw_accepted;

SUMMARIZE raw_accepted;
