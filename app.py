# ===== app.py : "otak" website (backend) =====
# Tugasnya: menyimpan data, menghitung saldo, lalu mengirim hasilnya ke halaman HTML.

from flask import Flask, render_template, request, redirect, flash
import json, os
from datetime import date

app = Flask(__name__)          # membuat aplikasi web
app.secret_key = "belajar-flask"  # kunci rahasia, wajib ada supaya pesan peringatan (flash) jalan

# ---------- VARIABEL & LIST (data tetap) ----------
FILE_DATA = "data.json"        # nama file tempat data disimpan
NAMA_BULAN = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]
KATEGORI_KELUAR = ["Makan", "Transportasi", "Groceries", "Amal", "Tagihan", "Hiburan", "Pendidikan", "Lainnya"]
KATEGORI_MASUK = ["Gaji", "Uang Saku", "Hadiah", "Lainnya"]


# ---------- FUNCTION: alat-alat kecil ----------
def format_rupiah(angka):
    # 1500000 -> "Rp 1.500.000"
    return "Rp " + f"{angka:,}".replace(",", ".")

# mendaftarkan function di atas supaya bisa dipakai di HTML: {{ angka | rupiah }}
app.add_template_filter(format_rupiah, "rupiah")


def muat_data():
    # Kalau file data sudah ada -> baca isinya. Kalau belum -> pakai data awal.
    if os.path.exists(FILE_DATA):
        with open(FILE_DATA) as f:      # "with" = buka file, otomatis ditutup setelah selesai
            return json.load(f)
    return {"kantong": [{"id": 1, "nama": "Dompet", "tipe": "biasa", "target": 0}],
            "transaksi": []}


def simpan_data():
    # Menulis isi variabel data ke file supaya tidak hilang saat program dimatikan
    with open(FILE_DATA, "w") as f:
        json.dump(data, f, indent=2)


data = muat_data()   # data berisi 2 list: daftar kantong & daftar transaksi.
                     # Tiap isi list berupa "kotak berlabel" (dictionary), misal t["jumlah"]


def buat_id_baru(daftar):
    # LOOPING: cari nomor id terbesar, lalu tambah 1
    terbesar = 0
    for item in daftar:
        if item["id"] > terbesar:
            terbesar = item["id"]
    return terbesar + 1


def catat(jenis, kategori, jumlah, kantong_id, catatan, tanggal=None):
    # Menambah satu transaksi ke list lalu menyimpannya
    if tanggal is None:
        tanggal = str(date.today())
    data["transaksi"].append({
        "id": buat_id_baru(data["transaksi"]),
        "tanggal": tanggal, "jenis": jenis, "kategori": kategori,
        "jumlah": jumlah, "kantong_id": kantong_id, "catatan": catatan,
    })
    simpan_data()


def hitung_saldo(kantong_id):
    # Saldo kantong = semua pemasukan - semua pengeluaran milik kantong itu
    saldo = 0
    for t in data["transaksi"]:                 # LOOPING: cek transaksi satu per satu
        if t["kantong_id"] == kantong_id:       # IF: hanya milik kantong ini
            if t["jenis"] == "pemasukan":
                saldo += t["jumlah"]
            else:
                saldo -= t["jumlah"]
    return saldo


def hitung_total(jenis):
    # Jumlahkan semua transaksi dengan jenis tertentu ("pemasukan" / "pengeluaran")
    total = 0
    for t in data["transaksi"]:
        if t["jenis"] == jenis:
            total += t["jumlah"]
    return total


def nama_kantong(kantong_id):
    for k in data["kantong"]:
        if k["id"] == kantong_id:
            return k["nama"]
    return "-"


def buat_cashflow():
    # Cashflow = uang masuk vs uang keluar, dikelompokkan per bulan
    daftar_bulan = []                       # LIST berisi bulan unik, misal "2026-10"
    for t in data["transaksi"]:
        bulan = t["tanggal"][:7]            # ambil 7 huruf pertama dari "2026-10-10"
        if bulan not in daftar_bulan:
            daftar_bulan.append(bulan)
    daftar_bulan.sort(reverse=True)         # bulan terbaru di atas

    hasil = []
    terbesar = 1                            # untuk menghitung panjang batang grafik
    for bulan in daftar_bulan:
        masuk = 0
        keluar = 0
        for t in data["transaksi"]:
            if t["tanggal"][:7] == bulan:
                if t["jenis"] == "pemasukan":
                    masuk += t["jumlah"]
                else:
                    keluar += t["jumlah"]
        tahun, no = bulan.split("-")        # "2026-10" -> tahun "2026", no "10"
        hasil.append({"nama": NAMA_BULAN[int(no) - 1] + " " + tahun,
                      "masuk": masuk, "keluar": keluar, "bersih": masuk - keluar})
        if masuk > terbesar:
            terbesar = masuk
        if keluar > terbesar:
            terbesar = keluar

    for h in hasil:                         # panjang batang dalam persen (0-100)
        h["lebar_masuk"] = h["masuk"] * 100 // terbesar
        h["lebar_keluar"] = h["keluar"] * 100 // terbesar
    return hasil


