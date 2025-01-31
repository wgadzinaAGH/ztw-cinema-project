from flask import Flask, request, Response, jsonify, render_template, redirect, url_for, g, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import check_password_hash
import random
import string
import logging


# Inicjalizacja aplikacji Flask
app = Flask(__name__)

# Konfiguracja bazy danych
app.logger.setLevel(logging.INFO)
app.config['SECRET_KEY'] = 'sekret'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kino.db'


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

@app.before_request
def load_database():
    g.kino = {
        "admin" : Administrator.query.all(), 
        "film" : Film.query.all(), 
        "rezerwacja" : Rezerwacja.query.all(),
        "seans" : Seans.query.all(),
        "klient" : Klient.query.all()
    }

@app.route('/')
def index():
    return render_template('index.html', gKino = g.kino)

@app.route('/onas')
def onas():
    return render_template('onas.html')

@app.route('/repertuar')
def repertuar():
    return render_template('repertuar.html', gKino = g.kino)

@app.route('/kontakt')
def kontakt():
    return render_template('kontakt.html')

# Wyświetlanie wszystkich filmów lub konkretnego filmu
@app.route('/api/filmy', methods=['GET'])
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

@app.route('/api/rezerwacja1', methods=['GET'])
def get_rezerwacja():
    # Pobranie wszystkich filmów
    rezerwacje = Rezerwacja.query.all()
    # Zwrócenie listy filmów w formacie JSON
    return jsonify([{
        'id': rezerwacja.id,
        'klient_id': rezerwacja.klient_id,
        'seans_id': rezerwacja.seans_id,
        'miejsca': rezerwacja.miejsca,
        'status': rezerwacja.status,
        'unikalny_kod': rezerwacja.unikalny_kod
    } for rezerwacja in rezerwacje]), 200

@app.route('/api/film/<int:film_id>', methods=['GET'])
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

@app.route('/api/seanse', methods=['GET'])
def get_seanse():
    # Pobranie wszystkich seansów
    seanse = Seans.query.all()
    
    # Zwrócenie listy seansów w formacie JSON
    return jsonify([{
        'id': seans.id,
        'film_id': seans.film_id,
        'data': seans.data.strftime('%Y-%m-%d'),
        'godzina': seans.godzina.strftime('%H:%M'),
        'sala': seans.sala,
        'cena': seans.cena
    } for seans in seanse]), 200

@app.route('/api/dodaj_film/<string:tytul>/<string:opis>/<string:gatunek>/<int:dlugosc>/<string:data_premiery>/<string:plakat_url>', methods=['GET', 'POST'])
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

@app.route('/api/rezerwacja/<int:film_id>/<string:data>/<string:godzina>/<string:miejsce>', methods=['GET', 'POST'])
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


# Lista dozwolonych użytkowników
ADMIN_CREDENTIALS = {
    "admin@ac.com": "123456",
    "pracownik@ac.com": "kino2025",
    "admin": "admin"
}

def check_auth(username, password):
    """Sprawdza, czy podane dane są poprawne"""
    return username in ADMIN_CREDENTIALS and ADMIN_CREDENTIALS[username] == password

def authenticate():
    """Zwraca nagłówek 401, który powoduje wyświetlenie okienka logowania"""
    return Response(
        'Podaj poprawne dane logowania.', 401,
        {'WWW-Authenticate': 'Basic realm="Admin Panel"'}
    )

@app.route('/admin')
def admin():
    auth = request.authorization
    if not auth or not check_auth(auth.username, auth.password):
        return authenticate()

    return render_template('admin.html', username=auth.username, gKino = g.kino)  # Panel administracyjny

@app.route('/admin/logout')
def logout():
    """Wylogowanie użytkownika"""
    return redirect(url_for('admin'))

