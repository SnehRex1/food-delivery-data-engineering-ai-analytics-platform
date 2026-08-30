USE ROLE ACCOUNTADMIN;
USE DATABASE FOOD_DELIVERY;
USE SCHEMA RAW;
USE WAREHOUSE FD_WH;


-- Dimensions = messy real source data -> tolerate & skip bad rows (CONTINUE).

COPY INTO RAW.RESTAURANTS FROM @FD_RAW_STAGE/restaurant/  ON_ERROR = 'CONTINUE';

COPY INTO RAW.users       FROM @FD_RAW_STAGE/users/        ON_ERROR = 'CONTINUE';

COPY INTO RAW.food        FROM @FD_RAW_STAGE/food/         ON_ERROR = 'CONTINUE';

COPY INTO RAW.menu        FROM @FD_RAW_STAGE/menu/         ON_ERROR = 'CONTINUE';

-- Facts = clean generated data -> stay strict so counts are exact.

COPY INTO RAW.orders      FROM @FD_RAW_STAGE/orders/       ON_ERROR = 'ABORT_STATEMENT';

COPY INTO RAW.order_items FROM @FD_RAW_STAGE/order_items/  ON_ERROR = 'ABORT_STATEMENT';

COPY INTO RAW.reviews     FROM @FD_RAW_STAGE/reviews/      ON_ERROR = 'ABORT_STATEMENT';

-- Sanity check.

SELECT 'restaurants' t, COUNT(*) n FROM RAW.restaurants
UNION ALL SELECT 'users',       COUNT(*) FROM RAW.users
UNION ALL SELECT 'food',        COUNT(*) FROM RAW.food
UNION ALL SELECT 'menu',        COUNT(*) FROM RAW.menu
UNION ALL SELECT 'orders',      COUNT(*) FROM RAW.orders
UNION ALL SELECT 'order_items', COUNT(*) FROM RAW.order_items
UNION ALL SELECT 'reviews',     COUNT(*) FROM RAW.reviews
ORDER BY t;
