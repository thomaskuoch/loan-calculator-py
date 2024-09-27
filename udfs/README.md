# Snowflake User-Defined Functions (UDFs)

This folder contains user-defined functions (UDFs) that can be executed in Snowflake.

## 1. XIRR (Extended Internal Rate of Return)

The `xirr` function calculates the internal rate of return for a series of cash flows occurring at irregular intervals.

### Steps to Use:
1. Copy and paste the content in the `udfs/xirr.sql` file into a Snowflake SQL query editor.
2. Execute the query to create the UDF in your Snowflake environment.

### Example Query:
Once the UDF is created, you can use the `xirr` function in your SQL queries like this:

```sql
SELECT
    ['2022-06-01', '2022-07-16', '2022-08-16', '2022-09-16'] AS dates,
    [-100, 34.67, 34.67, 34.66] AS cashflows,
    xirr(dates, cashflows) AS xirr_result;  -- Expected output: 0.207
```

This query will calculate the XIRR for the given cashflows and dates.

---

## 2. Loan Calculator

The loan calculator UDTF (User-Defined Table Function) helps compute loan interest payments based on the provided inputs.

### Steps to Use:
1. Generate the UDTF by running the following command in your terminal:

    ```bash
    uv run python scripts/generate_loan_calculator_udtf.py
    ```

    This will generate the SQL file `udfs/loan_calculator.sql`.

2. Copy and paste the content of `udfs/loan_calculator.sql` into a Snowflake SQL query editor.
3. Execute the query to create the UDTF in your Snowflake environment.

### Example Query:
After the UDTF is created, you can use it in SQL queries as shown below:

```sql
SELECT
    *
FROM
    TABLE(
        loan_calculator(
            10000,                -- Loan amount in cents
            0.209 :: float,       -- Interest rate (20.9%)
            3,                    -- Loan term in months
            '2022-06-01' :: date, -- Start date of the loan
            45,                   -- Days of the first repayment
            'interests'           -- Calculation type ('interests' or 'base_fees')
        )
    );
```

This will return a table with the calculated loan schedule based on the provided parameters.