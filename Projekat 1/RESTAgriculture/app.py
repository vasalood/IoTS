from flask import Flask
from RESTAgriculture.routes.sensor import sensor_bp

app = Flask(__name__)

# @app.route('/')
# def home():
#     return jsonify({"message": "REST Agriculture API radi!"})

app.register_blueprint(sensor_bp, url_prefix='/api')

if __name__ == '__main__':
    app.run(debug=True)