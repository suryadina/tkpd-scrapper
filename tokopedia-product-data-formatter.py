#!/usr/bin/env python

import sys
import re
import csv
import time
import math
import argparse
import pprint
import os.path

'''
TOKOPEDIA SCRAP RESULT FORMATTER
Created by Ardya Suryadinata (deenata.com)
Check README file for more detailed infomation.
'''


def genuri(productname):
    # Fungsi untuk men-generate URI Produk
    # versi 2.5: mengenerate URI Produk yang akan di-upload
    producturigenerated = productname
    chartoremove = ['&', '*', '\\', "'", '(', ')',
                    '+', '!', '@', '$', '%', '^', '~',
                    '`', '"', '{', '}', '|', '=', ',', '.', '?']
    for ch in chartoremove:
        producturigenerated = producturigenerated.replace(ch, "")
    chartoremove = ["<", ">"]
    for ch in chartoremove:
        producturigenerated = producturigenerated.replace(ch, " ")
    producturigenerated = producturigenerated.replace("/", " /")
    producturigenerated = producturigenerated.replace("/", "")
    producturigenerated = producturigenerated.replace(" ", "-")
    producturigenerated = producturigenerated.lower()
    producturigenerated = "-".join(filter(None, producturigenerated.split("-")))
    return producturigenerated


def roundup(x):
    # Fungsi untuk membulatkan nilai harga:
    if x < 20000:
        return int(math.ceil(x / 100.0)) * 100
    elif x >= 20000:
        return int(math.ceil(x / 1000.0)) * 1000


def markupharga(bbb, ccc, eee=3000):
    # fungsi untuk mark up harga dari suppplier
    # aaa = hargamodaltotal
    # bbb = hargaretail
    # ccc = pemesananminimal
    # ddd = marginyangdiinginkan
    # eee = nominalmarginminimal
    # fff = hargajualminimal
    # ggg = hargajualdiinginkan
    # hhh = hargajualfix

    # step 1. hitung harga modal total
    if bbb == 0 or ccc == 0:
        return 0
    else:
        aaa = bbb * ccc
        # step 2. tentukan margin yang ingin diperoleh
        if 0 <= bbb <= 1499:
            ddd = float(0.50)
        elif 1500 <= bbb <= 5999:
            ddd = float(0.45)
        elif 6000 <= bbb <= 30999:
            ddd = float(0.20)
        elif 31000 <= bbb <= 60999:
            ddd = float(0.15)
        elif 61000 <= bbb <= 159999:
            ddd = float(0.125)
        elif bbb > 159999:
            ddd = float(0.10)
        # step 3. Tentukan margin minimal atau wajib.
        # jadi apapun produknya sekali transaksi minimal dapat margin ini
        # eee = 3000 .mulai versi 2.4. user bisa
        # memasukkan min margin yang diinginkan
        # step 4. menghitung hargajual minimal/wajib per satuan barang
        fff = (float(eee) + float(aaa))
        # step 5. menghitung hargajual yang diinginkan
        ggg = (float(aaa) / ((ddd - float(1)) * float(-1)))
        # step 6. memilih hargajual akhir yang akan digunakan
        if fff > ggg:  # kalo harga jual wajib/minimal  lebih besar
            if bbb >= 6000:
                ggg = fff
            # kalo harga modal di bawah 5000 per pcs
            # naikin jumlah pemesanan minimal
            else:
                while fff > ggg:
                    ccc = ccc + 1
                    aaa = bbb * ccc
                    ggg = (float(aaa) / ((ddd - float(1)) * float(-1)))

        ggg = ggg / float(ccc)
        hhh = roundup(ggg)
        hargadanpemesananmin = {'hargajual': hhh, 'pemesananminimal': ccc}
        return hargadanpemesananmin


