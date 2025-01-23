from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask import request, jsonify

# Inicjalizacja aplikacji Flask
app = Flask(__name__)

# Konfiguracja bazy danych
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kino.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicjalizacja SQLAlchemy
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

    seanse = db.relationship('Seans', backref='film', lazy=True) #db.relationship - służy do definiowania relacji między tabelami

# Tabela Seanse
class Seans(db.Model):
    __tablename__ = 'seanse'
    id = db.Column(db.Integer, primary_key=True)
    film_id = db.Column(db.Integer, db.ForeignKey('filmy.id'), nullable=False)  #ForeignKey tworzy relację między tabelą Seanse ( kolumna film_id), a tabelą Filmy.
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
    miejsca = db.Column(db.Text, nullable=False)  # Lista miejsc w formacie tekstowym np. "A1, A2"
    status = db.Column(db.String(50), nullable=False)  # Status np. "potwierdzona", "anulowana"
    unikalny_kod = db.Column(db.String(100), unique=True, nullable=False)

# Tabela Administratorzy
class Administrator(db.Model):
    __tablename__ = 'administratorzy'
    id = db.Column(db.Integer, primary_key=True)
    imie = db.Column(db.String(100), nullable=False)
    nazwisko = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    haslo = db.Column(db.String(200), nullable=False)  # Hasło powinno być zaszyfrowane
    rola = db.Column(db.String(50), nullable=False)  # np. "zarządca", "pracownik kina"

# Funkcja tworząca bazy danych
#@app.before_first_request
#def create_tables():
#    db.create_all()

# Wyświetlanie wszystkich filmów lub konkretnego filmu
@app.route('/filmy', methods=['GET'])
def get_filmy():
    # Pobranie wszystkich filmów
    filmy = Film.query.all()
    # Zwrócenie listy filmów w formacie JSON
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
    # Pobranie konkretnego filmu
    film = Film.query.get_or_404(film_id)
    # Zwrócenie szczegółów filmu w formacie JSON
    return jsonify({
        'id': film.id,
        'tytul': film.tytul,
        'opis': film.opis,
        'gatunek': film.gatunek,
        'dlugosc': film.dlugosc,
        'data_premiery': film.data_premiery.strftime('%Y-%m-%d'),
        'plakat_url': film.plakat_url
    }), 200

# Dodawanie nowego filmu
@app.route('/filmy', methods=['POST'])
def add_film():
    # Pobranie danych z żądania
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Brak danych w żądaniu'}), 400
    
    try:
        # Utworzenie nowego obiektu Film
        nowy_film = Film(
            tytul=data['tytul'],
            opis=data.get('opis', ''),  # Opis jest opcjonalny
            gatunek=data['gatunek'],
            dlugosc=data['dlugosc'],
            data_premiery=datetime.strptime(data['data_premiery'], '%Y-%m-%d'),
            plakat_url=data.get('plakat_url')  # Plakat URL jest opcjonalny
        )
        # Dodanie filmu do bazy danych
        db.session.add(nowy_film)
        db.session.commit()
        # Zwrócenie odpowiedzi
        return jsonify({'message': 'Film został dodany', 'id': nowy_film.id}), 201
    except KeyError as e:
        return jsonify({'error': f'Brakuje pola: {e}'}), 400
    except ValueError as e:
        return jsonify({'error': 'Nieprawidłowy format danych'}), 400


@app.route('/filmy/<tytul>/<opis>/<gatunek>/<int:dlugosc>/<data_premiery>/<path:plakat_url>', methods=['POST'])
def add_film_via_url(tytul, opis, gatunek, dlugosc, data_premiery, plakat_url):
    try:
        # Utworzenie nowego filmu na podstawie danych z URL
        nowy_film = Film(
            tytul=tytul,
            opis=opis,
            gatunek=gatunek,
            dlugosc=dlugosc,
            data_premiery=datetime.strptime(data_premiery, '%Y-%m-%d'),
            plakat_url=plakat_url
        )
        db.session.add(nowy_film)
        db.session.commit()
        return jsonify({'message': 'Film został dodany', 'id': nowy_film.id}), 201
    except ValueError as e:
        return jsonify({'error': 'Nieprawidłowy format danych w URL'}), 400

if __name__ == '__main__':
    with app.app_context():
      db.create_all()
      app.run(debug=True)