from quart import Quart
from quart_cors import cors
from RESTAgriculture.routes.agriculture_controller import agriculture_bp

app = Quart(__name__)
app = cors(app, allow_origin="*")

# @app.route('/')
# def home():
#     return jsonify({"message": "REST Agriculture API radi!"})

app.register_blueprint(agriculture_bp, url_prefix='/api')

if __name__ == '__main__':
    app.run(debug=True)