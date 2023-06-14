import pandas as pd
from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
from sklearn.metrics.pairwise import euclidean_distances
from collections import Counter

# Make Flask app object
app = Flask(__name__)

# Flask config about mySQL
app.config['MYSQL_HOST'] = '3.34.148.235'
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Iot1234!'
app.config['MYSQL_DB'] = 'Iot'
app.config['MYSQL_DATABASE_CONNECT'] = True

# mySQL connection object
mysql = MySQL(app)

# Intialize global variable
bssid_list = []
rssi_list = []
place_records = []
df_POST = pd.DataFrame(columns=['bssid', 'rssi'])

# Home page(Do nothing)
@app.route('/')
def home():
    return 'HI'

# /flask End point Router use 'GET' method and 'POST' method
@app.route('/flask', methods = ['GET', 'POST'])
def estimate_location():
    global df_POST

    # In case of request from android is 'POST' method
    if request.method == 'POST':
        data = request.get_json()
        
        # Reinitialize android input list
        bssid_list = []
        rssi_list = []
        
        # Loop in android input list
        for i in data:
            # Add value into each list
            bssid_list.append(i["bssid"])
            rssi_list.append(i["rssi"])
        
        # Make lists into one Data frame
        df_POST = pd.DataFrame({
                                'bssid' : list(bssid_list),
                                'rssi' : list(rssi_list)})
        
        # Nothing should return (meaningless return)
        location = "Data Frame"
        return jsonify({"location" : location})
    
    # In case of request from android is 'GET' method
    else:
        # Error exception of request of 'GET' method before requested of 'POST' method
        # In this case noting input from android..
        if df_POST.empty:
            return jsonify({'error' : 'No Data'})
        
        # Make connection with mySQL and set cursor
        conn = mysql.connection
        cursor = conn.cursor()
        # Get data using query for mySQL Database
        query = "SELECT rssi, bssid, place FROM wifi WHERE bssid IN ('{}')".format("', '".join(df_POST['bssid']))
        cursor.execute(query)
        result = cursor.fetchall()
        
        # Make data into Data frame
        df_wifi = pd.DataFrame(result, columns=['rssi', 'bssid', 'place'])
        
        # Predicting present position model
        # Initialize place list
        place_records = []
        # Looping in android input data(bssid)
        for bssid in df_POST['bssid']:
            # df_matched list is for same bssid (android input bssid & DB data bssid)
            df_matched = df_wifi[df_wifi['bssid'] == bssid]
            # Get rssi value from android input in df_matched case
            rssi = df_POST[df_POST['bssid'] == bssid]['rssi'].values[0]
            # Exception of no match in android and DB bssid
            if not df_matched.empty:
                # Calculate distance between android input rssi and DB input rssi
                distances = euclidean_distances([[rssi]], df_matched[['rssi']])
                closest_index = distances.argmin()
                closest_data = df_matched.iloc[closest_index]
                place = closest_data['place']
                # Sum placees in same bssid and similer rssi (android input & DB data)
                place_records.append(place)
            else:
                # Just pass no match case from now
                continue
        
        # Exception check again
        if df_matched.empty:
            # Total df_matched empty case
            return jsonify({"error" :'Nothing matches in DB'})
        
        else:
            # Count locations in place_records
            counter = Counter(place_records)
            most_common = counter.most_common(1)
            # Get Mode value of location => final prediction
            location = most_common[0][0]
            
            # If get valid location
            if closest_data is not None:
                print("Successfully get location")
                print("Location : ", location)
                return jsonify({"location" : location})
            # Else closest dataset is empty
            else:
                return jsonify({"location" :'NaN'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000', debug=True)