def parsingarguments():
    # added 30 Oktober 2016. versi 2.4
    # versi tool
    version = " version 2.8.1 by ardya suryadinata"
    # membuat parser dan deskripsi tool
    parser = argparse.ArgumentParser(description="TOKOPEDIA SCRAP RESULT FORMATTER" + "\n" + version)
    # opsi untuk menampilkan versi
    parser.add_argument("--version", help="print version", action="store_true")
    # opsi untuk meminta inputan file input yang akan di format
    parser.add_argument("--input", help="Masukkan nama input file yang akan di-format")
    # opsi untuk meminta inputan file input yang akan di format
    parser.add_argument("--output", help="Masukkan nama output file hasil format")
    # opsi untuk minimal profit hasil markup
    parser.add_argument("--minmargin", help="Masukkan minimal margin yang diinginkan (integer) (default = 3000)", type=int)
    # opsi untuk mengatur etalase tempat produk akan disimpan (format khusus unutk tokopedia)
    parser.add_argument("--etalase", help="Masukkan Etalase yang diinginkan (default = Sale)")
    # option to create human read friendly output
    parser.add_argument("--humanprint", help="Option to enable human read-friendly output (default: False). Use compare log file as input")
    # melakukan parsing arguments
    args = parser.parse_args()
    # melakukan validasi dan tindak lanjut
    # dari argument yang berhasil diparsing
    if args.version:
        print sys.argv[0].split("\\")[-1] + " " + version
        sys.exit()
    if not args.input:
        parser.error("Input file belum dimasukkan (--input required)")
    if not args.output:
        parser.error("Nama file output belum dimasukkan (--output required)")
    # menyimpan argumen dari user
    argumendariuser = {
        'input': args.input,
        'output': args.output,
        'minmargin': args.minmargin,
        'etalase': args.etalase,
        'humanprint': args.humanprint
    }
    return argumendariuser


def field_format(type):
    field_raw = [
        'Nama Produk',
        'Harga Ecer',
        'Minimal Pembelian',
        'Berat Produk',
        'Asuransi',
        'Kondisi Produk',
        'Kategori 1',
        'Kategori 2',
        'Kategori 3',
        'Deskripsi',
        'Kuantitas Grosir 1',
        'Harga Grosir 1',
        'Kuantitas Grosir 2',
        'Harga Grosir 2',
        'Kuantitas Grosir 3',
        'Harga Grosir 3',
        'Availability',
        'URL Product',
        'Image URL 1',
        'Image URL 2',
        'Image URL 3',
        'Image URL 4',
        'Image URL 5',
    ]
    field_formatted = [
        'Timestamp',
        'Kode SKU',
        'Tempat Penjualan',
        'Nama',
        'Harga Retail',
        'Deskripsi',
        'Nama File Link Gambar 1',
        'Nama File Link Gambar 2',
        'Nama File Link Gambar 3',
        'Nama File Link Gambar 4',
        'Nama File Gambar 5',
        'Berat dalam gram',
        'Pemesanan Minimal',
        'Ketersediaan Stok',
        'Etalase',
        'Kategori Level 1',
        'Kategori Level 2',
        'Kategori Level 3',
        'Rentang Min 1',
        'Rentang Max 1',
        'Harga 1',
        'Rentang Min 2',
        'Rentang Max 2',
        'Harga 2',
        'Rentang Min 3',
        'Rentang Max 3',
        'Harga 3',
        'Rentang Min 4',
        'Rentang Max 4',
        'Harga 4',
        'Rentang Min 5',
        'Rentang Max 5',
        'Harga 5',
        'Berat dalam kg',
        'Kategori Produk',
        'Tag Produk',
        'Jumlah Stok',
        'URL Product',
        'URI Uploaded',
        'Image URL 1',
        'Image URL 2',
        'Image URL 3',
        'Image URL 4',
        'Image URL 5',
    ]
    field_raw_to_formatted = {
        'Nama Produk': ['Nama'],
        'Harga Ecer': ['Harga Retail'],
        'Minimal Pembelian': ['Pemesanan Minimal'],
        'Berat Produk': ['Berat dalam gram', 'Berat dalam kg'],
        'Asuransi': [''],
        'Kondisi Produk': [''],
        'Kategori 1': ['Kategori Level 1'],
        'Kategori 2': ['Kategori Level 2'],
        'Kategori 3': ['Kategori Level 3'],
        'Deskripsi': ['Deskripsi'],
        'Kuantitas Grosir 1': ['Rentang Min 1', 'Rentang Max 1'],
        'Harga Grosir 1': ['Harga 1'],
        'Kuantitas Grosir 2': ['Rentang Min 2', 'Rentang Max 2'],
        'Harga Grosir 2': ['Harga 2'],
        'Kuantitas Grosir 3': ['Rentang Min 3', 'Rentang Max 3'],
        'Harga Grosir 3': ['Harga 3'],
        'Availability': ['Ketersediaan Stok'],
        'URL Product': ['URL Product'],
        'Image URL 1': [''],
        'Image URL 2': [''],
        'Image URL 3': [''],
        'Image URL 4': [''],
        'Image URL 5': [''],
    }

    if type == "raw":
        return field_raw
    elif type == "formatted":
        return field_formatted
    elif type == "raw_to_formatted":
        return field_raw_to_formatted
    else:
        return None


