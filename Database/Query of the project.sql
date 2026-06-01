-- 1. Total Number of jobs

select COUNT(*) as total_jobs
from jobs;

-- 2. Most demanded Job roles

select title , COUNT(*) as total_jobs 
from jobs
group by title 
order by total_jobs DESC;

--3 . Top hiring companies

select "companyName" , COUNT(*) as openings
from jobs 
group by "companyName"
order by openings desc;


-- 4. Top hiring locations

select location , COUNT(*) as total_jobs
from jobs 
group by location
order by total_jobs desc;
\

-- 5.Average salary by role ⭐

select avg_salary , count(*) as salary 
from jobs
group by avg_salary
order by salary ASC;

-- 6. Highest paying jobs

SELECT
    title,
    "companyName",
    location,
    ROUND((avg_salary::numeric / 100000), 2) AS salary_lpa
FROM jobs
WHERE avg_salary > 0
ORDER BY avg_salary DESC
LIMIT 10;


-- 7. Average salary by company

SELECT 
	title,''

	ROUND(AVG(avg_salary)::numeric/100000,2) as avg_salary_lpa
from jobs
where avg_salary >0
GROUP BY title
ORDER BY avg_salary_lpa DESC
LIMIT 10;


-- 8. Average salary by experience

SELECT "minimumExperience",

ROUND(AVG(avg_salary)::numeric/100000 ,2) as avg_salary_by_experince
from jobs
Where avg_salary > 0
GROUP BY "minimumExperience"
ORDER BY avg_salary_by_experince;


-- 9. Experience level distribution

select "minimumExperience",
COUNT(*) as total_jobs
from jobs

GROUP BY "minimumExperience"
ORDER BY "minimumExperience";



-- 10. Jobs with salary not disclosed

select count(*) as salary_not_disclosed
from jobs
where salary = 'Not disclosed';


-- 11.Jobs with disclosed salary

select count(*) as salary_disclosed
from jobs
where avg_salary > 0;


-- 12. Top skills (very important)

select "tagsAndSkills" ,
COUNT(*) as frequency
from jobs
GROUP BY "tagsAndSkills"
order by frequency DESC
limit 10;


--13. Remote / Hybrid / Onsite

SELECT *
FROM jobs
WHERE location ILIKE '%Remote%'
OR location ILIKE '%Hybrid%'
OR location ILIKE '%Onsite%';



-- 14. Highest experience required


select 
title ,
"companyName",
"maximumExperience"
from jobs
ORDER BY "maximumExperience" DESC;



-- 15. Salary range spread


SELECT
    MIN(avg_salary)/100000 AS min_salary_lpa,
    MAX(avg_salary)/100000 AS max_salary_lpa,
    ROUND(AVG(avg_salary::numeric)/100000,2) AS overall_avg_salary_lpa
FROM jobs
WHERE avg_salary > 0;



-- My top 6 for final project report:

-- If you include only the strongest ones:

-- ✅ Total jobs
-- ✅ Most demanded roles
-- ✅ Top locations
-- ✅ Average salary by role
-- ✅ Salary vs experience
-- ✅ Top skills















