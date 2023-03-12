from seleniumwire import webdriver  # Import from seleniumwire
from seleniumwire.utils import decode
import json
import time

# Create a new instance of the Chrome driver
opsi = webdriver.ChromeOptions()
opsi.add_argument('--headless') # agar tidak menampilkan browser saat menjalankan script
driver = webdriver.Chrome(options=opsi)
# Go to the Google home page
driver.get('https://shopee.co.id/search?keyword=smartphone')
time.sleep(10)

for request in driver.requests: # Access requests via the `requests` attribute
    if request.response:
        if request.url.startswith('https://shopee.co.id/api/v4/search/search_items?by=relevancy&keyword='):
            response = request.response
            body = decode(response.body, response.headers.get('Content-Encoding', 'Identity'))
            decoded_body = body.decode('utf8') # data didecode menjadi utf8 agar bisa menampilkan html dari bentuk bytecode yang diperoleh
            json_data = json.loads(decoded_body)

            rows = json_data['items']
            # Mencari rata2 harga
            total_harga = 0
            for i in range(0, len(rows)):
                total_harga += int(json_data['items'][i]['item_basic']['price']/100000) #dibagi 100.000 disesuaikan dari tampilan diwebsite dan di api
            rata2_harga = total_harga / len(rows)
            # print(rata2_harga)

            # ---SCRAP API---
            data = []
            for i in range(0, len(rows)):
                nama_produk     = json_data['items'][i]['item_basic']['name']
                harga_produk    = int(json_data['items'][i]['item_basic']['price']/100000)
                rating_produk   = float("{:.1f}".format(float(json_data['items'][i]['item_basic']['item_rating']['rating_star'])))
                id_produk       = int(json_data['items'][i]['item_basic']['shopid'])
                stock_produk    = int(json_data['items'][i]['item_basic']['stock'])
                produk_terjual  = int(json_data['items'][i]['item_basic']['historical_sold'])
                lokasi_penjual  = json_data['items'][i]['item_basic']['shop_location']

                # Mengkategorikan produk
                kategori = ''
                if harga_produk > rata2_harga and rating_produk > 4 and produk_terjual > 10:
                    kategori = 'layak dibeli'
                elif harga_produk > rata2_harga and rating_produk < 4 and produk_terjual > 10:
                    kategori = 'perlu dipertimbangkan'
                elif harga_produk > rata2_harga and rating_produk > 4 and produk_terjual < 10:
                    kategori = 'perlu dipertimbangkan'
                else:
                    kategori = 'tidak direkomendasikan'

                data.append(
                    {
                        'nama_produk'   : nama_produk,
                        'harga_produk'  : harga_produk,
                        'rating_produk' : rating_produk,
                        'id_produk'     : id_produk,
                        'stock_produk'  : stock_produk,
                        'produk_terjual': produk_terjual,
                        'lokasi_penjual': lokasi_penjual,
                        'kategori'      : kategori
                    }
                )


with open('data.json', 'w') as f:
    json.dump(data, f)
    print('---SUCCESS---')
