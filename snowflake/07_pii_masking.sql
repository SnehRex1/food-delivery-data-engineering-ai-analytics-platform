-- ============================================================
-- 7. Email PII masking
-- ============================================================

USE ROLE ACCOUNTADMIN;
USE DATABASE FOOD_DELIVERY;
USE WAREHOUSE FD_WH;


-- Create a masking policy for email addresses.
--
-- Privileged transformation role:
--     sees the original value
--
-- Other roles:
--     see a masked value
--
-- Example:
--
--     john@gmail.com
--
-- becomes:
--
--     j***@gmail.com
--

CREATE OR REPLACE MASKING POLICY FD_EMAIL_MASK
AS (VAL STRING)
RETURNS STRING ->
    CASE

        -- dbt role can see the original value when required
        WHEN CURRENT_ROLE() = 'FD_DBT_ROLE'
            THEN VAL

        -- Everyone else receives a masked version
        ELSE
            REGEXP_REPLACE(
                VAL,
                '^(.).+(@.*)$',
                '\\1***\\2'
            )

    END;

-- Apply the masking policy to the actual email column.
ALTER TABLE FOOD_DELIVERY.MARTS.DIM_CUSTOMER
MODIFY COLUMN EMAIL
SET MASKING POLICY FD_EMAIL_MASK;

-- ============================================================
-- 7. Test PII masking
-- ============================================================

USE ROLE FD_DBT_ROLE;

SELECT EMAIL
FROM FOOD_DELIVERY.MARTS.DIM_CUSTOMER
LIMIT 5;


USE ROLE FD_ANALYST_ROLE;

SELECT EMAIL
FROM FOOD_DELIVERY.MARTS.DIM_CUSTOMER
LIMIT 5;