# ---------- HALAMAN UTAMA ----------
# @app.route = "kalau ada yang buka alamat ini, jalankan function di bawahnya"
@app.route("/")
def beranda():
    daftar_kantong = []
    for k in data["kantong"]:
        item = dict(k)                      # salin dulu, supaya data asli tidak berubah
        item["saldo"] = hitung_saldo(k["id"])
        item["persen"] = 0
        if k["tipe"] == "tabungan" and k["target"] > 0:
            persen = item["saldo"] * 100 // k["target"]
            item["persen"] = max(0, min(persen, 100))   # dijaga tetap di 0 sampai 100
        daftar_kantong.append(item)

    daftar_transaksi = []
    for t in data["transaksi"]:
        item = dict(t)
        item["kantong"] = nama_kantong(t["kantong_id"])
        daftar_transaksi.append(item)
    daftar_transaksi.reverse()              # transaksi terbaru di atas

    total_masuk = hitung_total("pemasukan")
    total_keluar = hitung_total("pengeluaran")

    # Kirim semua hasil hitungan ke file HTML
    return render_template("index.html",
                           kantong=daftar_kantong, transaksi=daftar_transaksi,
                           total_masuk=total_masuk, total_keluar=total_keluar,
                           saldo=total_masuk - total_keluar, cashflow=buat_cashflow(),
                           kategori_keluar=KATEGORI_KELUAR, kategori_masuk=KATEGORI_MASUK,
                           hari_ini=str(date.today()))


# ---------- MENERIMA DATA DARI FORM ----------
# request.form = isi form yang dikirim pengguna. redirect("/") = kembali ke halaman utama.
@app.route("/kantong", methods=["POST"])
def tambah_kantong():
    nama = request.form["nama"].strip()
    tipe = request.form["tipe"]                          # "biasa" atau "tabungan"
    target = int(request.form.get("target") or 0)        # "or 0" = kalau kosong, anggap 0
    saldo_awal = int(request.form.get("saldo_awal") or 0)

    if nama == "":
        flash("Nama kantong tidak boleh kosong.")
    elif tipe == "tabungan" and target <= 0:
        flash("Kantong tabungan harus punya target (goal) lebih dari 0.")
    else:
        id_baru = buat_id_baru(data["kantong"])
        data["kantong"].append({"id": id_baru, "nama": nama, "tipe": tipe, "target": target})
        if saldo_awal > 0:
            catat("pemasukan", "Saldo Awal", saldo_awal, id_baru, "")
        simpan_data()
    return redirect("/")


@app.route("/tambah-uang", methods=["POST"])
def tambah_uang():
    jumlah = int(request.form.get("jumlah") or 0)
    if jumlah <= 0:
        flash("Jumlah uang harus lebih dari 0.")
    else:
        catat("pemasukan", "Tambah Uang", jumlah, int(request.form["kantong_id"]), "")
    return redirect("/")


@app.route("/transaksi", methods=["POST"])
def tambah_transaksi():
    jenis = request.form["jenis"]
    jumlah = int(request.form.get("jumlah") or 0)
    kantong_id = int(request.form["kantong_id"])

    if jumlah <= 0:
        flash("Jumlah harus lebih dari 0.")
    elif jenis == "pengeluaran" and jumlah > hitung_saldo(kantong_id):
        flash("Saldo kantong tidak cukup untuk pengeluaran ini.")
    else:
        catat(jenis, request.form["kategori"], jumlah, kantong_id,
              request.form["catatan"], request.form["tanggal"])
    return redirect("/")


@app.route("/hapus/<int:id_transaksi>", methods=["POST"])
def hapus_transaksi(id_transaksi):
    target = None
    for t in data["transaksi"]:                 # cari transaksi yang id-nya cocok
        if t["id"] == id_transaksi:
            target = t

    if target is not None:
        saldo_sesudah = hitung_saldo(target["kantong_id"])
        if target["jenis"] == "pemasukan":
            saldo_sesudah -= target["jumlah"]   # menghapus pemasukan = saldo berkurang
        if saldo_sesudah < 0:
            flash("Tidak bisa dihapus: saldo kantong akan menjadi minus.")
        else:
            data["transaksi"].remove(target)    # buang dari list
            simpan_data()
    return redirect("/")


# Baris ini artinya: "kalau file ini dijalankan langsung, nyalakan websitenya"
if __name__ == "__main__":
    app.run(debug=True)
