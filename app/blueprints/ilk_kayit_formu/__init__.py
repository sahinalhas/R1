from flask import Blueprint

ilk_kayit_formu_bp = Blueprint('ilk_kayit_formu', __name__, template_folder='templates')

# Import routes after defining the blueprint to avoid circular imports
# The routes will be imported in app.__init__.py