@app.route('/admin/sprawdz-rezerwacje', methods=['GET', 'POST'])
def sprawdz_rezerwacje():
    rezerwacja = None
    message = None
    if request.method == 'POST':
        unikalny_kod = request.form.get('unikalny_kod')
        
        # Sprawdzamy, czy rezerwacja istnieje
        rezerwacja = Rezerwacja.query.filter_by(unikalny_kod=unikalny_kod).first()
        
        if not rezerwacja:
            message = "Nie znaleziono rezerwacji o podanym kodzie."
        # W przeciwnym razie, rezerwacja została znaleziona i wyświetlamy jej szczegóły
        
    return render_template('sprawdz_rezerwacje.html', rezerwacja=rezerwacja, message=message)

@app.route('/admin/usun-rezerwacje', methods=['GET', 'POST'])
def usun_rezerwacje_menu():
    if request.method == 'POST':
        # Pobieramy unikalny kod z formularza
        unikalny_kod = request.form.get('unikalny_kod')

        if not unikalny_kod:
            flash('Proszę podać kod rezerwacji.', 'error')
            return redirect(url_for('usun_rezerwacje_menu'))

        # Szukamy rezerwacji po unikalnym kodzie
        rezerwacja = Rezerwacja.query.filter_by(unikalny_kod=unikalny_kod).first()

        if not rezerwacja:
            flash('Rezerwacja o podanym kodzie nie istnieje.', 'error')
        else:
            db.session.delete(rezerwacja)
            db.session.commit()
            flash('Rezerwacja została usunięta!', 'success')

        return redirect(url_for('usun_rezerwacje_menu'))

    # Pobieramy wszystkie rezerwacje, by je wyświetlić
    rezerwacje = Rezerwacja.query.all()
    return render_template('usun_rezerwacje.html', rezerwacje=rezerwacje)


@app.route('/admin/zmien-rezerwacje', methods=['GET', 'POST'])
def zmien_rezerwacje():
    if request.method == 'POST':
        unikalny_kod = request.form.get('unikalny_kod')
        
        # Szukamy rezerwacji według kodu
        rezerwacja = Rezerwacja.query.filter_by(unikalny_kod=unikalny_kod).first()
        
        if not rezerwacja:
            flash('Nie znaleziono rezerwacji o podanym kodzie.', 'error')
            return redirect(url_for('zmien_rezerwacje'))
        
        return redirect(url_for('zmien_rezerwacje_form', rezerwacja_id=rezerwacja.id))
    
    return render_template('zmien_rezerwacje.html')

@app.route('/admin/zmien-rezerwacje/<int:rezerwacja_id>', methods=['GET', 'POST'])
def zmien_rezerwacje_form(rezerwacja_id):
    rezerwacja = Rezerwacja.query.get(rezerwacja_id)
    
    if not rezerwacja:
        flash('Rezerwacja nie istnieje!', 'error')
        return redirect(url_for('zmien_rezerwacje'))
    
    if request.method == 'POST':
        # Pobieramy dane z formularza
        rezerwacja.miejsca = request.form.get('nowe_miejsca')
        rezerwacja.status = request.form.get('status')
        db.session.commit()
        flash('Rezerwacja została zmieniona!', 'success')
        return redirect(url_for('sprawdz_rezerwacje'))
    
    return render_template('zmien_rezerwacje_form.html', rezerwacja=rezerwacja)

# wyświetlnanie, dodwanie, usuwanie, edycja rekordów do baz danych
@app.route('/admin/bazy', methods=['GET'])
def admin_bazy():
    return render_template('admin_bazy.html')

@app.route('/podsumowanie/<seans_id>/<klient_id>')
def podsumowanie(seans_id, klient_id):
    return render_template('podsumowanie.html', seans_id = seans_id, klient_id = klient_id)

@app.route('/dane_osobowe/<seans_id>/<klient_id>')
def dane_osobowe(seans_id, klient_id):
    return render_template('daneosobowe.html', seans_id = seans_id, klient_id = klient_id)

@app.route('/wybor_miejsca/<seans_id>/<tytul>/<dzien>/<godzina>/<sala>')
def wybor_miejsca(seans_id, tytul, dzien, godzina, sala):
    return render_template('wybormiejsca.html', gKino = g.kino, seans_id = seans_id,  tytul = tytul, dzien = dzien, godzina = godzina, sala = sala)

