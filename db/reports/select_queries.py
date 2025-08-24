def premises_information_query() -> str:
    return """@
        SELECT 
            P.ID,
            P.PREMISES_TYPE_NAME,
            P.PREMISES_UNIT_NAME,
            P.COMMUNITY_ADDRESS_NAME,
            P.AREA,
            P.ROOMS_NUMBER,
            P.PERSONS_QUANTITY,
            P.CREATED_AT,
            AA.DAMAGE_DATE,
            AA.DMC_CATEGORY || ' (пошкодження ' || AA.DMC_PERCENT || '%)' AS DMC_CATEGORY_PERCENT,
            CASE 
                WHEN TR.TCC_CATEGORY != '' 
                    THEN CONCAT(TR.TCC_CATEGORY, ' (', TR.TCC_NAME, ')') 
                ELSE '' 
            END AS TCC_CATEGORY_DESC,
            AV.AMOUNT_REAL_DAMAGES AS ACTUAL_VALUE,
            RV.AMOUNT_REAL_DAMAGES AS REPORT_VALUE
        FROM TEST_PREMISES AS P
        LEFT JOIN TEST_REPORT_VALUATION AS RV ON P.ID = RV.PREMISES_ID
        LEFT JOIN TEST_ACT_VALUATION AS AV ON P.ID = AV.PREMISES_ID
        LEFT JOIN TEST_EXAMINATION AS AA ON P.ID = AA.PREMISES_ID
        LEFT JOIN TEST_TECH_REPORT AS TR ON P.ID = TR.PREMISES_ID
        WHERE 
            P.COMMUNITY_ADDRESS_NAME = 'Тестове місто'
            AND P.CREATED_AT BETWEEN '2024-01-01' AND '2024-01-01 23:59'
            AND AA.EXAMINATION_REPORT_REQUIRED_FLAG = TRUE;
       """