def format_products_data(namafileinput, namafileoutput, marginminimal, etalase, human_print_flag=False):
    # function to format products data
    if etalase is None:
        etalase = 'Sale'
    # menginisasi fieldnames dari file scrap (input)
    fieldinput = field_format("raw")
    fieldoutput = field_format("formatted")
    # membuka file input dan output
    with open(namafileinput, "r") as fileinput, open(namafileoutput, "wb") as fileoutput:
        # membaca tiap baris di fileinput
        data = csv.DictReader(fileinput, fieldnames=fieldinput)
        # skip header row
        next(data, None)
        # menginisialisasi csv writer
        writer = csv.DictWriter(fileoutput, fieldnames=fieldoutput)
        # menulis header csv file output
        writer.writeheader()
        # inisialisasi counter produk
        counterproduk = 1
        # looping baris per baris
        for row in data:
            print "==============================================="
            print "Produk ke = " + str(counterproduk)
            counterproduk = counterproduk + 1
            # Melakukan formatting terhadap data baru.
            # Timestamp: ambil dari current date aja
            timestamp = time.localtime(time.time())
            timestamp = time.strftime("%b %d %Y %H:%M:%S", timestamp)
            # Skip Kode SKU.
            kodesku = ''
            # Tempat Penjualan. Default-nya
            tempatpenjualan = "Marketplace, Sosmed, dan Website"
            # Nama Produk
            namaproduk = row['Nama Produk']
            print "Nama Produk = " + namaproduk
            # pemesanan minimal
            pemesananminimal = row['Minimal Pembelian']
            try:
                pemesananminimal = int(pemesananminimal)
            except ValueError:
                pemesananminimal = 0
            # Harga Retail
            hargaretail = row['Harga Ecer']
            hargaretail = hargaretail.translate(None, '.,Rp ')
            try:
                hargaretail = int(hargaretail)
            except ValueError:
                hargaretail = 0
            print "hargaretail supplier = " + str(hargaretail) + " pemesanan minimal supplier = " + str(pemesananminimal)
            # markup harga. bagian ini untuk markup harga dari yang data tokopedia.
            if marginminimal is not None:
                hasilmarkup = markupharga(hargaretail, pemesananminimal, marginminimal)
            else:
                hasilmarkup = markupharga(hargaretail, pemesananminimal)
            print "hasil markup = ", hasilmarkup
            # versi 2.3. pemesanan minimal
            pemesananminimal = hasilmarkup['pemesananminimal']
            # versi 2.3. hargajualfix
            hargajualfix = hasilmarkup['hargajual']
            # URL Produk
            urlproduk = row['URL Product'].strip()
            print "url produk = ", urlproduk
            supplierusername = urlproduk.split('/')[3]
            # Mengambil deskripsi
            # versi 2.4. tambah pengecekan dan strip
            deskripsi = row['Deskripsi'].strip()
            # versi 2.4. remove jejak supplier
            wwwtokopedia = "https://www.tokopedia.com/"
            mtokopedia = "https://m.tokopedia.com/"
            ada_di_kami = "(Ada di Etalase Toko Kami)"
            deskripsi = deskripsi.replace(wwwtokopedia + supplierusername + "/", ada_di_kami)
            deskripsi = deskripsi.replace(wwwtokopedia + supplierusername + "/", ada_di_kami)
            deskripsi = deskripsi.replace(mtokopedia + supplierusername + "/", ada_di_kami)
            deskripsi = deskripsi.replace(mtokopedia + supplierusername + "/", ada_di_kami)
            deskripsi = deskripsi.replace(supplierusername, "Toko Kami")
            # versi 2.6. mengubah \n menjadi . \n
            deskripsi = deskripsi.replace("\n", ". \n")
            deskripsi = deskripsi.replace(". \n. \n", ". \n\n")
            # versi 2.5. batas panjang dikurangi dikit lagi.
            # biar ada space kalo ada perbedaan perhitungan
            # panjang antara tool ini dengan tokopedia
            # using while loop untuk mengulangi proses
            # sampai bisa dipastikan panjangnya kurang dari batas
            deskripsisplitted = deskripsi.split(" ")
            countdeskripsi = -1
            while len(deskripsi) >= 1980:
                deskripsi = " ".join(deskripsisplitted[:countdeskripsi])
                countdeskripsi = countdeskripsi - 1
            # Membuat nama file gambar
            namafilegambar = []
            for image_counter in range(1, 6):
                namafilegambar.append(namaproduk + "-" + str(image_counter) + ".jpg")
            # Berat dalam gram dan kg
            # versi 2.3: karakter .
            # dihilangkan agar perhitungan berat menjadi sesuai
            berat = row['Berat Produk']
            if "gr" in berat:
                berat = berat.translate(None, 'gr .')
                satuanberat = 'gr'
            elif "kg" in berat:
                berat = berat.translate(None, 'kg .')
                satuanberat = 'kg'
            else:
                berat = 0
                satuanberat = ""
            try:
                berat = float(berat)
            except ValueError:
                berat = 0
            # konversi satuan berat
            if satuanberat == 'kg':
                beratdalamkg = int(berat)
                beratdalamgr = int(float(1000) * float(berat))
            elif satuanberat == "gr":
                beratdalamkg = math.ceil(float(berat) / float(1000))
                beratdalamgr = int(berat)
            else:
                beratdalamgr = 0
                beratdalamkg = 0
            try:
                pemesananminimal = int(pemesananminimal)
            except ValueError:
                pemesananminimal = 1
            # Ketersediaan Stok.
            # Karena data baru, jadi diasumsikan semua produk ready stok
            if row['Availability'].find("Stok produk kosong") >= 0:
                ketersediaanstok = 0
            else:
                ketersediaanstok = 1
            # Kategori produk di tokopedia. Versi 2.3: tambahin strip
            kategorilevel1 = row['Kategori 1'].strip()
            kategorilevel2 = row['Kategori 2'].strip()
            kategorilevel3 = row['Kategori 3'].strip()
            # Grosir
            rentangmin = []
            rentangmax = []
            hargagrosir = []
            for counter_grosir in range(1, 4):
                kuantitasgrosir = row['Kuantitas Grosir ' + str(counter_grosir)]
                # print kuantitasgrosir
                # mengecek apakah ada tanda lebih besar / sama dengan
                if u'\u2265' in unicode(kuantitasgrosir, "utf-8"):
                    rentangmin.append(re.findall('\d+', kuantitasgrosir)[0])
                    rentangmax.append(str(int(rentangmin[counter_grosir - 1]) + 1))
                    hargagrosir.append(row['Harga Grosir ' + str(counter_grosir)].translate(None, '.,Rp '))
                # menecek apakah ada tanda "-" . data inputnya misal "2-5". jadi tanda "-" digunakan sebagai pembatas
                elif "-" in kuantitasgrosir:
                    temp_grosir = kuantitasgrosir.split('-')
                    rentangmin.append(temp_grosir[0])
                    rentangmax.append(temp_grosir[1])
                    hargagrosir.append(row['Harga Grosir ' + str(counter_grosir)].translate(None, ',.Rp '))
                # kalau di data input field grosirnya kosong
                else:
                    rentangmin.append("")
                    rentangmax.append("")
                    hargagrosir.append("")
                # menghapus spasi dari rentang minimal dan maksimal
                rentangmin[counter_grosir - 1] = rentangmin[counter_grosir - 1].translate(None, " ")
                rentangmax[counter_grosir - 1] = rentangmax[counter_grosir - 1].translate(None, " ")
                # mencoba mengubah semuanya jadi integer.
                try:
                    rentangmin[counter_grosir - 1] = int(rentangmin[counter_grosir - 1])
                    rentangmax[counter_grosir - 1] = int(rentangmax[counter_grosir - 1])
                    hargagrosir[counter_grosir - 1] = int(hargagrosir[counter_grosir - 1])
                    print "Detail Grosir Supplier = ", rentangmin[counter_grosir - 1], rentangmax[counter_grosir - 1], hargagrosir[counter_grosir - 1]
                    # Perbaikan di versi 2.3. Penghitungan markup harga grosir, rentang min dan max
                    if marginminimal is not None:
                        hasilmarkupgrosir = markupharga(int(hargagrosir[counter_grosir - 1]), rentangmin[counter_grosir - 1], marginminimal)
                    else:
                        hasilmarkupgrosir = markupharga(int(hargagrosir[counter_grosir - 1]), rentangmin[counter_grosir - 1])
                    print "Hasil markupgrosir = ", hasilmarkupgrosir
                    # versi 2.4. inisialisasi
                    # pastikan temphargagrosir dan temprentangmin kosong
                    temphargagrosir = 0
                    # mengisi nilai temporary
                    temphargagrosir = hasilmarkupgrosir['hargajual']
                    # versi 2.4. pengecekan data
                    if hargajualfix <= temphargagrosir:
                        temphargagrosir = hargajualfix - 100
                    if counter_grosir - 1 > 0:
                        if hargagrosir[counter_grosir - 2] <= temphargagrosir:
                            temphargagrosir = hargagrosir[counter_grosir - 2] - 100
                    hargagrosir[counter_grosir - 1] = temphargagrosir

                    # memastikan rentang min >=  pemesanan minimal retail hasil formatting
                    if rentangmin[counter_grosir - 1] <= pemesananminimal:
                        rentangmin[counter_grosir - 1] = pemesananminimal + 1
                    if rentangmax[counter_grosir - 1] <= rentangmin[counter_grosir - 1]:
                        rentangmax[counter_grosir - 1] = rentangmin[counter_grosir - 1] + 1
                    # memastikan rentang min dan max satu dan lainnya tidak saling tumpang tindih
                    if counter_grosir - 1 > 0:
                        if rentangmin[counter_grosir - 1] <= rentangmax[counter_grosir - 2]:
                            rentangmin[counter_grosir - 1] = rentangmax[counter_grosir - 2] + 1
                        if rentangmin[counter_grosir - 1] - rentangmax[counter_grosir - 2] != 1:
                            rentangmin[counter_grosir - 1] = rentangmax[counter_grosir - 2] + 1
                # kalau gak bisa diubah jadi integer. nilainya di nol kan saja
                except ValueError:
                    rentangmin[counter_grosir - 1] = ""
                    rentangmax[counter_grosir - 1] = ""
                    hargagrosir[counter_grosir - 1] = ""

            # Tambahan di versi 2.3. Pengecekan nilai grosir
            # nanti ya.

            # Berat dalam kg. Lihat kode di atas.
            # Sudah dihitung bersamaan dengan berat dalam gram
            beratdalamkg = beratdalamkg
            # Kategori Produk
            kategoriproduk = ""
            # Tag Produk
            tagproduk = ""
            # Jumlah Stok.
            if row['Availability'].find("Stok produk kosong") >= 0:
                jumlahstok = 0
            else:
                jumlahstok = 1000
            # Final step. Cek panjang nama produk.
            # tidak boleh lebih dari 70 karakter. (versi 2.3)
            newnamaproduk = namaproduk
            if len(newnamaproduk) >= 70:
                while len(newnamaproduk) >= 70:
                    newnamaproduk = newnamaproduk.split(" ")
                    newnamaproduk = " ".join(newnamaproduk[:-1])
            # versi 2.5: mengenerate URI Produk yang akan di-upload
            uriuploaded = genuri(newnamaproduk)
            # final step. kita cek apakah referensi produk di supplier
            # pernah di-upload berulang sehingga menghasilkan "numbered" URI.
            # misal: "eve-magic-bra-1" padahal normalnya "eve-magic-bra" saja
            # mengambil part terakhir dari url produk di toko supplier
            lastparturlproduk = urlproduk.strip().split("-")[-1]
            # inisialisasi flag
            indexed = False
            # coba convert menjadi angka
            try:
                # ternyata url supplier diakhiri dengan angka
                lastparturlproduk = int(lastparturlproduk)
                # kalo ternyata URL dari supplier diakhiri dengan integer,
                # maka sekarang cek apakah integer tersebut merupakan
                # bagian dari nama produk atau bukan
                uriproductsupplier = genuri(namaproduk)
                try:
                    lastparturisupplier = int(uriproductsupplier.strip().split("-")[-1])
                    if lastparturisupplier == lastparturlproduk:
                        indexed = False
                        # cek level 2 nya
                        lastparturlproduk = urlproduk.strip().split("-")[-2]
                        try:
                            lastparturlproduk = int(lastparturlproduk)
                            indexed = True
                        except ValueError:
                            pass
                    else:
                        indexed = True
                except ValueError:
                    indexed = True
            except ValueError:
                pass
            if indexed:
                indexpadaurlsupplier = lastparturlproduk
                uriuploaded = uriuploaded + "-" + str(indexpadaurlsupplier)
            # get image urls
            imageurl = []
            for k in range(1, 6):
                imageurl.append(row['Image URL ' + str(k)].strip())
            # menulis hasil pengeloahan ke file csv
            # if counterproduk != 1:
            writer.writerow({
                fieldoutput[0]: timestamp,
                fieldoutput[1]: kodesku,
                fieldoutput[2]: tempatpenjualan,
                fieldoutput[3]: newnamaproduk,
                fieldoutput[4]: hargajualfix,
                fieldoutput[5]: deskripsi,
                fieldoutput[6]: namafilegambar[0],
                fieldoutput[7]: namafilegambar[1],
                fieldoutput[8]: namafilegambar[2],
                fieldoutput[9]: namafilegambar[3],
                fieldoutput[10]: namafilegambar[4],
                fieldoutput[11]: beratdalamgr,
                fieldoutput[12]: pemesananminimal,
                fieldoutput[13]: ketersediaanstok,
                fieldoutput[14]: etalase,
                fieldoutput[15]: kategorilevel1,
                fieldoutput[16]: kategorilevel2,
                fieldoutput[17]: kategorilevel3,
                fieldoutput[18]: rentangmin[0],
                fieldoutput[19]: rentangmax[0],
                fieldoutput[20]: hargagrosir[0],
                fieldoutput[21]: rentangmin[1],
                fieldoutput[22]: rentangmax[1],
                fieldoutput[23]: hargagrosir[1],
                fieldoutput[24]: rentangmin[2],
                fieldoutput[25]: rentangmax[2],
                fieldoutput[26]: hargagrosir[2],
                fieldoutput[33]: beratdalamkg,
                fieldoutput[34]: kategoriproduk,
                fieldoutput[35]: tagproduk,
                fieldoutput[36]: jumlahstok,
                fieldoutput[37]: urlproduk,
                fieldoutput[38]: uriuploaded,
                fieldoutput[39]: imageurl[0],
                fieldoutput[40]: imageurl[1],
                fieldoutput[41]: imageurl[2],
                fieldoutput[42]: imageurl[3],
                fieldoutput[43]: imageurl[4],
            })
            # update counter
            print "\n"
    # create human-read-friendly file
    if human_print_flag is not False:
        human_print(human_print_flag, namafileoutput)
    return