@app.route('/api/rezerwacja', methods=['POST'])
def zarezerwuj_miejsce():
    dane = request.json
    print("Odebrano dane:", dane)
    
    data = request.json
    seans_id = data.get('seans_id')
    miejsca = data.get('miejsca')  # Lista miejsc np. ["1A", "1B"]
    klient_id = data.get('klient_id')
    if not seans_id or not miejsca or not klient_id:
        return jsonify({'error': 'Brakuje danych wejściowych'}), 400
    # Sprawdź, czy miejsca są już zajęte
    zajete_miejsca = Rezerwacja.query.filter_by(seans_id=seans_id).all()
    zajete_miejsca_set = set()
    for rez in zajete_miejsca:
        zajete_miejsca_set.update(rez.miejsca.split(', '))
    if any(miejsce in zajete_miejsca_set for miejsce in miejsca):
        return jsonify({'error': 'Jedno lub więcej miejsc jest już zajętych'}), 400
    # Tworzenie nowej rezerwacji
    unikalny_kod = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    nowa_rezerwacja = Rezerwacja(
        klient_id=klient_id,
        seans_id=seans_id,
        miejsca=', '.join(miejsca),
        status='potwierdzona',
        unikalny_kod=unikalny_kod
    )
    db.session.add(nowa_rezerwacja)
    db.session.commit()
    return jsonify({
        'message': 'Rezerwacja zakończona sukcesem!',
        'unikalny_kod': unikalny_kod,
        'miejsca': miejsca
    }), 200

@app.route('/api/klienci', methods=['POST']) #dodawanie klienta
def dodaj_klienta():
    data = request.json  # Pobranie danych z żądania

    # Sprawdzenie, czy wszystkie wymagane pola są obecne
    if not all(key in data for key in ['imie', 'nazwisko', 'email']):
        return jsonify({'error': 'Brak wymaganych pól'}), 400

    # Sprawdzenie, czy e-mail jest unikalny
    if Klient.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Podany adres e-mail już istnieje'}), 409  # Kod 409 - konflikt

    try:
        # Tworzenie nowego klienta
        nowy_klient = Klient(
            imie=data['imie'],
            nazwisko=data['nazwisko'],
            email=data['email']
        )

        db.session.add(nowy_klient)
        db.session.commit()

        return jsonify({'message': 'Klient dodany pomyślnie', 'id': nowy_klient.id}), 201  # 201 - Created
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500  # 500 - Internal Server Error

@app.route('/admin/bazy/zarzadzaj_filmami', methods=['GET', 'POST'])
def zarzadzaj_filmami():
    message = None
    filmy = Film.query.all()  # Pobieranie wszystkich filmów z bazy w kolejności wg daty premiery

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

    return render_template('admin_bazy_zarzadzaj_filmami.html', message=message, filmy=filmy)

@app.route('/admin/bazy/zarzadzaj_filmami/edytuj/<int:film_id>', methods=['GET', 'POST'])
def edytuj_film(film_id):
    film = Film.query.get_or_404(film_id)  # Pobieramy film z bazy na podstawie jego ID

    if request.method == 'POST':
        # Pobieramy dane z formularza
        film.tytul = request.form['tytul']
        film.opis = request.form['opis']
        film.gatunek = request.form['gatunek']
        film.dlugosc = int(request.form['dlugosc'])
        film.data_premiery = datetime.strptime(request.form['data_premiery'], '%Y-%m-%d')
        film.plakat_url = request.form['plakat_url']

        try:
            # Zatwierdzamy zmiany w bazie danych
            db.session.commit()
            message = "Film został pomyślnie zaktualizowany!"
            return redirect(url_for('zarzadzaj_filmami', message=message))  # Przekierowanie do strony admin
        except Exception as e:
            db.session.rollback()  # W razie błędu cofamy zmiany
            message = f"Wystąpił błąd: {str(e)}"
            return render_template('admin_bazy_zarzadzaj_filmami_edytuj.html', film=film, message=message)

    return render_template('admin_bazy_zarzadzaj_filmami_edytuj.html', film=film)

