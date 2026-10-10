// script.js : bagian "interaktif" di browser (tanpa reload halaman)

// FUNCTION 1: mengisi pilihan kategori sesuai jenis transaksi
function isiKategori() {
  var jenis = document.getElementById("jenis").value;   // VARIABEL: ambil pilihan jenis
  var pilihan;                                          // akan berisi LIST kategori

  // IF ELSE: pemasukan dan pengeluaran punya kategori berbeda
  if (jenis == "pemasukan") {
    pilihan = KATEGORI_MASUK;
  } else {
    pilihan = KATEGORI_KELUAR;
  }

  var kotak = document.getElementById("kategori");
  kotak.innerHTML = "";                                 // kosongkan dulu isinya

  // LOOPING: tambahkan satu <option> untuk setiap kategori di list
  for (var i = 0; i < pilihan.length; i++) {
    kotak.innerHTML += "<option>" + pilihan[i] + "</option>";
  }
}

// FUNCTION 2: kolom "goal" hanya muncul kalau memilih kantong tabungan
function tampilkanTarget() {
  var tipe = document.getElementById("tipe").value;
  var kolomTarget = document.getElementById("target");

  if (tipe == "tabungan") {
    kolomTarget.style.display = "block";   // tampilkan
  } else {
    kolomTarget.style.display = "none";    // sembunyikan
  }
}

// FUNCTION 3: tanya dulu sebelum menghapus. true = lanjut, false = batal
function konfirmasiHapus() {
  return confirm("Yakin ingin menghapus transaksi ini?");
}

// Jalankan sekali saat halaman pertama dibuka
isiKategori();
tampilkanTarget();
