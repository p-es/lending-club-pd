SELECT grade,
        count(*) AS n,
        round(avg(int_rate), 2) AS mean_rate,
        round(avg(default_flag)*100, 1) AS default_pct,
        round(avg((total_pymnt - collection_recovery_fee)/loan_amnt - 1)*100, 2) AS mean_return_pct,
        round(stddev((total_pymnt - collection_recovery_fee)/loan_amnt - 1)*100, 2) AS sd_return_pct
FROM cohort
GROUP BY grade 
ORDER BY grade;

