# Catatan Uang Harian

Website sederhana untuk mencatat uang harian: mengatur kantong-kantong uang, mencatat pemasukan dan pengeluaran, menabung untuk sebuah goal, dan melihat cashflow tiap bulan.

Proyek ini dibuat sebagai latihan belajar pemrograman, jadi kodenya sengaja dibuat sederhana dan setiap bagian diberi komentar penjelasan.

## Fitur

- **Kantong uang**: buat beberapa kantong (misal Dompet, Rekening, Uang Darurat), masing-masing punya saldo sendiri.
- **Tambah uang**: isi saldo kantong kapan saja.
- **Transaksi**: tambah dan hapus pemasukan atau pengeluaran.
- **Kategori**: pengeluaran (Makan, Transportasi, Groceries, Amal, Tagihan, Hiburan, Pendidikan, Lainnya) dan pemasukan (Gaji, Uang Saku, Hadiah, Lainnya).
- **Kantong tabungan**: kantong yang punya goal (target), lengkap dengan batang progres persen.
- **Cashflow**: perbandingan uang masuk dan uang keluar per bulan.
- **Ringkasan**: saldo sekarang, total pemasukan, dan total pengeluaran.
- **Pengaman**: pengeluaran ditolak jika saldo kantong tidak cukup.

## Teknologi

| Bagian | Yang dipakai |
|---|---|
| Backend | Python + Flask |
| Tampilan | HTML (template Jinja), CSS |
| Interaksi | JavaScript |
| Penyimpanan data | File JSON per pengunjung (folder `data/`) |

## Struktur Folder

```
pencatat-uang/
├── app.py                 # Backend: hitung saldo, simpan data, atur halaman
├── requirements.txt       # Daftar library Python yang dibutuhkan
├── templates/
│   └── index.html         # Halaman website
└── static/
    ├── style.css          # Warna dan tata letak
    └── script.js          # Bagian interaktif (kategori, konfirmasi hapus)
```

Folder `data/` akan muncul sendiri. Setiap pengunjung punya file datanya sendiri di dalamnya.

## Cara Menjalankan

1. Pastikan Python sudah terpasang (cek dengan `python --version`).
2. Buka terminal di folder proyek (folder yang berisi `app.py`).
3. Pasang Flask:
   ```
   pip install -r requirements.txt
   ```
4. Jalankan:
   ```
   python app.py
   ```
5. Buka browser dan masuk ke `http://127.0.0.1:5000`.

Untuk mematikan website, tekan `Ctrl + C` di terminal.

## Cara Memakai

1. **Buat kantong** lewat form "Buat kantong baru". Pilih "Kantong tabungan" jika ingin ada goal, lalu isi targetnya.
2. **Tambah uang** ke kantong lewat form "Tambah uang ke kantong".
3. **Catat transaksi** lewat form di bagian Transaksi. Pilih jenis, kategori, kantong, jumlah, dan tanggal.
4. **Hapus transaksi** dengan tombol "Hapus" di tabel. Saldo kantong otomatis menyesuaikan.
5. **Lihat cashflow** di bagian paling bawah.

## Cara Kerja Singkat

- Data disimpan dalam dua list: daftar kantong dan daftar transaksi.
- Saldo kantong tidak disimpan, tetapi dihitung ulang dari semua transaksi milik kantong itu. Karena itu, menghapus transaksi otomatis memperbaiki saldo.
- "Saldo awal" dan "Tambah uang" dicatat sebagai pemasukan, sehingga ikut terhitung di cashflow.
- Python menghitung semuanya, lalu mengirim hasilnya ke `index.html` untuk ditampilkan.

## Catatan Penting

- **Data tiap pengunjung terpisah.** Browser pengunjung diberi kode unik (cookie), dan datanya disimpan di `data/<kode>.json`. Pengunjung baru selalu mulai dari Rp 0. Data hanya bisa dibuka di browser yang sama, karena belum ada login.
- **Jangan unggah folder `data/` ke GitHub** (sudah dicegah oleh `.gitignore`), karena berisi data pribadi.
- **Di Vercel data bisa hilang sewaktu-waktu.** Vercel hanya menyediakan penyimpanan sementara. Untuk data permanen, pakai hosting yang menyimpan file (misalnya PythonAnywhere) atau database.
- Website ini belum memakai login, jadi siapa pun yang bisa membukanya bisa melihat dan mengubah data.

## Ide Pengembangan

- Hapus kantong
- Pindah uang antar kantong
- Filter transaksi per bulan atau per kategori
- Grafik pengeluaran per kategori
- Login supaya data aman
- Ganti `data.json` dengan database (SQLite)
