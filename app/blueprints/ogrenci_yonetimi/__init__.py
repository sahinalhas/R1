from flask import Blueprint

ogrenci_yonetimi_bp = Blueprint('ogrenci_yonetimi', __name__, template_folder='templates')

# Import routes after defining the blueprint to avoid circular imports
# The routes will be imported in app.__init__.py