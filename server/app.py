#!/usr/bin/env python3

from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate

from models import db, Bakery, BakedGood

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

@app.route('/')
def home():
    return '<h1>Bakery GET-POST-PATCH-DELETE API</h1>'


# ---------------- GET ROUTES ---------------- #

@app.route('/bakeries', methods=['GET'])
def bakeries():
    bakeries = [bakery.to_dict() for bakery in Bakery.query.all()]
    return make_response(jsonify(bakeries), 200)


@app.route('/bakeries/<int:id>', methods=['GET', 'PATCH'])
def bakery_by_id(id):
    bakery = Bakery.query.filter_by(id=id).first()

    if not bakery:
        return make_response(jsonify({"error": "Bakery not found"}), 404)

    if request.method == 'GET':
        return make_response(jsonify(bakery.to_dict()), 200)

    elif request.method == 'PATCH':
        data = request.form
        if "name" in data:
            bakery.name = data["name"]
            db.session.commit()
        return make_response(jsonify(bakery.to_dict()), 200)


@app.route('/baked_goods/by_price', methods=['GET'])
def baked_goods_by_price():
    baked_goods = BakedGood.query.order_by(BakedGood.price.desc()).all()
    return make_response(jsonify([bg.to_dict() for bg in baked_goods]), 200)


@app.route('/baked_goods/most_expensive', methods=['GET'])
def most_expensive_baked_good():
    most_expensive = BakedGood.query.order_by(BakedGood.price.desc()).first()
    if not most_expensive:
        return make_response(jsonify({"error": "No baked goods found"}), 404)
    return make_response(jsonify(most_expensive.to_dict()), 200)


# ---------------- POST ROUTE ---------------- #

@app.route('/baked_goods', methods=['POST'])
def create_baked_good():
    data = request.form

    new_bg = BakedGood(
        name=data.get("name"),
        price=data.get("price"),
        bakery_id=data.get("bakery_id"),
    )

    db.session.add(new_bg)
    db.session.commit()

    return make_response(jsonify(new_bg.to_dict()), 201)


# ---------------- DELETE ROUTE ---------------- #

@app.route('/baked_goods/<int:id>', methods=['DELETE'])
def delete_baked_good(id):
    bg = BakedGood.query.filter_by(id=id).first()

    if not bg:
        return make_response(jsonify({"error": "Baked good not found"}), 404)

    db.session.delete(bg)
    db.session.commit()

    return make_response(jsonify({"message": "Baked good deleted"}), 200)


# ---------------- MAIN ---------------- #

if __name__ == '__main__':
    app.run(port=5555, debug=True)
