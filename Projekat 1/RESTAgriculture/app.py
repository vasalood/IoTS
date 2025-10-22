from quart import Quart
from quart_cors import cors
from routes.agriculture_controller import agriculture_bp

app = Quart(__name__)
app = cors(app, allow_origin="*")

app.register_blueprint(agriculture_bp, url_prefix='/api')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)