@app.route('/admin/bazy/zarzadzaj_filmami/usun/<int:film_id>', methods=['GET'])
def usun_film(film_id):
    film = Film.query.get_or_404(film_id)
    try:
        db.session.delete(film)
        db.session.commit()
        message = "Film został pomyślnie usunięty!"
    except Exception as e:
        db.session.rollback()
        message = f"Wystąpił błąd: {str(e)}"

    return redirect(url_for('zarzadzaj_filmami', message=message))

@app.route('/admin/bazy/zarzadzaj_seansami', methods=['GET', 'POST'])
def zarzadzaj_seansami():
    message = None
    seanse = Seans.query.order_by(Seans.film_id).all()  # Pobieranie seansów, sortowane po dacie i godzinie

    if request.method == 'POST':
        film_id = request.form.get('film_id')
        data = request.form.get('data')
        godzina = request.form.get('godzina')
        sala = request.form.get('sala')
        cena = request.form.get('cena')
        try:
            nowy_seans = Seans(
                film_id=int(film_id),
                data=datetime.strptime(data, '%Y-%m-%d'),
                godzina=datetime.strptime(godzina, '%H:%M').time(),
                sala=sala,
                cena=float(cena)
            )
            db.session.add(nowy_seans)
            db.session.commit()
            message = "Seans został pomyślnie dodany!"
        except Exception as e:
            db.session.rollback()
            message = f"Wystąpił błąd: {str(e)}"

    return render_template('admin_bazy_zarzadzaj_seansami.html', message=message, seanse=seanse)

@app.route('/admin/bazy/zarzadzaj_seansami/edytuj/<int:seans_id>', methods=['GET', 'POST'])
def edytuj_seans(seans_id):
    seans = Seans.query.get_or_404(seans_id)  # Pobieramy seans z bazy na podstawie jego ID
    filmy = Film.query.all()

    if request.method == 'POST':
        # Pobieramy dane z formularza
        seans.film_id = int(request.form['film_id'])
        seans.data = datetime.strptime(request.form['data'], '%Y-%m-%d')
        seans.godzina = datetime.strptime(request.form['godzina'], '%H:%M').time()
        seans.sala = request.form['sala']
        seans.cena = float(request.form['cena'])

        try:
            # Zatwierdzamy zmiany w bazie danych
            db.session.commit()
            message = "Seans został pomyślnie zaktualizowany!"
            return redirect(url_for('zarzadzaj_seansami', message=message))  # Przekierowanie do strony admin
        except Exception as e:
            db.session.rollback()  # W razie błędu cofamy zmiany
            message = f"Wystąpił błąd: {str(e)}"
            return render_template('admin_bazy_zarzadzaj_seansami_edytuj.html', seans=seans, message=message)

    return render_template('admin_bazy_zarzadzaj_seansami_edytuj.html', seans=seans, filmy=filmy)

@app.route('/admin/bazy/zarzadzaj_seansami/usun/<int:seans_id>', methods=['GET'])
def usun_seans(seans_id):
    seans = Seans.query.get_or_404(seans_id)
    try:
        db.session.delete(seans)
        db.session.commit()
        message = "Seans został pomyślnie usunięty!"
    except Exception as e:
        db.session.rollback()
        message = f"Wystąpił błąd: {str(e)}"

    return redirect(url_for('zarzadzaj_seansami', message=message))

@app.route('/admin/bazy/zarzadzaj_rezerwacjami', methods=['GET', 'POST'])
def zarzadzaj_rezerwacjami():
    message = None
    rezerwacje = Rezerwacja.query.order_by(Rezerwacja.id.desc()).all()  # Pobieranie wszystkich rezerwacji, sortowanie malejąco po ID

    if request.method == 'POST':
        klient_id = request.form.get('klient_id')
        seans_id = request.form.get('seans_id')
        miejsca = request.form.get('miejsca')
        status = request.form.get('status')

        try:
            nowa_rezerwacja = Rezerwacja(
                klient_id=int(klient_id),
                seans_id=int(seans_id),
                miejsca=miejsca,
                status=status,
                unikalny_kod=f"{seans_id}-{miejsca}-{datetime.now().strftime('%Y%m%d%H%M%S')}"  # Generowanie unikalnego kodu
            )
            db.session.add(nowa_rezerwacja)
            db.session.commit()
            message = "Rezerwacja została pomyślnie dodana!"
        except Exception as e:
            db.session.rollback()
            message = f"Wystąpił błąd: {str(e)}"

    return render_template('admin_bazy_zarzadzaj_rezerwacjami.html', message=message, rezerwacje=rezerwacje)

