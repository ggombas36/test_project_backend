import pandas           as pd
from   flask            import Flask, jsonify
from   flask_sqlalchemy import SQLAlchemy
from   flask_cors       import CORS

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
CORS(app)

db = SQLAlchemy(app)

class DBWData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.Float, nullable=False)
    speed = db.Column(db.Float, nullable=False)
    yaw_rate = db.Column(db.Float, nullable=True)
    v_front_left = db.Column(db.Float, nullable=True)
    v_front_right = db.Column(db.Float, nullable=True)
    v_rear_left = db.Column(db.Float, nullable=True)
    v_rear_right = db.Column(db.Float, nullable=True)

class IMUData(db.Model):
    id        = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.Float, nullable=False)
    gyro_x    = db.Column(db.Float, nullable=True)
    gyro_y    = db.Column(db.Float, nullable=True)
    gyro_z    = db.Column(db.Float, nullable=True)
    acc_x     = db.Column(db.Float, nullable=True)
    acc_y     = db.Column(db.Float, nullable=True)
    acc_z     = db.Column(db.Float, nullable=True)
    conf_gyro = db.Column(db.Float, nullable=True)
    conf_acc  = db.Column(db.Float, nullable=True)

def load_data():
    dbw_data = pd.read_csv('data/dbw.csv', na_values=['', 'null', 'undefined'], on_bad_lines='skip')
    imu_data = pd.read_csv('data/imu.csv', na_values=['', 'null', 'undefined'], on_bad_lines='skip')

    dbw_data.dropna(subset=['timestamp'], inplace=True)
    imu_data.dropna(subset=['timestamp'], inplace=True)

    dbw_data.fillna({
        'speed': 0.0,
        'yaw_rate': 0.0,
        'v_front_left': 0.0,
        'v_front_right': 0.0,
        'v_rear_left': 0.0,
        'v_rear_right': 0.0,
    }, inplace=True)

    imu_data.fillna({
        'gyro_x': 0.0,
        'gyro_y': 0.0,
        'gyro_z': 0.0,
        'acc_x': 0.0,
        'acc_y': 0.0,
        'acc_z': 0.0,
        'conf_gyro': 1.0,
        'conf_acc': 1.0,
    }, inplace=True)

    db.session.query(DBWData).delete()
    db.session.query(IMUData).delete()

    for _, row in dbw_data.iterrows():
        db.session.add(DBWData(
            timestamp=row['timestamp'],
            speed=row['speed'],
            yaw_rate=row['yaw_rate'],
            v_front_left=row['v_front_left'],
            v_front_right=row['v_front_right'],
            v_rear_left=row['v_rear_left'],
            v_rear_right=row['v_rear_right'],
        ))

    for _, row in imu_data.iterrows():
        db.session.add(IMUData(
            timestamp=row['timestamp'],
            gyro_x=row['gyro_x'],
            gyro_y=row['gyro_y'],
            gyro_z=row['gyro_z'],
            acc_x=row['acc_x'],
            acc_y=row['acc_y'],
            acc_z=row['acc_z'],
            conf_gyro=row['conf_gyro'],
            conf_acc=row['conf_acc'],
        ))
    db.session.commit()

with app.app_context():
    db.create_all()
    load_data()

@app.route('/dbw', methods=['GET'])
def get_dbw_data():
    data = DBWData.query.all()
    result = [
        {
            'id': item.id,
            'timestamp': item.timestamp,
            'speed': item.speed,
            'yaw_rate': item.yaw_rate,
            'v_front_left': item.v_front_left,
            'v_front_right': item.v_front_right,
            'v_rear_left': item.v_rear_left,
            'v_rear_right': item.v_rear_right,
        } for item in data
    ]
    return jsonify(result)

@app.route('/imu', methods=['GET'])
def get_imu_data():
    data = IMUData.query.all()
    result = [
        {
            'id': item.id,
            'timestamp': item.timestamp,
            'gyro_x': item.gyro_x,
            'gyro_y': item.gyro_y,
            'gyro_z': item.gyro_z,
            'acc_x': item.acc_x,
            'acc_y': item.acc_y,
            'acc_z': item.acc_z,
            'conf_gyro': item.conf_gyro,
            'conf_acc': item.conf_acc,
        } for item in data
    ]
    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
