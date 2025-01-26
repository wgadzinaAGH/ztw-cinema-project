from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask import request, jsonify

# Inicjalizacja aplikacji Flask
app = Flask(__name__)

# Konfiguracja bazy danych
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kino.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'


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
    plakat_url = db.Column(db.String(1000), nullable=True)

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


with app.app_context():
    db.create_all()

#Funkcja tworząca bazy danych
#@app.before_first_request
#def create_tables():
   # db.create_all()

@app.route('/')
def home():
    return "Witaj! Użyj /filmy, aby zobaczyć listę filmów lub skorzystaj z innych dostępnych endpointów.", 200


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

@app.route('/api/dodaj_film/<string:tytul>/<string:opis>/<string:gatunek>/<int:dlugosc>/<string:data_premiery>/<string:plakat_url>', methods=['GET'])
def add_film_via_url(tytul, opis, gatunek, dlugosc, data_premiery, plakat_url):
    try:
        # Konwersja daty z formatu string na obiekt datetime
        data_premiery_parsed = datetime.strptime(data_premiery, '%Y-%m-%d').date()
        
        # Utworzenie nowego obiektu Film
        nowy_film = Film(
            tytul=tytul,
            opis=opis,
            gatunek=gatunek,
            dlugosc=dlugosc,
            data_premiery=data_premiery_parsed,
            plakat_url=plakat_url
        )
        
        # Dodanie filmu do bazy danych
        db.session.add(nowy_film)
        db.session.commit()
        
        # Zwrócenie odpowiedzi z ID nowo dodanego filmu
        return jsonify({
            'status': 'success',
            'message': 'Film został dodany',
            'film_id': nowy_film.id
        }), 201

    except ValueError:
        return jsonify({'status': 'error', 'message': 'Nieprawidłowy format daty. Oczekiwano: YYYY-MM-DD'}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Wystąpił błąd: {str(e)}'}), 500



@app.route('/api/rezerwacja/<int:film_id>/<string:data>/<string:godzina>/<string:miejsce>', methods=['GET'])
def zarezerwuj_bilet(film_id, data, godzina, miejsce):
    try:
        # Sprawdzenie, czy podany film istnieje
        film = Film.query.get(film_id)
        if not film:
            return jsonify({'status': 'error', 'message': 'Film nie istnieje'}), 404

        # Sprawdzenie, czy seans w podanym dniu i godzinie istnieje
        seans = Seans.query.filter_by(film_id=film_id, data=datetime.strptime(data, '%Y-%m-%d').date(), godzina=datetime.strptime(godzina, '%H:%M').time()).first()
        if not seans:
            return jsonify({'status': 'error', 'message': 'Seans nie istnieje w podanym dniu i godzinie'}), 404

        # Sprawdzenie, czy miejsce jest już zajęte
        zajete_miejsca = [rez.miejsca for rez in seans.rezerwacje]
        if miejsce in ','.join(zajete_miejsca):
            return jsonify({'status': 'error', 'message': 'Miejsce jest już zajęte'}), 400

        # Tworzenie nowej rezerwacji
        nowa_rezerwacja = Rezerwacja(
            klient_id=None,  # Możesz tu dodać logikę przypisywania do użytkownika
            seans_id=seans.id,
            miejsca=miejsce,
            status='potwierdzona',
            unikalny_kod=str(film_id) + miejsce + datetime.now().strftime('%Y%m%d%H%M%S')  # Generowanie unikalnego kodu
        )

        # Zapisanie rezerwacji w bazie danych
        db.session.add(nowa_rezerwacja)
        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'Rezerwacja została potwierdzona',
            'unikalny_kod': nowa_rezerwacja.unikalny_kod,
            'film': film.tytul,
            'data': data,
            'godzina': godzina,
            'miejsce': miejsce
        }), 201
    except ValueError:
        return jsonify({'status': 'error', 'message': 'Nieprawidłowe dane wejściowe'}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Wystąpił błąd: {str(e)}'}), 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Tworzenie tabel w bazie danych
    app.run(debug=True)  # Uruchomienie serwera
