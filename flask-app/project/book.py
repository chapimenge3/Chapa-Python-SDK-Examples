import datetime
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from chapa import Chapa
from .models import Book, Transaction
from . import db, chapa


router = Blueprint('books', __name__)

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
        return redirect(url_for('books.books'))
    else:
        books = Book.query.filter_by()
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
        return redirect(url_for('books.books'))
    else:
        return render_template('edit_book.html', book=book)


@router.route('/books/<int:id>/delete', methods=['GET', 'POST'])
@login_required
def delete_book(id):
    print('YESS')
    book = Book.query.get_or_404(id)
    if book.user_id != current_user.id:
        flash('You cannot delete this book', 'danger')
        return redirect(url_for('books.book'))
    if request.method == 'POST':
        db.session.delete(book)
        db.session.commit()
        flash('Book deleted successfully', 'success')
    return redirect(url_for('books.books'))


@router.route('/books/<int:id>', methods=['GET'])
@login_required
def show_book(id):
    book = Book.query.get_or_404(id)
    return render_template('show_book.html', book=book)


def create_chapa_checkout(data):
    response = chapa.initialize(**data)
    print('Response', response.status, response.message)
    if response.status != 'success':
        return None

    return response.data

# buy
@router.route('/books/<int:id>/buy', methods=['POST'])
@login_required
def buy_book(id):
    book = Book.query.get_or_404(id)
    if book.user_id == current_user.id:
        flash('You cannot buy your own book', 'danger')
        return redirect(url_for('books.books'))

    transaction = Transaction(
        user_id=current_user.id, book_id=book.id, price=book.price,
        date=datetime.datetime.now(), chapa_url=None
    )
    db.session.add(transaction)
    db.session.commit()

    print('\n\n\Transaction id', transaction.id, (current_user.name + " ").split(maxsplit=1))

    name = (current_user.name + " ").split(maxsplit=1)

    first_name, last_name = 'None', 'None'
    first_name = name[0]
    if len(name) != 1:
        last_name = name[1]

    # create chapa transaction
    data = {
        'email': current_user.email,
        'amount': book.price,
        'tx_ref': transaction.id,
        'first_name': first_name or 'None',
        'last_name': last_name or 'None',
        'callback_url': f'https://37ad-197-156-86-208.in.ngrok.io{url_for("books.book_buy_success")}',
        'customization': {
            'title': 'Amazing Company',
            'description': 'This is a test project for chapa python sdk'
        }
    }
    checkout = create_chapa_checkout(data)
    
    if not checkout:
        # send report to log file or admin here.
        flash('Error happened, please try agan')
        return redirect(url_for('books.show_book', id=id))

    transaction.chapa_url = checkout.checkout_url
    db.session.add(transaction)

    return redirect(checkout.checkout_url)

@router.route('/books/webhook', methods=['POST'])
def book_webhook():
    print(request.headers)
    print(request.cookies)
    print(request.data)
    print(request.args)
    print(request.form)
    print(request.endpoint)
    print(request.method)
    print(request.remote_addr)

    return {
        "sucess": True
    }

