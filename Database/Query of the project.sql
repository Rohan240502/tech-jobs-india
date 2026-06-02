










select * from jobs;


-- SELECT job_title, COUNT(*)
-- FROM jobs
-- GROUP BY job_title
-- ORDER BY COUNT(*) DESC;

select title from jobs;

SELECT column_name
FROM information_schema.columns
WHERE table_name = 'jobs';


select * from jobs LIMIT 10 ;
select count(*) from jobs;


select title , COUNT(*) as Total_Jobs 
from jobs
GROUP BY title 
ORDER BY Total_Jobs DESC;



select companyName , COUNT(*) as Total_jobs
from jobs
GROUP BY companyName
ORDER BY Total_jobs







SELECT * FROM user_analytics ORDER BY timestamp DESC;






CREATE TABLE IF NOT EXISTS user_analytics (
    id SERIAL PRIMARY KEY,
    query_type VARCHAR(50),
    job_role VARCHAR(255),
    experience DOUBLE PRECISION,
    location VARCHAR(255),
    predicted_lpa DOUBLE PRECISION,
    user_email VARCHAR(255) DEFAULT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

SELECT * FROM user_analytics ORDER BY timestamp DESC;

SELECT user_email, timestamp, job_role, location 
FROM user_analytics 
WHERE user_email IS NOT NULL 
ORDER BY timestamp DESC;


SELECT job_role, COUNT(*) as search_count 
FROM user_analytics 
WHERE query_type = 'salary_prediction'
GROUP BY job_role 
ORDER BY search_count DESC 
LIMIT 10;
