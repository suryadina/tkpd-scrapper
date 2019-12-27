'''
FILTER PRODUK DARI MASTER DATA
Versi 1.1 created 1 Nopember 2016 by Ardya

Log Update:
versi 1.0: initial release 29 September 2016 by Ardya
versi 1.1: penambahan argumen parsing. 1 Nopember 2016 by Ardya

Pre-requirements:
01. Pengguna menyediakan file data produk yang sudah diformat (yang merupakan output dari tool "tokopedia-product-data-formatter.py").
02. Pengguna menyediakan file yang berisi daftar url tokopedia dari produk yang akan di FILTER

Input Argument:
01. File data produk (yang merupakan output dari tool "tokopedia-product-data-formatter") 
02. Nama file output (data produk "baru")  yang diinginkan
03. File yang berisi daftar url tokopedia dari produk yang akan di FILTER

Output Program:
01. File data produk yang dipilih (di-filter)

Notes:
01. After run this script, please inspect the results manually
'''

#import module
import os, sys, re, urllib2, time, random, csv, urllib, argparse, math, socket, ssl, string, argparse
#import maketrans
from string import maketrans


def parsingarguments():
    #versi tool
    version = " version 1.1 . 1 Nopember 2016 \n created by ardya suryadinata"
    #membuat parser dan deskripsi tool
    parser = argparse.ArgumentParser(description="TOKOPEDIA PRODUCT DATA FILTERER" + "\n" + version)
    #opsi untuk menampilkan versi
    parser.add_argument("--version", help="print version", action="store_true")
    #opsi untuk meminta inputan file input
    parser.add_argument("--input", help="Masukkan nama file sumber yang akan di-filter (formatted-data file)")
    #opsi untuk meminta inputan file output
    parser.add_argument("--output", help="Masukkan nama output file hasil filter")
    #opsi untuk meminta daftar url produk
    parser.add_argument("--targeturl", help="Masukkan nama file yang berisi daftar url produk yang akan di filter")
    #melakukan parsing arguments
    args = parser.parse_args()
    #melakukan validasi dan tindak lanjut dari argument yang berhasil diparsing
    if args.version:
        print sys.argv[0].split("\\")[-1] + " " + version
    if args.input == None:
        parser.error("Nama file input belum dimasukkan (--input required)")
    if args.output == None:
        parser.error("Nama file output belum dimasukkan (--output required)")
    if args.targeturl == None:
        parser.error("Nama file daftar url produk belum dimasukkan (--targeturl required)")
    #menyimpan argumen dari user
    argumendariuser = {'input':args.input, 'output':args.output, 'targeturl':args.targeturl}
    return argumendariuser

#get arguments from user
argumendariuser = parsingarguments()
#file data lama
namafilesumberdata = argumendariuser['input']
#output: data file baru
namafilefilteredproduk = argumendariuser['output']
#file daftar url produk yang akan difilter
namafiledaftarurl = argumendariuser['targeturl']

#product columns initialization
#Nama Produk = product name, Harga Ecer = retail price, Minimal Pembelian = min. purchase quantity, Berat Produk = product weight, Asuransi = insurance, Kondisi Product = Product condition, Kategori = category, Deskripsi = description, Kuantitas Grosir = wholesale quantity, Harga Grosir = wholesale price
fieldoutput = ['Timestamp', 'Kode SKU', 'Tempat Penjualan', 'Nama', 'Harga Retail', 'Deskripsi', 'Nama File Link Gambar 1', 'Nama File Link Gambar 2', 'Nama File Link Gambar 3', 'Nama File Link Gambar 4', 'Nama File Gambar 5',  'Berat dalam gram', 'Pemesanan Minimal', 'Ketersediaan Stok', 'Etalase', 'Kategori Level 1', 'Kategori Level 2', 'Kategori Level 3', 'Rentang Min 1', 'Rentang Max 1',  'Harga 1',  'Rentang Min 2', 'Rentang Max 2', 'Harga 2', 'Rentang Min 3', 'Rentang Max 3', 'Harga 3', 'Rentang Min 4',  'Rentang Max 4', 'Harga 4', 'Rentang Min 5', 'Rentang Max 5', 'Harga 5', 'Berat dalam kg', 'Kategori Produk', 'Tag Produk', 'Jumlah Stok', 'URL Product', 'URI Uploaded']
#open input file (url of products file)
with open(namafilesumberdata, "r") as filesumberdata, open(namafilefilteredproduk, "wb") as filefilteredproduk, open(namafiledaftarurl, "r") as filedaftarurl:
    #membaca tiap baris di fileinput
    data = csv.DictReader(filesumberdata, fieldnames=fieldoutput)
    #skip header row
    next(data, None)
    #csv writer initialization
    writerfiltereddata = csv.DictWriter(filefilteredproduk, fieldnames=fieldoutput)
    #write the csv file header
    writerfiltereddata.writeheader()
    #product counter
    counter_produk = 1
    #baca url yang akan digunakan sebagai filter
    daftarurl = filedaftarurl.read()
    #take url from file. one url per-line
    for row in data:   
        #print some status
        print "======================================================="
        print "Produk ke = " + str(counter_produk)
        #get url of product - url in this tool is used as unique value as urls in tokopedia are set permanently for every unique product
        urlproduk = row['URL Product']
        #cek apakah termasuk data yang difilter
        if urlproduk in daftarurl:
            print "URL PRODUK = " + urlproduk + "Filtered"
            #write allproduct data
            writerfiltereddata.writerow({fieldoutput[0]:row['Timestamp'], fieldoutput[1]:row['Kode SKU'], fieldoutput[2]:row['Tempat Penjualan'], fieldoutput[3]:row['Nama'], fieldoutput[4]:row['Harga Retail'], fieldoutput[5]:row['Deskripsi'], fieldoutput[6]:row['Nama File Link Gambar 1'], fieldoutput[7]:row['Nama File Link Gambar 2'], fieldoutput[8]:row['Nama File Link Gambar 3'], fieldoutput[9]:row['Nama File Link Gambar 4'], fieldoutput[10]:row['Nama File Gambar 5'], fieldoutput[11]:row['Berat dalam gram'], fieldoutput[12]:row['Pemesanan Minimal'], fieldoutput[13]:row['Ketersediaan Stok'], fieldoutput[14]:row['Etalase'], fieldoutput[15]:row['Kategori Level 1'], fieldoutput[16]:row['Kategori Level 2'], fieldoutput[17]:row['Kategori Level 3'], fieldoutput[18]:row['Rentang Min 1'], fieldoutput[19]:row['Rentang Max 1'], fieldoutput[20]:row['Harga 1'], fieldoutput[21]:row['Rentang Min 2'], fieldoutput[22]:row['Rentang Max 2'], fieldoutput[23]:row['Harga 2'], fieldoutput[24]:row['Rentang Min 3'], fieldoutput[25]:row['Rentang Max 3'], fieldoutput[26]:row['Harga 3'], fieldoutput[27]:row['Rentang Min 4'], fieldoutput[28]:row['Rentang Max 4'], fieldoutput[29]:row['Harga 4'], fieldoutput[30]:row['Rentang Min 5'], fieldoutput[31]:row['Rentang Max 5'], fieldoutput[32]:row['Harga 5'], fieldoutput[33]:row['Berat dalam kg'], fieldoutput[34]:row['Kategori Produk'], fieldoutput[35]:row['Tag Produk'], fieldoutput[36]:row['Jumlah Stok'], fieldoutput[37]:row['URL Product'], fieldoutput[38]:row['URI Uploaded']})
        #print the product counter into terminal
        counter_produk = counter_produk + 1
