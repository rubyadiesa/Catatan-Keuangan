from flask import Flask, render_template, request, redirect, flash, make_response
import json, os, uuid
from datetime import date

app = Flask(__name__)
app.secret_key = "belajar-flask"

if os.environ.get("VERCEL"):
    FOLDER_DATA = "/tmp/data"
else:
    FOLDER_DATA = "data"
os.makedirs(FOLDER_DATA, exist_ok=True)     # buat folder kalau belum ada

def id_valid(id_user):
    # KEAMANAN: kode pengunjung harus 32 karakter, isinya hanya 0-9 dan a-f.
    # Tanpa ini, orang jahat bisa mengisi cookie dengan nama file lain di server.
    if len(id_user) != 32:
        return False
    for huruf in id_user:                   # LOOPING: cek huruf satu per satu
        if huruf not in "0123456789abcdef":
            return False
    return True


def ambil_id_pengguna():
    # Baca kode pengunjung dari cookie browser. Kalau tidak ada / tidak valid -> None
    id_user = request.cookies.get("id_pengguna")
    if id_user is not None and id_valid(id_user):
        return id_user
    return None


def lokasi_file(id_user):
    # Tiap pengunjung punya file sendiri, misal: data/3f9a....json
    return os.path.join(FOLDER_DATA, id_user + ".json")

def format_rupiah(angka):
    return "Rp " + f"{angka:,}".replace(",", ".")     # 1500000 -> "Rp 1.500.000"

app.add_template_filter(format_rupiah, "rupiah")      # supaya bisa dipakai di HTML


def muat_data(id_user):
    # Kalau pengunjung ini sudah punya file -> baca. Kalau belum -> data awal (Rp 0)
    if os.path.exists(lokasi_file(id_user)):
        with open(lokasi_file(id_user)) as f:
            return json.load(f)
    return {"kantong": [{"id": 1, "nama": "Dompet", "tipe": "biasa", "target": 0}],
            "transaksi": []}


def simpan_data(id_user, data):
    with open(lokasi_file(id_user), "w") as f:
        json.dump(data, f, indent=2)


def buat_id_baru(daftar):
    terbesar = 0
    for item in daftar:
        if item["id"] > terbesar:
            terbesar = item["id"]
    return terbesar + 1


def catat(data, id_user, jenis, kategori, jumlah, kantong_id, catatan, tanggal=None):
    if tanggal is None:
        tanggal = str(date.today())
    data["transaksi"].append({
        "id": buat_id_baru(data["transaksi"]),
        "tanggal": tanggal, "jenis": jenis, "kategori": kategori,
        "jumlah": jumlah, "kantong_id": kantong_id, "catatan": catatan,
    })
    simpan_data(id_user, data)


def hitung_saldo(data, kantong_id):
    saldo = 0
    for t in data["transaksi"]:
        if t["kantong_id"] == kantong_id:
            if t["jenis"] == "pemasukan":
                saldo += t["jumlah"]
            else:
                saldo -= t["jumlah"]
    return saldo


def hitung_total(data, jenis):
    total = 0
    for t in data["transaksi"]:
        if t["jenis"] == jenis:
            total += t["jumlah"]
    return total


def nama_kantong(data, kantong_id):
    for k in data["kantong"]:
        if k["id"] == kantong_id:
            return k["nama"]
    return "-"


def buat_cashflow(data):
    daftar_bulan = []
    for t in data["transaksi"]:
        bulan = t["tanggal"][:7]
        if bulan not in daftar_bulan:
            daftar_bulan.append(bulan)
    daftar_bulan.sort(reverse=True)

    hasil = []
    terbesar = 1
    for bulan in daftar_bulan:
        masuk = 0
        keluar = 0
        for t in data["transaksi"]:
            if t["tanggal"][:7] == bulan:
                if t["jenis"] == "pemasukan":
                    masuk += t["jumlah"]
                else:
                    keluar += t["jumlah"]
        tahun, no = bulan.split("-")
        hasil.append({"nama": NAMA_BULAN[int(no) - 1] + " " + tahun,
                      "masuk": masuk, "keluar": keluar, "bersih": masuk - keluar})
        if masuk > terbesar:
            terbesar = masuk
        if keluar > terbesar:
            terbesar = keluar

    for h in hasil:
        h["lebar_masuk"] = h["masuk"] * 100 // terbesar
        h["lebar_keluar"] = h["keluar"] * 100 // terbesar
    return hasil


