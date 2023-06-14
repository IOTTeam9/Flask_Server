import pandas as pd
from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
from sklearn.metrics.pairwise import euclidean_distances
from collections import Counter

app = Flask(__name__)

app.config['MYSQL_HOST'] = '3.34.148.235'
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Iot1234!'
app.config['MYSQL_DB'] = 'Iot'
app.config['MYSQL_DATABASE_CONNECT'] = True

mysql = MySQL(app)

bssid_list = []
rssi_list = []
place_records = []
df_POST = pd.DataFrame(columns=['bssid', 'rssi'])

@app.route('/')
def home():
    return 'HI'

@app.route('/flask', methods = ['GET', 'POST'])
def estimate_location():
    global df_POST
    
    if request.method == 'POST':
        data = request.get_json()
        
        bssid_list = []
        rssi_list = []
        
        for i in data:
            bssid_list.append(i["bssid"])
            rssi_list.append(i["rssi"])
        df_POST = pd.DataFrame({
                                'bssid' : list(bssid_list),
                                'rssi' : list(rssi_list)})

        location = "Data Frame"

        return jsonify({"location" : location})
    
    else:
        if df_POST.empty:
            return jsonify({'error' : 'No Data'})
        
        conn = mysql.connection
        cursor = conn.cursor()
        query = "SELECT rssi, bssid, place FROM wifi WHERE bssid IN ('{}')".format("', '".join(df_POST['bssid']))
        cursor.execute(query)
        result = cursor.fetchall()
        
        df_wifi = pd.DataFrame(result, columns=['rssi', 'bssid', 'place'])
        
        place_records = []
        for bssid in df_POST['bssid']:
            df_matched = df_wifi[df_wifi['bssid'] == bssid]
            rssi = df_POST[df_POST['bssid'] == bssid]['rssi'].values[0]
            distances = euclidean_distances([[rssi]], df_matched[['rssi']])
            closest_index = distances.argmin()
            closest_data = df_matched.iloc[closest_index]
            place = closest_data['place']
            place_records.append(place)
        
        counter = Counter(place_records)
        most_common = counter.most_common(1)
        location = most_common[0][0]
        
        if closest_data is not None:
            print("Successfully get location")
            return jsonify({"location" : location})
        else:
            return jsonify({"location" :'NaN'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000', debug=True)