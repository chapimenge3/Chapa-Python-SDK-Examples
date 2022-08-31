import datetime
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from .models import Book, Transaction
from . import db

router = Blueprint('auth', __name__)

# CRUD for books


@router.route('/books', methods=['GET', 'POST'])
@login_required
def books():
    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')
        year = request.form.get('year')
        price = request.form.get('price')
        user = current_user
        if not title or not author or not year or not price:
            flash('Please fill in all the fields', 'danger')
            return redirect(url_for('book.create_book'))

        book = Book(title=title, author=author, year=year,
                    price=price, user_id=user.id)
        db.session.add(book)
        db.session.commit()
        flash('Book created successfully', 'success')
    else:
        # paginated query
        page = request.args.get('page', 1, type=int)
        books = Book.query.filter_by(
            user_id=current_user.id).paginate(page, per_page=5)
        return render_template('books.html', books=books)

# create book get route


@router.route('/create_book', methods=['GET'])
@login_required
def create_book():
    return render_template('create_book.html')


@router.route('/books/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_book(id):
    book = Book.query.get_or_404(id)
    if book.user_id != current_user.id:
        flash('You cannot edit this book', 'danger')
        return redirect(url_for('auth.books'))
    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')
        year = request.form.get('year')
        price = request.form.get('price')
        if not title or not author or not year or not price:
            flash('Please fill in all the fields', 'danger')
            return redirect(url_for('auth.edit_book', id=id))
        book.title = title
        book.author = author
        book.year = year
        book.price = price
        db.session.commit()
        flash('Book updated successfully', 'success')
        return redirect(url_for('book.books'))
    else:
        return render_template('edit_book.html', book=book)


@router.route('/books/<int:id>/delete', methods=['GET', 'POST'])
@login_required
def delete_book(id):
    book = Book.query.get_or_404(id)
    if book.user_id != current_user.id:
        flash('You cannot delete this book', 'danger')
        return redirect(url_for('auth.books'))
    if request.method == 'POST':
        db.session.delete(book)
        db.session.commit()
        flash('Book deleted successfully', 'success')
        return redirect(url_for('auth.books'))
    else:
        return render_template('delete_book.html', book=book)

# show


@router.route('/books/<int:id>', methods=['GET'])
@login_required
def show_book(id):
    book = Book.query.get_or_404(id)
    return render_template('show_book.html', book=book)


def create_chapa_checkout(data):
    pass


# buy
@router.route('/books/<int:id>/buy', methods=['GET'])
@login_required
def buy_book(id):
    book = Book.query.get_or_404(id)
    if book.user_id == current_user.id:
        flash('You cannot buy your own book', 'danger')
        return redirect(url_for('auth.books'))

    # create chapa transaction
    checkout = create_chapa_checkout({})

    transaction = Transaction(
        user_id=current_user.id, book_id=book.id, price=book.price,
        date=datetime.datetime.now(), chapa_url=checkout.checkout_url
    )
    
    db.session.add(transaction)
    db.session.commit()

    return redirect(checkout.checkout_url)


@router.route('/books/webhook', methods=['POST'])
@login_required
def book_webhook():
    # get headers
    pass

