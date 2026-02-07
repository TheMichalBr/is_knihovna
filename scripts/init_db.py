import csv
import os
from pathlib import Path
from sqlalchemy.exc import IntegrityError

from models.database import engine, SessionLocal, Base
from models.models import Book, BookCopy, User, RoleEnum
from core.security import get_password_hash


def create_tables():
	Base.metadata.create_all(bind=engine)


def load_books(csv_path: str, db):
	added = 0
	if not os.path.exists(csv_path):
		print(f"Knihy: soubor nenalezen: {csv_path}")
		return added

	with open(csv_path, encoding="utf-8") as fh:
		reader = csv.DictReader(fh, delimiter=";")
		for row in reader:
			title = row.get("Název") or row.get("Nazev") or ""
			author = row.get("Autor") or ""
			isbn = (row.get("ISBN") or "").strip()
			try:
				publication_year = int(row.get("Rok vydání") or row.get("Rok vydani") or 0) or None
			except ValueError:
				publication_year = None
			publisher = row.get("Vydavatel") or ""
			category = row.get("Žánr") or row.get("Zanr") or ""
			try:
				pages = int(row.get("Počet stran") or row.get("Pocet stran") or 0) or None
			except ValueError:
				pages = None
			description = row.get("Popis") or ""

			if not isbn:
				continue

			existing = db.query(Book).filter(Book.isbn == isbn).first()
			if existing:
				continue

			book = Book(
				title=title.strip(),
				author=author.strip(),
				isbn=isbn,
				description=description.strip(),
				publisher=publisher.strip(),
				publication_year=publication_year,
				pages=pages,
				category=category.strip()
			)
			db.add(book)
			db.flush()

			inv_a = f"{book.id:05d}-A"
			inv_b = f"{book.id:05d}-B"
			copy_a = BookCopy(book_id=book.id, inventory_number=inv_a, condition="dobrá", is_available=True)
			copy_b = BookCopy(book_id=book.id, inventory_number=inv_b, condition="přijatelná", is_available=True)
			db.add_all([copy_a, copy_b])

			added += 1

	try:
		db.commit()
	except IntegrityError:
		db.rollback()

	print(f"Načteno knih: {added}")
	return added


def load_users(csv_path: str, db):
	added = 0
	if not os.path.exists(csv_path):
		print(f"Uživatelé: soubor nenalezen: {csv_path}")
		return added

	with open(csv_path, encoding="utf-8") as fh:
		reader = csv.DictReader(fh, delimiter=";")
		for row in reader:
			username = (row.get("Uzivatelske_jmeno") or row.get("Uzivatel") or row.get("username") or "").strip()
			password = (row.get("Heslo") or row.get("heslo") or "").strip()
			full_name = (row.get("Cele_jmeno") or row.get("Cele jmeno") or row.get("Cele_jméno") or "").strip()

			if not username or not password:
				continue

			existing = db.query(User).filter(User.username == username).first()
			if existing:
				continue

			user = User(
				username=username,
				email=f"{username}@local",
				full_name=full_name,
				password_hash=get_password_hash(password),
				role=RoleEnum.READER,
				is_active=True
			)
			db.add(user)
			added += 1

	try:
		db.commit()
	except IntegrityError:
		db.rollback()

	print(f"Načteno uživatelů: {added}")
	return added


def main():
	create_tables()
	base_dir = Path(__file__).resolve().parents[1]
	books_csv = os.path.join(base_dir, "docs", "knihy.csv")
	users_csv = os.path.join(base_dir, "docs", "uzivatele.csv")

	db = SessionLocal()
	try:
		load_books(books_csv, db)
		load_users(users_csv, db)
	finally:
		db.close()


if __name__ == "__main__":
	main()