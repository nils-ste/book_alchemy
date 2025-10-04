from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from data_models import db, Author, Book
import datetime
import os

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/library.sqlite')}"
db.init_app(app)


@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    if request.method == 'GET':
        return (render_template('add_author.html'))
    elif request.method == 'POST':
        name = request.form['name']
        birth_str = request.form['birthdate']  # e.g. '1980-05-12'
        death_str = request.form.get('date_of_death', '')  # may be ''

        birth_date = datetime.date.fromisoformat(birth_str)
        date_of_death = datetime.date.fromisoformat(death_str) if death_str else None

        author = Author(name=name, birth_date=birth_date, date_of_death=date_of_death)
        db.session.add(author)
        db.session.commit()
        return redirect(url_for('add_author'))


@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'GET':
        authors = db.session.query(Author).all()
        return render_template('add_book.html', authors=authors)
    elif request.method == 'POST':
        author_id = int(request.form['author_id'])
        title = request.form['title']
        isbn = request.form['isbn']
        pub_year = request.form['publication_year']
        isbn_for_url = isbn.replace('-', '')
        cover_url = f"https://covers.openlibrary.org/b/isbn/{isbn_for_url}-M.jpg"
        book = Book(isbn=isbn, title=title, author_id=author_id, publication_year=pub_year, cover=cover_url)
        db.session.add(book)
        db.session.commit()
        return redirect(url_for('add_book'))


@app.route('/', methods=['GET'])
def index():
    sort = request.args.get('sort')

    if sort == 'title':
        books = db.session.query(Book).order_by(Book.title).all()
    elif sort == 'author':
        books = (db.session.query(Book)
                 .join(Author, Book.author_id == Author.id)
                 .order_by(Author.name)
                 .all())
    else:
        books = db.session.query(Book).all()

    authors = db.session.query(Author).all()
    return render_template('home.html', books=books, authors=authors)


"""with app.app_context():
  db.create_all()"""

if __name__ == '__main__':
    app.run(debug=True)
