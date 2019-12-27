'''
SCRAP TOKOPEDIA.COM PRODUCTS
Version history
1.0 released on 8 July 2016 by Ardya
1.1 released on 26 August 2016 by Ardya
1.2 released on 27 August 2016 by Ardya
1.3 released on 1 Nopember 2016 by Ardya
1.4 released on 12 August 2017 by Ardya
1.4.1 released on 31 August 2017 by Ardya

Updates log:
version 1.1
    => add column in output file to indicate whether the procuct is ready stock or not
    => add "mode" as argv[4] to decide if the products images will be downloaded (mode = 1) or not (mode = any other value)
    => add column in output file that record the product source URL
version 1.2
    => move data scraping process into function and create tokopedia_tools_library_1_0
version 1.3
    => use tokopedia_tools_library_1_2
    => add argument parsing
version 1.4
    => changes in script description
    => script now comply PEP8
    => use tokopedia_tools_library_1_3
    => unused imports removed
    => add image urls
version 1.4.1
	=> fix bug when printing image url

Pre-requirements:
01. User must provide a file consisting products url (one url per-line)

Input Argument:
01. URL of products file
02. Ouput Data File (where the scrape results stored)
03. Target directory to save product's images
04. mode. 1 untuk download gambar. nilai lain untuk gak download

Notes:
01. After run this script, please inspect the results manually

External Module:
01. https://github.com/python-pillow/Pillow/blob/master/docs/installation.rst
02. BeautifulSoup
03. https://pypi.python.org/pypi/fake-useragent

'''
# import module
import os
import sys
import time
import random
import csv
import argparse
import socket
# import custom library
from tokopedia_tools_library_1_3_1 import tokopediaproductscrapper


def parsingarguments():
    # versi tool
    version = " version 1.4 - Released on 12 August 2017 \n by ardya suryadinata"
    # membuat parser dan deskripsi tool
    parser = argparse.ArgumentParser(description="TOKOPEDIA DATA SCRAPPER" + "\n" + version)
    # opsi untuk menampilkan versi
    parser.add_argument("--version", help="print version", action="store_true")
    # opsi untuk meminta inputan file input yang akan di format
    parser.add_argument("--input", help="Masukkan nama input file berisi daftar url yang di-scrape")
    # opsi untuk meminta inputan file input yang akan di format
    parser.add_argument("--output", help="Masukkan nama output file hasil scrape")
    # opsi untuk minimal profit hasil markup
    parser.add_argument("--imagedir", help="Masukkan nama folder tempat gambar akan disimpan. Jika tidak di-set maka gambar tidak di-download")
    # melakukan parsing arguments
    args = parser.parse_args()
    # melakukan validasi dan tindak lanjut dari argument yang berhasil diparsing
    if args.version:
        print sys.argv[0].split("\\")[-1] + " " + version
    if args.input is None:
        parser.error("Input file belum dimasukkan (--input required)")
    if args.output is None:
        parser.error("Nama file output belum dimasukkan (--output required)")
    if args.imagedir is not None:
        setmode = 1
    else:
        setmode = 0
    # menyimpan argumen dari user
    argumendariuser = {
        'input': args.input,
        'output': args.output,
        'imagedir': args.imagedir,
        'mode': setmode
    }
    return argumendariuser


def main():
    # get arguments from user
    argumendariuser = parsingarguments()
    # file consisting products url
    namafileurl = argumendariuser['input']
    # output file whare the scrape data stored
    namafiledataproduk = argumendariuser['output']
    # target directory where the images of products stored
    namafoldergambarproduk = argumendariuser['imagedir']
    # if this argument is set = 1. then download the product images. otherwise. skip
    mode = str(argumendariuser['mode'])
    print "mode = " + mode

    # product columns initialization
    # Nama Produk = product name, Harga Ecer = retail price, Minimal Pembelian = min. purchase quantity,
    # Berat Produk = product weight, Asuransi = insurance, Kondisi Product = Product condition,
    # Kategori = category, Deskripsi = description, Kuantitas Grosir = wholesale quantity, Harga Grosir = wholesale price
    fieldproduk = [
        'Nama Produk',
        'Harga Ecer',
        'Minimal Pembelian',
        'Berat Produk', 'Asuransi',
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

    # set global timeout setting
    socket.setdefaulttimeout(30)

    # check if target directori (namafoldergambarproduk) exists. if not, then create new folder
    if namafoldergambarproduk:
        if not os.path.exists(namafoldergambarproduk):
            os.makedirs(namafoldergambarproduk)

    # open input file (url of products file)
    with open(namafileurl) as fileurlproduk:
        with open(namafiledataproduk, "wb") as filedataproduk:
            # csv writer initialization
            writer = csv.DictWriter(filedataproduk, fieldnames=fieldproduk)
            # write the csv file header
            writer.writeheader()
            # product counter
            counter_produk = 1
            # take url from file. one url per-line
            for urlproduk in fileurlproduk:
                # print some status
                print "======================================================="
                print "Produk ke = " + str(counter_produk)
                print "\n"
                # scrape product data
                scrapeproduct = tokopediaproductscrapper(urlproduk, mode, namafoldergambarproduk)
                # write the result as csv file if scrape product data successfull
                if scrapeproduct is not False:
                    writer.writerow({
                        fieldproduk[0]: scrapeproduct['Nama Produk'],
                        fieldproduk[1]: scrapeproduct['Harga Ecer'],
                        fieldproduk[2]: scrapeproduct['Minimal Pembelian'],
                        fieldproduk[3]: scrapeproduct['Berat Produk'],
                        fieldproduk[4]: scrapeproduct['Asuransi'],
                        fieldproduk[5]: scrapeproduct['Kondisi Produk'],
                        fieldproduk[6]: scrapeproduct['Kategori 1'],
                        fieldproduk[7]: scrapeproduct['Kategori 2'],
                        fieldproduk[8]: scrapeproduct['Kategori 3'],
                        fieldproduk[9]: scrapeproduct['Deskripsi'],
                        fieldproduk[10]: scrapeproduct['Kuantitas Grosir 1'],
                        fieldproduk[11]: scrapeproduct['Harga Grosir 1'],
                        fieldproduk[12]: scrapeproduct['Kuantitas Grosir 2'],
                        fieldproduk[13]: scrapeproduct['Harga Grosir 2'],
                        fieldproduk[14]: scrapeproduct['Kuantitas Grosir 3'],
                        fieldproduk[15]: scrapeproduct['Harga Grosir 3'],
                        fieldproduk[16]: scrapeproduct['Availability'],
                        fieldproduk[17]: scrapeproduct['URL Product'],
                        fieldproduk[18]: scrapeproduct['Image URL 1'],
                        fieldproduk[19]: scrapeproduct['Image URL 2'],
                        fieldproduk[20]: scrapeproduct['Image URL 3'],
                        fieldproduk[21]: scrapeproduct['Image URL 4'],
                        fieldproduk[22]: scrapeproduct['Image URL 5'],
                    })
                # print the product counter into terminal
                print "Selesai Produk ke = " + str(counter_produk)
                print "=======================================================\n"
                counter_produk = counter_produk + 1
                # give some short delay before scraping next product
                time.sleep(random.randrange(4, 9))
            return


if __name__ == "__main__":
    main()
    sys.exit()