@app.route('/admin/bazy/zarzadzaj_rezerwacjami/edytuj/<int:rezerwacja_id>', methods=['GET', 'POST'])
def edytuj_rezerwacje(rezerwacja_id):
    rezerwacja = Rezerwacja.query.get_or_404(rezerwacja_id)  # Pobieramy rezerwację na podstawie ID
    seanse = Seans.query.all()
    klienci = Klient.query.all()

    if request.method == 'POST':
        # Pobieramy dane z formularza
        rezerwacja.klient_id = int(request.form['klient_id'])
        rezerwacja.seans_id = int(request.form['seans_id'])
        rezerwacja.miejsca = request.form['miejsca']
        rezerwacja.status = request.form['status']

        try:
            # Zatwierdzamy zmiany w bazie danych
            db.session.commit()
            message = "Rezerwacja została pomyślnie zaktualizowana!"
            return redirect(url_for('zarzadzaj_rezerwacjami', message=message))  # Przekierowanie do widoku rezerwacji
        except Exception as e:
            db.session.rollback()  # W razie błędu cofamy zmiany
            message = f"Wystąpił błąd: {str(e)}"
            return render_template('admin_bazy_zarzadzaj_rezerwacjami_edytuj.html', rezerwacja=rezerwacja, message=message)

    return render_template('admin_bazy_zarzadzaj_rezerwacjami_edytuj.html', rezerwacja=rezerwacja, seanse=seanse, klienci=klienci)

@app.route('/admin/bazy/zarzadzaj_rezerwacjami/usun/<int:rezerwacja_id>', methods=['GET'])
def usun_rezerwacje(rezerwacja_id):
    rezerwacja = Rezerwacja.query.get_or_404(rezerwacja_id)
    try:
        db.session.delete(rezerwacja)
        db.session.commit()
        message = "Rezerwacja została pomyślnie usunięta!"
    except Exception as e:
        db.session.rollback()
        message = f"Wystąpił błąd: {str(e)}"

    return redirect(url_for('zarzadzaj_rezerwacjami', message=message))

@app.route('/admin/bazy/zarzadzaj_klientami', methods=['GET', 'POST'])
def zarzadzaj_klientami():
    message = None
    klienci = Klient.query.all()  # Pobieranie wszystkich klientów, sortowanie po nazwisku

    if request.method == 'POST':
        imie = request.form.get('imie')
        nazwisko = request.form.get('nazwisko')
        email = request.form.get('email')

        try:
            nowy_klient = Klient(
                imie=imie,
                nazwisko=nazwisko,
                email=email
            )
            db.session.add(nowy_klient)
            db.session.commit()
            message = "Klient został pomyślnie dodany!"
        except Exception as e:
            db.session.rollback()
            message = f"Wystąpił błąd: {str(e)}"

    return render_template('admin_bazy_zarzadzaj_klientami.html', message=message, klienci=klienci)

@app.route('/admin/bazy/zarzadzaj_klientami/edytuj/<int:klient_id>', methods=['GET', 'POST'])
def edytuj_klienta(klient_id):
    klient = Klient.query.get_or_404(klient_id)  # Pobieramy klienta na podstawie ID

    if request.method == 'POST':
        # Pobieramy dane z formularza
        klient.imie = request.form['imie']
        klient.nazwisko = request.form['nazwisko']
        klient.email = request.form['email']

        try:
            # Zatwierdzamy zmiany w bazie danych
            db.session.commit()
            message = "Dane klienta zostały pomyślnie zaktualizowane!"
            return redirect(url_for('zarzadzaj_klientami', message=message))  # Przekierowanie do widoku klientów
        except Exception as e:
            db.session.rollback()  # W razie błędu cofamy zmiany
            message = f"Wystąpił błąd: {str(e)}"
            return render_template('admin_bazy_zarzadzaj_klientami_edytuj.html', klient=klient, message=message)

    return render_template('admin_bazy_zarzadzaj_klientami_edytuj.html', klient=klient)

