import snowflake.connector

def run_snowflake_query(
    user: str,
    password: str,
    account: str,
    warehouse: str,
    database: str,
    schema: str,
    query: str
):
    """
    Connects to Snowflake and executes the provided SQL query.
    Returns the results as a list of dictionaries.
    """
    ctx = snowflake.connector.connect(
        user=user,
        password=password,
        account=account,
        warehouse=warehouse,
        database=database,
        schema=schema
    )
    try:
        cs = ctx.cursor()
        cs.execute(query)
        columns = [col[0] for col in cs.description]
        results = [dict(zip(columns, row)) for row in cs.fetchall()]
        return results
    finally:
        cs.close()
        ctx.close()

        import streamlit as st
import pandas as pd
import snowflake.connector
from datetime import datetime
import time

def show_snowflake_query_page():
    if st.session_state.current_user['role'] != "Admin":
        st.error("🚫 Access denied. This tool is only available to Admins.")
        return

    st.header("🧊 Snowflake FIDO Pull Tool (Admin Only)")
    st.markdown("Use this to pull FIDOs for cleanup directly from Snowflake using brand or fuzzy description matches.")

    # Inputs
    brand = st.text_input("🔖 Brand Name (exact match):", "")
    fuzzy = st.text_area("🔍 Fuzzy Description Matches (comma-separated):", "")
    project_title = st.text_input("📁 Project Title (for upload):", "")
    queue_type = st.selectbox("📋 Queue Type:", ["Non-licensed", "Licensed", "CATQ"])
    priority = st.select_slider("🎯 Priority:", ["low", "medium", "high"], value="medium")

    if st.button("🚀 Run Snowflake Query"):
        if not brand and not fuzzy:
            st.warning("You must enter a brand name or at least one fuzzy match.")
            return

        fuzzy_array = [f.strip() for f in fuzzy.split(',') if f.strip()]
        fuzzy_sql_array = ", ".join([f"'%{x}%'" for x in fuzzy_array]) if fuzzy_array else "'%'"

        # Build your full query string dynamically (your actual full query here)
        query = f"""
        WITH base_fidos_raw AS (
            SELECT FIDO, BARCODE, category_id, description, brand, BRAND_ID, MANUFACTURER,
                   'DESC_MATCH' AS match_source,
                   CASE WHEN DELETED_DATE IS NOT NULL THEN 'YES' ELSE 'NO' END AS is_deleted
            FROM fetch_services_prod.staging.fido_catalog_cleaned_stage
            WHERE description ILIKE ANY (ARRAY[{fuzzy_sql_array}])
              AND FIDO_TYPE = 'PRODUCT'

            UNION ALL

            SELECT FIDO, BARCODE, category_id, description, brand, BRAND_ID, MANUFACTURER,
                   'BRAND_MATCH' AS match_source,
                   CASE WHEN DELETED_DATE IS NOT NULL THEN 'YES' ELSE 'NO' END AS is_deleted
            FROM fetch_services_prod.staging.fido_catalog_cleaned_stage
            WHERE brand ILIKE '%{brand}%'
              AND FIDO_TYPE = 'PRODUCT'
        ),
        ranked_fidos AS (
            SELECT *, ROW_NUMBER() OVER (PARTITION BY FIDO ORDER BY match_source) AS row_num
            FROM base_fidos_raw
        ),
        fido_and_upc AS (
            SELECT fido, SUM(final_price) AS gmv
            FROM ANALYTICS_PROD.PAM_SERVICE.P_REWARDS_RECEIPT_JOIN_ITEMS
            WHERE purchase_date BETWEEN DATEADD(day, -365, CURRENT_DATE) AND CURRENT_DATE
              AND fido IS NOT NULL AND barcode_upc IS NOT NULL
            GROUP BY fido
        ),
        fido_only AS (
            SELECT fido, SUM(final_price) AS gmv
            FROM ANALYTICS_PROD.PAM_SERVICE.P_REWARDS_RECEIPT_JOIN_ITEMS
            WHERE purchase_date BETWEEN DATEADD(day, -365, CURRENT_DATE) AND CURRENT_DATE
              AND fido IS NOT NULL AND barcode_upc IS NULL
            GROUP BY fido
        ),
        upc_only_raw AS (
            SELECT barcode_upc, SUM(final_price) AS gmv
            FROM ANALYTICS_PROD.PAM_SERVICE.P_REWARDS_RECEIPT_JOIN_ITEMS
            WHERE purchase_date BETWEEN DATEADD(day, -365, CURRENT_DATE) AND CURRENT_DATE
              AND fido IS NULL AND barcode_upc IS NOT NULL
            GROUP BY barcode_upc
        ),
        upc_only AS (
            SELECT fc.fido, SUM(u.gmv) AS gmv
            FROM upc_only_raw u
            JOIN fetch_services_prod.staging.fido_catalog_cleaned_stage fc ON u.barcode_upc = fc.barcode
            GROUP BY fc.fido
        ),
        combined_gmv AS (
            SELECT fido, SUM(gmv) AS gmv
            FROM (
                SELECT * FROM fido_and_upc
                UNION ALL
                SELECT * FROM fido_only
                UNION ALL
                SELECT * FROM upc_only
            )
            GROUP BY fido
        ),
        gmv_with_fido AS (
            SELECT r.FIDO, r.BARCODE, r.category_id, r.description, r.brand, r.BRAND_ID,
                   r.MANUFACTURER, r.match_source, r.is_deleted, COALESCE(g.gmv, 0) AS gmv
            FROM ranked_fidos r
            LEFT JOIN combined_gmv g ON r.FIDO = g.fido
            WHERE r.row_num = 1
        )
        SELECT f.FIDO, f.BARCODE, c.name_hierarchy AS category_hierarchy,
               f.description, f.brand, f.BRAND_ID, f.MANUFACTURER, f.match_source,
               f.is_deleted, f.gmv AS gmv_365d,
               CASE 
                   WHEN f.gmv = 0 THEN '$0'
                   WHEN f.gmv < 500 THEN '$1 - $499'
                   WHEN f.gmv < 1000 THEN '$500 - $999'
                   WHEN f.gmv < 5000 THEN '$1000 - $4999'
                   WHEN f.gmv < 10000 THEN '$5000 - $9999'
                   ELSE '$10000+'
               END AS gmv_threshold,
               CURRENT_DATE AS run_date,
               DATEADD(day, -365, CURRENT_DATE) AS gmv_start_date,
               CURRENT_DATE AS gmv_end_date
        FROM gmv_with_fido f
        LEFT JOIN analytics_prod.catalog.categories c ON f.category_id = c.id
        ORDER BY f.is_deleted, f.match_source, f.brand, f.description
        """

        # Connect and execute
        try:
            conn = snowflake.connector.connect(
                user=st.secrets["snowflake"]["user"],
                password=st.secrets["snowflake"]["password"],
                account=st.secrets["snowflake"]["account"],
                warehouse=st.secrets["snowflake"]["warehouse"],
                database=st.secrets["snowflake"]["database"],
                schema=st.secrets["snowflake"]["schema"]
            )
            cursor = conn.cursor()
            with st.spinner("Running query..."):
                cursor.execute(query)
                rows = cursor.fetchall()
                columns = [col[0] for col in cursor.description]
                df = pd.DataFrame(rows, columns=columns)

            st.success(f"✅ Query returned {len(df)} rows.")
            st.dataframe(df, use_container_width=True)

            # CSV download
            csv = df.to_csv(index=False)
            st.download_button("📥 Download CSV", csv, "snowflake_fido_results.csv", "text/csv")

            # Upload into project queue
            if st.button("📤 Push as Project"):
                if not project_title:
                    st.warning("Please enter a project title before uploading.")
                else:
                    now = datetime.now()
                    formatted_date = now.strftime('%Y%m%d_%H%M%S')
                    queue_mapping = {
                        "Non-licensed": "nonlicensed",
                        "Licensed": "licensed",
                        "CATQ": "catq"
                    }
                    queue_code = queue_mapping[queue_type]
                    file_key = f"{queue_code}_{project_title}_{priority}_{formatted_date}"
                    df['upload_date'] = now.strftime("%Y-%m-%d")
                    df['status'] = 'Pending Review'
                    df['uploader'] = st.session_state.current_user['name']
                    df['reviewer'] = ''
                    df['review_date'] = ''
                    df['comments'] = ''
                    df['priority'] = priority
                    df['GMV'] = pd.to_numeric(df['gmv_365d'], errors='coerce').fillna(0)

                    # Push into session state
                    st.session_state.uploaded_files[file_key] = df
                    from utils import save_session_state, refresh_session_state  # adjust path if needed
                    save_session_state()
                    refresh_session_state()

                    st.success(f"🎉 Project '{project_title}' pushed into {queue_type} queue!")
                    time.sleep(1)
                    st.rerun()

        except Exception as e:
            st.error(f"❌ Snowflake error: {e}")

now = datetime.now()

# Add required review/project metadata
df['CATEGORY'] = df['category_hierarchy']  # Convert
df['DESCRIPTION'] = df['description']
df['BRAND'] = df['brand']
df['status'] = 'Pending Review'
df['uploader'] = st.session_state.current_user['name']
df['reviewer'] = ''
df['review_date'] = ''
df['comments'] = ''
df['priority'] = priority
df['upload_date'] = now.strftime("%Y-%m-%d")

# Add editable fields for updates
df['updated_description'] = ''
df['updated_category'] = ''
df['updated_brand'] = ''
df['no_change'] = False

# Standardize GMV column
df['GMV'] = pd.to_numeric(df['gmv_365d'], errors='coerce').fillna(0)
