from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Inicjalizacja aplikacji Flask
app = Flask(__name__)

# Konfiguracja bazy danych
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kino.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicjalizacja SQLAlchemy i Flask-Migrate
db = SQLAlchemy(app)

# Tabela Filmy
class Film(db.Model):
    __tablename__ = 'filmy'
    id = db.Column(db.Integer, primary_key=True)
    tytul = db.Column(db.String(150), nullable=False)
    opis = db.Column(db.Text, nullable=True)
    gatunek = db.Column(db.String(50), nullable=False)
    dlugosc = db.Column(db.Integer, nullable=False)
    data_premiery = db.Column(db.Date, nullable=False)
    plakat_url = db.Column(db.String(300), nullable=True)

    seanse = db.relationship('Seans', backref='film', lazy=True)

# Tabela Seanse
class Seans(db.Model):
    __tablename__ = 'seanse'
    id = db.Column(db.Integer, primary_key=True)
    film_id = db.Column(db.Integer, db.ForeignKey('filmy.id'), nullable=False)
    data = db.Column(db.Date, nullable=False)
    godzina = db.Column(db.Time, nullable=False)
    sala = db.Column(db.String(10), nullable=False)
    cena = db.Column(db.Float, nullable=False)

    rezerwacje = db.relationship('Rezerwacja', backref='seans', lazy=True)

# Tabela Klienci
class Klient(db.Model):
    __tablename__ = 'klienci'
    id = db.Column(db.Integer, primary_key=True)
    imie = db.Column(db.String(100), nullable=False)
    nazwisko = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)

    rezerwacje = db.relationship('Rezerwacja', backref='klient', lazy=True)

# Tabela Rezerwacje
class Rezerwacja(db.Model):
    __tablename__ = 'rezerwacje'
    id = db.Column(db.Integer, primary_key=True)
    klient_id = db.Column(db.Integer, db.ForeignKey('klienci.id'), nullable=False)
    seans_id = db.Column(db.Integer, db.ForeignKey('seanse.id'), nullable=False)
    miejsca = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), nullable=False)
    unikalny_kod = db.Column(db.String(100), unique=True, nullable=False)

# Tabela Administratorzy
class Administrator(db.Model):
    __tablename__ = 'administratorzy'
    id = db.Column(db.Integer, primary_key=True)
    imie = db.Column(db.String(100), nullable=False)
    nazwisko = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    haslo = db.Column(db.String(200), nullable=False)
    rola = db.Column(db.String(50), nullable=False)

# Endpointy
@app.route('/filmy', methods=['GET'])
def get_filmy():
    filmy = Film.query.all()
    return jsonify([{
        'id': film.id,
        'tytul': film.tytul,
        'opis': film.opis,
        'gatunek': film.gatunek,
        'dlugosc': film.dlugosc,
        'data_premiery': film.data_premiery.strftime('%Y-%m-%d'),
        'plakat_url': film.plakat_url
    } for film in filmy]), 200

@app.route('/filmy/<int:film_id>', methods=['GET'])
def get_film(film_id):
    film = Film.query.get(film_id)
    if not film:
        return jsonify({'error': 'Film nie został znaleziony'}), 404

    return jsonify({
        'id': film.id,
        'tytul': film.tytul,
        'opis': film.opis,
        'gatunek': film.gatunek,
        'dlugosc': film.dlugosc,
        'data_premiery': film.data_premiery.strftime('%Y-%m-%d'),
        'plakat_url': film.plakat_url
    }), 200

@app.route('/filmy', methods=['POST'])
def add_film():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Brak danych w żądaniu'}), 400

    try:
        nowy_film = Film(
            tytul=data['tytul'],
            opis=data.get('opis', ''),
            gatunek=data['gatunek'],
            dlugosc=data['dlugosc'],
            data_premiery=datetime.strptime(data['data_premiery'], '%Y-%m-%d'),
            plakat_url=data.get('plakat_url')
        )
        db.session.add(nowy_film)
        db.session.commit()
        return jsonify({'message': 'Film został dodany', 'id': nowy_film.id}), 201
    except KeyError as e:
        db.session.rollback()
        return jsonify({'error': f'Brakuje pola: {e}'}), 400
    except ValueError:
        db.session.rollback()
        return jsonify({'error': 'Nieprawidłowy format danych'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Wystąpił błąd: {e}'}), 500

@app.route('/filmy/<tytul>/<opis>/<gatunek>/<int:dlugosc>/<data_premiery>/<path:plakat_url>', methods=['POST'])
def add_film_via_url(tytul, opis, gatunek, dlugosc, data_premiery, plakat_url):
    try:
        # Tworzenie nowego obiektu Film
        nowy_film = Film(
            tytul=tytul,
            opis=opis,
            gatunek=gatunek,
            dlugosc=dlugosc,
            data_premiery=datetime.strptime(data_premiery, '%Y-%m-%d'),
            plakat_url=plakat_url
        )
        # Dodanie i zapis w bazie danych
        db.session.add(nowy_film)
        db.session.commit()
        return jsonify({'message': 'Film został dodany', 'id': nowy_film.id}), 201
    except ValueError:
        db.session.rollback()
        return jsonify({'error': 'Nieprawidłowy format daty. Użyj YYYY-MM-DD.'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Wystąpił błąd: {e}'}), 500

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    message = None
    if request.method == 'POST':
        tytul = request.form.get('tytul')
        opis = request.form.get('opis')
        gatunek = request.form.get('gatunek')
        dlugosc = request.form.get('dlugosc')
        data_premiery = request.form.get('data_premiery')
        plakat_url = request.form.get('plakat_url')

        try:
            nowy_film = Film(
                tytul=tytul,
                opis=opis,
                gatunek=gatunek,
                dlugosc=int(dlugosc),
                data_premiery=datetime.strptime(data_premiery, '%Y-%m-%d'),
                plakat_url=plakat_url
            )
            db.session.add(nowy_film)
            db.session.commit()
            message = "Film został pomyślnie dodany!"
        except Exception as e:
            db.session.rollback()
            message = f"Wystąpił błąd: {str(e)}"

    return render_template('admin.html', message=message)

if __name__ == '__main__':
    app.run(debug=True)