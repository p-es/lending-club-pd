SELECT loan_status, count(*) AS n
FROM raw_accepted
GROUP BY loan_status
ORDER BY n DESC;

SELECT min(strptime(issue_d, '%b-%Y')) AS first_loan,
       max(strptime(issue_d, '%b-%Y')) AS last_loan
FROM raw_accepted;


SELECT date_trunc('quarter', issue_date) AS vintage,
       count(*) AS n_loans,
       round(avg(default_flag) * 100, 2) AS default_rate_pct
FROM cohort
GROUP BY vintage
ORDER BY vintage;


SELECT date_trunc('quarter', issue_date) AS vintage,
            avg(default_flag)*100 AS default_pct, count(*) AS n
        FROM cohort GROUP BY 1 ORDER BY 1

SELECT grade,
       count(*) AS n_loans,
       round(avg(default_flag) * 100, 2) AS default_rate_pct
FROM cohort
GROUP BY grade
ORDER BY grade;


SELECT sub_grade,
       count(*) AS n_loans,
       round(avg(default_flag) * 100, 1) AS default_rate_pct
FROM cohort
GROUP BY sub_grade 
ORDER BY sub_grade;

SELECT grade,
            avg(default_flag)*100 AS default_pct, count(*) AS n
        FROM cohort GROUP BY 1 ORDER BY 1;
SELECT sub_grade,
            avg(default_flag)*100 AS default_pct, count(*) AS n
        FROM cohort GROUP BY 1 ORDER BY 1;



SELECT purpose,
            avg(default_flag)*100 AS default_pct, count(*) AS n
        FROM cohort GROUP BY 1 ORDER BY 2 DESC;


SELECT floor(((fico_range_low+fico_range_high)/2)/20)*20 AS fico_bin,
                avg(default_flag)*100 AS default_pct, count(*) AS n
         FROM cohort GROUP BY 1 HAVING count(*) > 500 ORDER BY 1;


SELECT floor(dti/5)*5 AS dti_bin,
                    avg(default_flag)*100 AS default_pct, count(*) AS n
             FROM cohort
             WHERE dti IS NOT NULL
             GROUP BY 1 HAVING count(*) > 500 ORDER BY 1;

SELECT sub_grade, avg(int_rate) AS avg_int_rate,
                     avg(default_flag)*100 AS default_pct, count(*) AS n
              FROM cohort GROUP BY 1 ORDER BY 1;

SELECT 
    CASE WHEN issue_date <= DATE '2014-12-31' THEN 'train' ELSE 'test' AND AS split,
    COUNT(*) AS n,
    round(avg(default_flag)*100, 2) AS default_pct,
    min(issue_date) AS first, max(issue_date) AS last
    FROM cohort GROUP BY 1 ORDER BY 1 DESC;
#train: n = 306462, default_pct = 13.25
#test: n = 194357, default_pct = 14.92

