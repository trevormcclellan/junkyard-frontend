from flask import Blueprint, render_template, request

main_bp = Blueprint('main', __name__, template_folder='templates')

@main_bp.route('/')
def index():
    return render_template('main/index.html')

# Add other routes and logic specific to your new region
