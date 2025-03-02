import pymysql
from flask import Flask, render_template, jsonify
import pandas as pd
from pymysql import MySQLError

app = Flask(__name__)

# 配置数据库连接
def get_db_connection():
    try:
        connection = pymysql.connect(
            host="localhost",
            user="root",  # 替换为你的数据库用户名
            password="root",  # 替换为你的数据库密码
            database="traffic_monitor",  # 替换为你的数据库名称
            port=3306
        )
        if connection.open:
            print("Successfully connected to the database!")
            return connection
        else:
            print("Failed to connect to the database!")
            return None
    except MySQLError as e:
        print(f"Error while connecting to MySQL: {e}")
        return None

# 从数据库获取数据
def get_data_from_db():
    connection = get_db_connection()
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT timestamp, vehicle_count FROM traffic_data ORDER BY timestamp ASC LIMIT 10")
                rows = cursor.fetchall()
                connection.close()

                # 将数据转换为 pandas DataFrame
                data = pd.DataFrame(rows, columns=['timestamp', 'vehicle_count'])
                return data
        except MySQLError as e:
            print(f"Error executing query: {e}")
            connection.close()
            return None
    else:
        return None

@app.route("/")
def index():
    data = get_data_from_db()
    if data is not None:
        print("Data fetched from database:", data)
        data_json = data.to_dict(orient='records')
        return render_template('line_chart.html', data=data_json)
    else:
        print("Unable to fetch data from the database!")
        return "<p>Unable to fetch data from the database!</p>"

@app.route("/api/data")
def api_data():
    data = get_data_from_db()
    if data is not None:
        data_json = data.to_dict(orient='records')
        return jsonify(data_json)
    else:
        return jsonify([])

if __name__ == "__main__":
    app.run(debug=True)