def human_print(log_file_name, data_file_name):
    print "==============="
    print "Now creating human-read-friendly output file"
    print "Notes: Only updated and error products in will be written to file"
    print "Notes: Products with no data changed status will be printed to terminal"
    print "==============="
    # product columns initialization
    # Nama Produk = product name, Harga Ecer = retail price,
    # Minimal Pembelian = min. purchase quantity,
    # Berat Produk = product weight, Asuransi = insurance,
    # Kondisi Product = Product condition, Kategori = category,
    # Deskripsi = description, Kuantitas Grosir = wholesale quantity,
    # Harga Grosir = wholesale price
    field_input = field_format("formatted")
    field_print = field_format("raw_to_formatted")
    # open input file (url of products file)
    print "create output file name"
    output_file_name = data_file_name.split(".")
    output_file_name = ".".join(output_file_name[:-1]) + "-readable.txt"
    with open(data_file_name, "r") as file_data,\
            open(output_file_name, "wb") as file_output,\
            open(log_file_name, "r") as file_log:
        # membaca tiap baris di fileinput
        products_data = csv.DictReader(file_data, fieldnames=field_input)
        # skip header row
        next(products_data, None)
        # baca file log yang akan digunakan sebagai filter
        log_data = []
        # save updated products url in url_list
        url_list = []
        # save product url in a new list
        for log in file_log.readlines():
            if log:
                log_data.append([x.strip() for x in log.strip().split('#')])
                url_list.append(log_data[-1][1].strip())
        # pprint.pprint(log_data)
        # pprint.pprint(url_list)
        # loop through products_data
        for row in products_data:
            # initialise human-read-friendly variable to be written
            human_read_string = ""
            # check in comparation log whether
            # products has been changed or an error occured.
            urlproduk = row['URL Product'].split("/")[-1]
            if any(urlproduk in ssss for ssss in log_data):
                # get index of urlproduct in url_list
                index_url = url_list.index(urlproduk)
                # get length of log_data[index_url]
                log_data_len = len(log_data[index_url])
                # if log_data len > 5: product updated
                # or no change in product data
                if log_data_len >= 4:
                    # check if there is any changes in product data
                    if "Data produk Tetap" not in log_data[index_url]:
                        human_read_string = human_read_string + "*******************************\r\n"
                        human_read_string = human_read_string + "*******************************\r\n"
                        human_read_string = human_read_string + "Updated product = " + str(log_data[index_url][1]) + "\r\n"
                        human_read_string = human_read_string + "Product availability = " + str(log_data[index_url][2]) + "\r\n"
                        human_read_string = human_read_string + "Update(s):\r\n"
                        for x in range(3, log_data_len):
                            updated_details = str(log_data[index_url][x])
                            if updated_details:
                                detail_list = field_print[log_data[index_url][x]]
                                human_read_string = human_read_string + "\r\n==> " + str(updated_details) + "\r\n"
                                # pprint.pprint(detail_list)
                                for detail in detail_list:
                                    if detail:
                                        detail_content = str(row[detail]).replace("\n", "\r\n")
                                        human_read_string = human_read_string + detail + " = " + detail_content + "\r\n"
                        print human_read_string
                        file_output.write(human_read_string)
                    else:
                        print "*******************************"
                        print "*******************************"
                        print "Updated product = ", log_data[index_url][1]
                        print "Data Produk Tetap"
                elif log_data_len == 4:
                    human_read_string = human_read_string + "*******************************\r\n"
                    human_read_string = human_read_string + "*******************************\r\n"
                    human_read_string = human_read_string + "Product = " + str(log_data[index_url][1]) + "\r\n"
                    human_read_string = human_read_string + "Error, please check if this product is still exists\r\n"
                    print human_read_string
                    file_output.write(human_read_string)
                else:
                    human_read_string = human_read_string + "*******************************\r\n"
                    human_read_string = human_read_string + "*******************************\r\n"
                    human_read_string = human_read_string + "Product = " + str(log_data[index_url][1]) + "\r\n"
                    human_read_string = human_read_string + "Error, length of data not valid\r\n"
                    print human_read_string
                    file_output.write(human_read_string)
    return


