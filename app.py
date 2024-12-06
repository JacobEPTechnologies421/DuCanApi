from flask import Flask, request, jsonify
import pyodbc

app = Flask(__name__)

# Azure SQL Database connection details
server = 'ducanserver.database.windows.net'
database = 'dbo.dcData'
username = 'ducanadmin'
password = 'Ept640024'
driver = '{ODBC Driver 17 for SQL Server}'  # Make sure this driver is installed

@app.route('/')
def home():
    return "Welcome to the DuCan Data API!"

@app.route('/upload', methods=['POST'])
def upload_data():
    try:
        data = request.json  # Parse JSON data from request

        # Connect to Azure SQL Database
        conn = pyodbc.connect(
            f"DRIVER={driver};SERVER={server};PORT=1433;DATABASE={database};UID={username};PWD={password}"
        )
        cursor = conn.cursor()

        # SQL Query
        query = """
        INSERT INTO dbo.DuCanData_test (
            DeviceID, Timestamp, Battery, DCVoltage, MotorSpeed, MotorCurrent, MotorVoltage, 
            MotorLegATemp, MotorLegBTemp, MotorLegCTemp, MotorTemp, Battery1SOC, Battery1HCT, 
            Battery1LCT, Battery1HCV, Battery1LCV, Battery1DCL, Battery1Volatge, Battery1Current, 
            Batter2SOC, Battery2HCT, Battery2LCT, Battery2HCV, Battery2LCV, Battery2DCL, Battery2Volatge, 
            Battery2Current, Battery3SOC, Battery3HCT, Battery3LCT, Battery3HCV, Battery3LCV, Battery3DCL, 
            Battery3Volatge, Battery3Current, ChargeCurrent, ChargerPluggedIn, ChargerStatusfromHMI, 
            System_Status_Active_Station, System_Status_Emergency1, System_Status_Emergency_2, 
            System_Status_Misc, SystemFault, BatteryFault, MotorFault
        )
        VALUES (?, GETDATE(), ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        # Execute query
        cursor.execute(query, tuple(data.values()))
        conn.commit()

        return jsonify({"status": "success"}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500



@app.route('/get-data', methods=['GET'])
def get_data():
    try:
        # Get query parameters
        device_id = request.args.get('DeviceID')
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')

        # Connect to Azure SQL Database
        conn = pyodbc.connect(
            f"DRIVER={driver};SERVER={server};PORT=1433;DATABASE={database};UID={username};PWD={password}"
        )
        cursor = conn.cursor()

        # Construct the SQL query
        query = "SELECT * FROM dbo.DuCanData_test WHERE 1=1"
        params = []

        if device_id:
            query += " AND DeviceID = ?"
            params.append(device_id)
        
        if start_time:
            query += " AND Timestamp >= ?"
            params.append(start_time)
        
        if end_time:
            query += " AND Timestamp <= ?"
            params.append(end_time)

        # Execute query
        cursor.execute(query, params)
        columns = [column[0] for column in cursor.description]  # Fetch column names
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]  # Fetch all rows

        return jsonify(results), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run()
