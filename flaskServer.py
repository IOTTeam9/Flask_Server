import pandas as pd
import numpy as np
from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
from apscheduler.schedulers.background import BackgroundScheduler
from sklearn.metrics.pairwise import euclidean_distances
from sklearn.preprocessing import LabelEncoder, StandardScaler

app = Flask(__name__)

app.config['MYSQL_HOST'] = '3.34.148.235'
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Iot1234!'
app.config['MYSQL_DB'] = 'Iot'
app.config['MYSQL_DATABASE_CONNECT'] = True

mysql = MySQL(app)
scheduler = BackgroundScheduler()
label_encoder = LabelEncoder()
std_scaler = StandardScaler()

@app.route('/')
def home():
    return 'HI'

@app.route('/flask', methods = ['GET', 'POST'])
def estimate_location():
    
    print("Open of /flask")

    bssid_list = []
    rssi_list = []
    
    data = request.get_json()
    print("Data get successfully ! ")
    
    for i in data:
        bssid_list.append(i["bssid"])
        rssi_list.append(i["rssi"])
    df_POST = pd.DataFrame({
                             'bssid' : bssid_list,
                             'rssi' : rssi_list})
    
    print("DataFramming successfully")
    print(df_POST)

    conn = mysql.connection
    cursor = conn.cursor()
    query = "SELECT rssi, bssid, place FROM wifi WHERE bssid IN ('{}')".format("', '".join(df_POST['bssid']))
    cursor.execute(query)
    result = cursor.fetchall()
    df_wifi = pd.DataFrame(result, columns=['rssi', 'bssid', 'place'])
    
    print("mySQL Data read successfully")
    print(df_wifi)

    df_POST['bssid'] = [int(x.replace(":", "")[-12:], 16) for x in df_POST['bssid']]
    df_wifi['bssid'] = [int(x.replace(":", "")[-12:], 16) for x in df_wifi['bssid']]

    distances = euclidean_distances(df_POST[['rssi', 'bssid']], df_wifi[['rssi', 'bssid']])

    closest_index = np.argmin(distances)
    closest_data = df_wifi.iloc[closest_index]

    if closest_data is not None:
        location = closest_data['place']
        print("Successfully get location")
        return jsonify({location})
    else:
        return jsonify({'NaN'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000', debug=True)