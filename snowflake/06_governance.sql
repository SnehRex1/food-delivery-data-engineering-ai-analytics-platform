-- ============================================================
-- Snowflake Security / Governance
-- ============================================================
-- Purpose:
--   Establish role-based access control (RBAC) for the
--   Food Delivery analytics platform.
--
-- Roles:
--   FD_DBT_ROLE       -> dbt transformations
--   FD_ANALYST_ROLE   -> human analytical users
--   FD_AI_READ_ROLE   -> AI / Text-to-SQL read-only access
--
-- IMPORTANT:
--   Run this script using ACCOUNTADMIN during initial setup.
-- ============================================================

USE ROLE ACCOUNTADMIN;


-- ============================================================
-- 1. CREATE APPLICATION-SPECIFIC ROLES
-- ============================================================

-- Role used by dbt to perform transformations.
CREATE ROLE IF NOT EXISTS FD_DBT_ROLE;

-- Role used by analysts to query analytical data.
CREATE ROLE IF NOT EXISTS FD_ANALYST_ROLE;

-- Read-only role used by AI applications.
CREATE ROLE IF NOT EXISTS FD_AI_READ_ROLE;


-- ============================================================
-- 2. ROLE HIERARCHY
-- ============================================================

-- SYSADMIN becomes the parent role for the application roles.
--
-- This keeps the role hierarchy manageable and avoids
-- assigning administrative privileges directly to users.

GRANT ROLE FD_DBT_ROLE
TO ROLE SYSADMIN;

GRANT ROLE FD_ANALYST_ROLE
TO ROLE SYSADMIN;

GRANT ROLE FD_AI_READ_ROLE
TO ROLE SYSADMIN;


-- ============================================================
-- 3. ANALYST ACCESS
-- ============================================================

-- Allow analysts to access the FOOD_DELIVERY database.
GRANT USAGE
ON DATABASE FOOD_DELIVERY
TO ROLE FD_ANALYST_ROLE;

-- Allow analysts to access the MARTS schema.
GRANT USAGE
ON SCHEMA FOOD_DELIVERY.MARTS
TO ROLE FD_ANALYST_ROLE;

-- Allow analysts to query all existing analytical tables.
GRANT SELECT
ON ALL TABLES IN SCHEMA FOOD_DELIVERY.MARTS
TO ROLE FD_ANALYST_ROLE;

-- Automatically grant SELECT on future mart tables.
--
-- This is important because dbt may create new analytical
-- tables after this governance script has been executed.
GRANT SELECT
ON FUTURE TABLES IN SCHEMA FOOD_DELIVERY.MARTS
TO ROLE FD_ANALYST_ROLE;


-- ============================================================
-- 4. AI READ-ONLY ACCESS
-- ============================================================

-- AI applications only require access to analytical data.
GRANT USAGE
ON DATABASE FOOD_DELIVERY
TO ROLE FD_AI_READ_ROLE;

GRANT USAGE
ON SCHEMA FOOD_DELIVERY.MARTS
TO ROLE FD_AI_READ_ROLE;

-- Existing mart tables are readable by the AI role.
GRANT SELECT
ON ALL TABLES IN SCHEMA FOOD_DELIVERY.MARTS
TO ROLE FD_AI_READ_ROLE;

-- Future mart tables are also readable.
GRANT SELECT
ON FUTURE TABLES IN SCHEMA FOOD_DELIVERY.MARTS
TO ROLE FD_AI_READ_ROLE;


-- ============================================================
-- 5. DBT TRANSFORMATION ACCESS
-- ============================================================

-- dbt can access the FOOD_DELIVERY database.
GRANT USAGE
ON DATABASE FOOD_DELIVERY
TO ROLE FD_DBT_ROLE;


-- ------------------------------------------------------------
-- RAW
-- ------------------------------------------------------------

-- dbt can access the RAW schema.
GRANT USAGE
ON SCHEMA FOOD_DELIVERY.RAW
TO ROLE FD_DBT_ROLE;

-- dbt can read raw source tables.
GRANT SELECT
ON ALL TABLES IN SCHEMA FOOD_DELIVERY.RAW
TO ROLE FD_DBT_ROLE;

-- Automatically allow dbt to read future raw tables.
GRANT SELECT
ON FUTURE TABLES IN SCHEMA FOOD_DELIVERY.RAW
TO ROLE FD_DBT_ROLE;


-- ------------------------------------------------------------
-- STAGING
-- ------------------------------------------------------------

-- dbt can access the STAGING schema.
GRANT USAGE
ON SCHEMA FOOD_DELIVERY.STAGING
TO ROLE FD_DBT_ROLE;

-- dbt can read existing staging tables/views.
GRANT SELECT
ON ALL TABLES IN SCHEMA FOOD_DELIVERY.STAGING
TO ROLE FD_DBT_ROLE;

-- dbt can create staging tables when required.
GRANT CREATE TABLE
ON SCHEMA FOOD_DELIVERY.STAGING
TO ROLE FD_DBT_ROLE;


-- ------------------------------------------------------------
-- MARTS
-- ------------------------------------------------------------

-- dbt can access the MARTS schema.
GRANT USAGE
ON SCHEMA FOOD_DELIVERY.MARTS
TO ROLE FD_DBT_ROLE;

-- dbt can read existing analytical tables.
GRANT SELECT
ON ALL TABLES IN SCHEMA FOOD_DELIVERY.MARTS
TO ROLE FD_DBT_ROLE;

-- dbt can create new analytical tables.
GRANT CREATE TABLE
ON SCHEMA FOOD_DELIVERY.MARTS
TO ROLE FD_DBT_ROLE;


-- ============================================================
-- 6. GOVERNANCE VERIFICATION
-- ============================================================

-- Display the roles created by this script.
SHOW ROLES;

-- Display the role hierarchy.
SHOW GRANTS TO ROLE SYSADMIN;

SHOW GRANTS TO ROLE FD_DBT_ROLE;
SHOW GRANTS TO ROLE FD_ANALYST_ROLE;
SHOW GRANTS TO ROLE FD_AI_READ_ROLE;