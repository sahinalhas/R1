from flask import Blueprint

calisma_programi_bp = Blueprint('calisma_programi', __name__, template_folder='templates')

# Import routes after defining the blueprint to avoid circular imports
# The routes will be imported in app.__init__.py