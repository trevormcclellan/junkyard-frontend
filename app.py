from flask import Flask
from utah.routes import utah_bp
from main.routes import main_bp

app = Flask(__name__)

# Register region-specific blueprints
app.register_blueprint(main_bp)        # Main site at /
app.register_blueprint(utah_bp, url_prefix='/utah')  # Utah site at /utah

if __name__ == '__main__':
    app.run(debug=True, port=5001)