@app.route('/admin/bazy/zarzadzaj_klientami/usun/<int:klient_id>', methods=['GET'])
def usun_klienta(klient_id):
    klient = Klient.query.get_or_404(klient_id)
    try:
        db.session.delete(klient)
        db.session.commit()
        message = "Klient został pomyślnie usunięty!"
    except Exception as e:
        db.session.rollback()
        message = f"Wystąpił błąd: {str(e)}"

    return redirect(url_for('zarzadzaj_klientami', message=message))

@app.route('/admin/bazy/zarzadzaj_administratorami', methods=['GET', 'POST'])
def zarzadzaj_administratorami():
    message = None
    administratorzy = Administrator.query.order_by(Administrator.nazwisko.asc()).all()  # Pobieranie wszystkich administratorów, sortowanie po nazwisku

    if request.method == 'POST':
        imie = request.form.get('imie')
        nazwisko = request.form.get('nazwisko')
        email = request.form.get('email')
        haslo = request.form.get('haslo')
        rola = request.form.get('rola')

        try:
            nowy_administrator = Administrator(
                imie=imie,
                nazwisko=nazwisko,
                email=email,
                haslo=haslo,  # Hasło powinno być zaszyfrowane
                rola=rola
            )
            db.session.add(nowy_administrator)
            db.session.commit()
            message = "Administrator został pomyślnie dodany!"
        except Exception as e:
            db.session.rollback()
            message = f"Wystąpił błąd: {str(e)}"

    return render_template('admin_bazy_zarzadzaj_administratorami.html', message=message, administratorzy=administratorzy)

@app.route('/admin/bazy/zarzadzaj_administratorami/edytuj/<int:admin_id>', methods=['GET', 'POST'])
def edytuj_administratora(admin_id):
    administrator = Administrator.query.get_or_404(admin_id)  # Pobieramy administratora na podstawie ID

    if request.method == 'POST':
        # Pobieramy dane z formularza
        administrator.imie = request.form['imie']
        administrator.nazwisko = request.form['nazwisko']
        administrator.email = request.form['email']
        haslo = request.form.get('haslo')
        if haslo:  # Zmiana hasła, tylko jeśli zostało wprowadzone
            administrator.haslo = haslo
        administrator.rola = request.form['rola']

        try:
            # Zatwierdzamy zmiany w bazie danych
            db.session.commit()
            message = "Dane administratora zostały pomyślnie zaktualizowane!"
            return redirect(url_for('zarzadzaj_administratorami', message=message))  # Przekierowanie do widoku administratorów
        except Exception as e:
            db.session.rollback()  # W razie błędu cofamy zmiany
            message = f"Wystąpił błąd: {str(e)}"
            return render_template('admin_bazy_zarzadzaj_administratorami_edytuj.html', administrator=administrator, message=message)

    return render_template('admin_bazy_zarzadzaj_administratorami_edytuj.html', administrator=administrator)

@app.route('/admin/bazy/zarzadzaj_administratorami/usun/<int:admin_id>', methods=['GET'])
def usun_administratora(admin_id):
    administrator = Administrator.query.get_or_404(admin_id)
    try:
        db.session.delete(administrator)
        db.session.commit()
        message = "Administrator został pomyślnie usunięty!"
    except Exception as e:
        db.session.rollback()
        message = f"Wystąpił błąd: {str(e)}"

    return redirect(url_for('zarzadzaj_administratorami', message=message))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Tworzenie tabel w bazie danych
    app.run(debug=True)  # Uruchomienie serwera