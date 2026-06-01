-- Schema definition for Tech Job Market database

DROP TABLE IF EXISTS jobs;

CREATE TABLE jobs (
    "title" VARCHAR(255),
    "jobId" BIGINT PRIMARY KEY,
    "currency" VARCHAR(50),
    "jobUploaded" VARCHAR(255),
    "companyName" VARCHAR(255),
    "tagsAndSkills" TEXT,
    "experience" VARCHAR(255),
    "salary" VARCHAR(255),
    "location" VARCHAR(555),
    "companyId" BIGINT,
    "jobDescription" TEXT,
    "minimumSalary" DOUBLE PRECISION,
    "maximumSalary" DOUBLE PRECISION,
    "minimumExperience" DOUBLE PRECISION,
    "maximumExperience" DOUBLE PRECISION,
    "avg_salary" DOUBLE PRECISION,
    "jobUploaded_cleaned" DOUBLE PRECISION
);
