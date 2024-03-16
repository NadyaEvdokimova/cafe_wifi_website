from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, URLField, BooleanField
from wtforms.validators import DataRequired, URL
from datetime import datetime
import os.path
import os


app = Flask(__name__)

# Connect to Database
db = SQLAlchemy()
db_name = 'cafes.db'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, db_name)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db.init_app(app)
app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY')
Bootstrap5(app)


class Cafe(db.Model):
    __tablename__ = 'cafe'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


with app.app_context():
    db.create_all()


class CafeForm(FlaskForm):
    name = StringField('Cafe name', validators=[DataRequired()])
    map_url = URLField('Location', validators=[DataRequired(), URL()])
    img_url = URLField('Image URL', validators=[DataRequired(), URL()])
    location = StringField('District', validators=[DataRequired()])
    seats = StringField('Number of seats, e.g. 30-40', validators=[DataRequired()])
    has_toilet = BooleanField('Does it have toilets')
    has_wifi = BooleanField('Does it have WiFi?')
    has_sockets = BooleanField('Are there sockets?')
    can_take_calls = BooleanField('Calls are possible?')
    coffee_price = StringField('Average coffee price', validators=[DataRequired()])
    submit = SubmitField('Submit')


@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}


@app.route("/")
def home():
    result = db.session.execute(db.select(Cafe).order_by(Cafe.name))
    all_cafes = result.scalars().all()
    cafes = [cafe.to_dict() for cafe in all_cafes]
    cafes_length = len(cafes)
    return render_template("index.html", cafes=cafes, cafes_length=cafes_length)


@app.route("/add", methods=["POST", "GET"])
def add():
    form = CafeForm()
    if form.validate_on_submit():
        name = request.form.get("name")
        map_url = request.form.get("map_url")
        img_url = request.form.get("img_url")
        location = request.form.get("location")
        seats = request.form.get("seats")
        has_toilet = bool(request.form.get("has_toilet"))
        has_wifi = bool(request.form.get("has_wifi"))
        has_sockets = bool(request.form.get("has_sockets"))
        can_take_calls = bool(request.form.get("can_take_calls"))
        coffee_price = request.form.get("coffee_price")
        new_cafe = Cafe(name=name, map_url=map_url, coffee_price=coffee_price, img_url=img_url, location=location,
                        seats=seats, has_toilet=has_toilet, has_wifi=has_wifi, has_sockets=has_sockets,
                        can_take_calls=can_take_calls)
        db.session.add(new_cafe)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template('add.html', form=form)


@app.route('/edit/<int:cafe_id>', methods=["GET", "POST"])
def edit_cafe(cafe_id):
    cafe = db.get_or_404(Cafe, cafe_id)
    edit_form = CafeForm(
        name=cafe.name,
        map_url=cafe.map_url,
        img_url=cafe.img_url,
        location=cafe.location,
        seats=cafe.seats,
        has_toilet=bool(cafe.has_toilet),
        has_wifi=bool(cafe.has_wifi),
        has_sockets=bool(cafe.has_sockets),
        can_take_calls=bool(cafe.can_take_calls),
        coffee_price=cafe.coffee_price
    )
    print(type(cafe.has_toilet))
    if edit_form.validate_on_submit():
        cafe.name = edit_form.name.data
        cafe.map_url = edit_form.map_url.data
        cafe.img_url = edit_form.img_url.data
        cafe.location = edit_form.location.data
        cafe.seats = edit_form.seats.data
        cafe.has_toilet = bool(edit_form.has_toilet.data)
        cafe.has_wifi = bool(edit_form.has_wifi.data)
        cafe.has_sockets = bool(edit_form.has_sockets.data)
        cafe.can_take_calls = bool(edit_form.can_take_calls.data)
        cafe.coffee_price = edit_form.coffee_price.data
        db.session.commit()
        print(type(edit_form.has_wifi.data))
        return redirect(url_for("home"))
    return render_template("add.html", form=edit_form, is_edit=True)


@app.route('/delete/<int:cafe_id>')
def delete_cafe(cafe_id):
    cafe = db.get_or_404(Cafe, cafe_id)
    db.session.delete(cafe)
    db.session.commit()
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=False, port=5001)
