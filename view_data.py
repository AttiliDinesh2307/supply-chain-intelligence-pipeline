from db_handler import get_connection

def view_table(table_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    
    column_names = [description[0] for description in cursor.description]
    print(f"\n--- {table_name} ({len(rows)} rows) ---")
    print(column_names)
    for row in rows:
        print(row)
    
    conn.close()

if __name__ == "__main__":
    view_table("weather_log")
    view_table("exchange_rate_log")
    view_table("country_data")