def print_users_arguments(usersarguments):
    # pretty print users arguments
    pprint.pprint(usersarguments)
    return


def main():
    # start time
    starttime = time.time()
    # print status
    print "================"
    print "Parsing Argumets/Settings"
    # versi 2.4: Parsing argument
    argumendariuser = parsingarguments()
    # print user's arguments
    print_users_arguments(argumendariuser)
    # mengambil nama file sebagai inputan
    namafileinput = argumendariuser['input']
    # Mengambil nama file output
    namafileoutput = argumendariuser['output']
    # Mengambil margin minimal yang diinginkan user
    marginminimal = argumendariuser['minmargin']
    # mengambil nama etalase tujuan
    etalase = argumendariuser['etalase']
    # mengambil nama file log sebagai input human-read-friendly-print
    humanprint = argumendariuser['humanprint']
    # mengecek apakah humanprint ada isi nya
    if humanprint is None:
        humanprint = False
    else:
        # mengecek apakah file log exist
        if os.path.isfile(humanprint) is False:
            print "======================================================"
            print "Running program without printing human-readable result"
            print "======================================================"
            humanprint = False
    if etalase is None:
        etalase = 'Sale'
    # Run main function
    format_products_data(namafileinput, namafileoutput, marginminimal, etalase, humanprint)
    # print total execution time
    print "================"
    print("Completed in --- %s seconds ---" % (time.time() - starttime))
    print "================"
    # exiting
    return


if __name__ == "__main__":
    main()
    sys.exit()
