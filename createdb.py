import sqlite3, json

# load data json dan create database
with open('data.json') as f:
    source = json.load(f)

# koneksikan ke database smartphone.db
conn = sqlite3.connect('smartphone.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS smartphone
            (ID INTEGER PRIMARY KEY,
            nama_produk TEXT,
            harga_produk INTEGER,
            rating_produk FLOAT,
            id_produk INTEGER,
            stock_produk INTEGER,
            produk_terjual INTEGER,
            lokasi_penjual TEXT,
            kategori TEXT)''')

for phone in source:
    c.execute("INSERT INTO smartphone (nama_produk, harga_produk, rating_produk, id_produk, stock_produk, produk_terjual, lokasi_penjual, kategori) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (phone['nama_produk'], phone['harga_produk'], phone['rating_produk'], phone['id_produk'], phone['stock_produk'], phone['produk_terjual'], phone['lokasi_penjual'], phone['kategori']))
conn.commit()