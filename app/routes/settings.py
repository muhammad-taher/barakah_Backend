from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.core import StoreSettings
from flask_jwt_extended import jwt_required

settings_bp = Blueprint('settings', __name__, url_prefix='/api/v1/settings')

@settings_bp.route('/', methods=['GET'])
def get_settings():
    settings = StoreSettings.query.all()
    result = {s.key: s.value for s in settings}
    return jsonify(result), 200

@settings_bp.route('/', methods=['PUT'])
@jwt_required()
def update_settings():
    data = request.get_json()
    for key, value in data.items():
        setting = StoreSettings.query.filter_by(key=key).first()
        if setting:
            setting.value = value
        else:
            new_setting = StoreSettings(key=key, value=value)
            db.session.add(new_setting)
    db.session.commit()
    return jsonify({"message": "Settings updated successfully"}), 200