def beranda():
    id_user = ambil_id_pengguna()
    pengunjung_baru = False
    if id_user is None:                     # belum punya kode -> buatkan kode baru
        id_user = uuid.uuid4().hex          # uuid4().hex = kode acak 32 karakter
        pengunjung_baru = True

    data = muat_data(id_user)

    daftar_kantong = []
    for k in data["kantong"]:
        item = dict(k)
        item["saldo"] = hitung_saldo(data, k["id"])
        item["persen"] = 0
        if k["tipe"] == "tabungan" and k["target"] > 0:
            persen = item["saldo"] * 100 // k["target"]
            item["persen"] = max(0, min(persen, 100))
        daftar_kantong.append(item)

    daftar_transaksi = []
    for t in data["transaksi"]:
        item = dict(t)
        item["kantong"] = nama_kantong(data, t["kantong_id"])
        daftar_transaksi.append(item)
    daftar_transaksi.reverse()

    total_masuk = hitung_total(data, "pemasukan")
    total_keluar = hitung_total(data, "pengeluaran")

    halaman = make_response(render_template("index.html",
        kantong=daftar_kantong, transaksi=daftar_transaksi,
        total_masuk=total_masuk, total_keluar=total_keluar,
        saldo=total_masuk - total_keluar, cashflow=buat_cashflow(data),
        kategori_keluar=KATEGORI_KELUAR, kategori_masuk=KATEGORI_MASUK,
        hari_ini=str(date.today())))

    if pengunjung_baru:                     # titipkan kode ke browser selama 1 tahun
        halaman.set_cookie("id_pengguna", id_user, max_age=60 * 60 * 24 * 365,
                           httponly=True, samesite="Lax")
    return halaman

@app.route("/kantong", methods=["POST"])
def tambah_kantong():
    id_user = ambil_id_pengguna()
    if id_user is None:
        return redirect("/")
    data = muat_data(id_user)

    nama = request.form["nama"].strip()
    tipe = request.form["tipe"]
    target = int(request.form.get("target") or 0)
    saldo_awal = int(request.form.get("saldo_awal") or 0)

    if nama == "":
        flash("Nama kantong tidak boleh kosong.")
    elif tipe == "tabungan" and target <= 0:
        flash("Kantong tabungan harus punya target (goal) lebih dari 0.")
    else:
        id_baru = buat_id_baru(data["kantong"])
        data["kantong"].append({"id": id_baru, "nama": nama, "tipe": tipe, "target": target})
        simpan_data(id_user, data)
        if saldo_awal > 0:
            catat(data, id_user, "pemasukan", "Saldo Awal", saldo_awal, id_baru, "")
    return redirect("/")


@app.route("/tambah-uang", methods=["POST"])
def tambah_uang():
    id_user = ambil_id_pengguna()
    if id_user is None:
        return redirect("/")
    data = muat_data(id_user)

    jumlah = int(request.form.get("jumlah") or 0)
    if jumlah <= 0:
        flash("Jumlah uang harus lebih dari 0.")
    else:
        catat(data, id_user, "pemasukan", "Tambah Uang", jumlah,
              int(request.form["kantong_id"]), "")
    return redirect("/")


@app.route("/transaksi", methods=["POST"])
def tambah_transaksi():
    id_user = ambil_id_pengguna()
    if id_user is None:
        return redirect("/")
    data = muat_data(id_user)

    jenis = request.form["jenis"]
    jumlah = int(request.form.get("jumlah") or 0)
    kantong_id = int(request.form["kantong_id"])

    if jumlah <= 0:
        flash("Jumlah harus lebih dari 0.")
    elif jenis == "pengeluaran" and jumlah > hitung_saldo(data, kantong_id):
        flash("Saldo kantong tidak cukup untuk pengeluaran ini.")
    else:
        catat(data, id_user, jenis, request.form["kategori"], jumlah, kantong_id,
              request.form["catatan"], request.form["tanggal"])
    return redirect("/")


@app.route("/hapus/<int:id_transaksi>", methods=["POST"])
def hapus_transaksi(id_transaksi):
    id_user = ambil_id_pengguna()
    if id_user is None:
        return redirect("/")
    data = muat_data(id_user)

    target = None
    for t in data["transaksi"]:
        if t["id"] == id_transaksi:
            target = t

    if target is not None:
        saldo_sesudah = hitung_saldo(data, target["kantong_id"])
        if target["jenis"] == "pemasukan":
            saldo_sesudah -= target["jumlah"]
        if saldo_sesudah < 0:
            flash("Tidak bisa dihapus: saldo kantong akan menjadi minus.")
        else:
            data["transaksi"].remove(target)
            simpan_data(id_user, data)
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
