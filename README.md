# E-Commerce Public Data Dashboard ✨

Dashboard ini dibuat untuk menganalisis data transaksi e-commerce Brasil, mencakup tren pesanan, kategori produk dengan pendapatan tertinggi, segmentasi pelanggan dengan RFM, dan volume transaksi per wilayah.

## Dataset
Dataset yang digunakan dalam proyek ini berasal dari **Brazilian E-Commerce Public Dataset by Olist**. Karena ukuran file yang besar, dataset tidak diunggah ke repositori ini.

## Setup Environment - Anaconda

```bash
conda create --name main-ds python=3.9
conda activate main-ds
pip install -r requirements.txt
```

## Setup Environment - Shell/Terminal

```bash
mkdir proyek_analisis_data
cd proyek_analisis_data
pipenv install
pipenv shell
pip install -r requirements.txt
```

## Menjalankan Dashboard

Pastikan file berikut berada dalam folder yang sama dengan `dashboard.py`:

- `orders_dataset.csv`
- `order_items_dataset.csv`
- `products_dataset.csv`
- `product_category_name_translation.csv`
- `customers_dataset.csv`
- `order_payments_dataset.csv`

Lalu jalankan dashboard dengan perintah berikut:

```bash
streamlit run dashboard.py
```

## Catatan

Dashboard akan terbuka otomatis di browser lokal setelah perintah dijalankan.
