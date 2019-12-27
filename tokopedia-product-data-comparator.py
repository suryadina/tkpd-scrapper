# import module
import sys
import time
import random
import csv
import argparse
import ConfigParser
import pprint
# import custom library
from tokopedia_tools_library_1_3_1 import tokopediaproductscrapper


def print_users_arguments(usersarguments):
    # pretty print users arguments
    pprint.pprint(usersarguments)


def parsing_arguments():
    # versi tool
    version = " version 2.7 - 31 August 2017\n by ardya suryadinata"
    # membuat parser dan deskripsi tool
    parser = argparse.ArgumentParser(description="TOKOPEDIA PRODUCT DATA COMPARATOR" + "\n" + version)
    # opsi untuk menampilkan versi
    parser.add_argument("--version", help="print version", action="store_true")
    # opsi untuk meminta inputan file input
    parser.add_argument("--input", help="Masukkan nama file data lama (raw/unformatted) yang akan dibandingkan dengan data di supplier (REQUIRED)")
    parser.add_argument("--output", help="Masukkan nama output file hasil perbandingan (REQUIRED)")
    parser.add_argument("--configfile", help="use config file to set arguments")
    # melakukan parsing arguments
    args = parser.parse_args()
    # melakukan validasi dan tindak lanjut dari argument yang berhasil diparsing
    if args.version:
        print sys.argv[0].split("\\")[-1] + " " + version
        sys.exit()
    # check if configfile will be used
    if args.configfile:
        config_values = parse_config_file(args.configfile)
        argumendariuser = {
            'input': config_values['settings']['input'],
            'output': config_values['settings']['output'],
        }
        return argumendariuser
    elif args.input is None:
        parser.error("Nama file input belum dimasukkan (--input required)")
    elif args.output is None:
        parser.error("Nama file output belum dimasukkan (--output required)")
    else:
        # menyimpan argumen dari user
        argumendariuser = {'input': args.input, 'output': args.output}
        return argumendariuser


def parse_config_file(config_file):
    config = ConfigParser.ConfigParser()
    try:
        config.read(config_file)
        section_list = config.sections()
    except IOError:
        print "Reading config file failed. Exiting program"
        sys.exit(1)
    except ConfigParser.ERROR:
        print "Failed to get section list. Exiting program"
        sys.exit(1)
    print "Reading Config = ", section_list
    # get option value
    config_values = {}
    # if section list is not empty
    if section_list:
        for section in section_list:
            dict1 = {}
            options = config.options(section)
            for option in options:
                try:
                    dict1[option] = config.get(section, option)
                    if dict1[option] == -1:
                        print("skip: %s" % option)
                except ConfigParser.Error:
                    print("exception on %s!" % option)
                    dict1[option] = None
            config_values[section] = dict1
        return config_values
    else:
        print "Error. Cannot find any section. Config file is not valid"
        sys.exit(1)


def compare_products_data(namafiledatalama, namafileallproductbaru):
    # check values of namafiledatalama and namafileallproductbaru
    if not namafiledatalama or not namafileallproductbaru:
        print "Input file or output file name cannot be empty. Exiting program"
        sys.exit(1)
    # membuat nama nama file output
    namatemporary = namafileallproductbaru.split('.')
    if len(namatemporary) > 1:
        namafiledatabaru = '.'.join(namatemporary[:-1]) + "-updated." + namatemporary[-1]
    elif len(namatemporary) == 1:
        namafiledatabaru = namatemporary + "-updated.csv"

    # membuat nama file log
    namafilelog = '.'.join(namatemporary[:-1]) + "-komparasi.log"

    # product columns initialization
    # Nama Produk = product name, Harga Ecer = retail price,
    # Minimal Pembelian = min. purchase quantity,
    # Berat Produk = product weight,
    # Asuransi = insurance, Kondisi Product = Product condition,
    # Kategori = category,
    # Deskripsi = description, Kuantitas Grosir = wholesale quantity,
    # Harga Grosir = wholesale price
    fieldproduk = [
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
    # open input file (url of products file)
    with open(namafiledatalama) as filedatalama, \
            open(namafileallproductbaru, "wb") as fileallproductbaru,\
            open(namafiledatabaru, "wb") as filedatabaru,\
            open(namafilelog, "wb") as filelog:
        # membaca tiap baris di fileinput
        data = csv.DictReader(filedatalama, fieldnames=fieldproduk)
        # skip header row
        next(data, None)
        # csv writer initialization
        writernewdata = csv.DictWriter(filedatabaru, fieldnames=fieldproduk)
        writerallproductdata = csv.DictWriter(fileallproductbaru, fieldnames=fieldproduk)
        # write the csv file header
        writernewdata.writeheader()
        writerallproductdata.writeheader()
        # product counter
        counter_produk = 1
        # take url from file. one url per-line
        for row in data:
            # print some status
            print "======================================================="
            print "Produk ke = " + str(counter_produk)
            print "\n"
            # get url of product - url in this tool is used as unique value as urls in tokopedia are set permanently
            # for every unique product
            urlproduk = row['URL Product']
            print "URL PRODUK = " + urlproduk
            # log string
            stringlog = str(counter_produk) + "#"
            stringlog = stringlog + urlproduk.strip().split("/")[4] + "#"
            # flag perubahan data
            flagperubahan = False
            # scrape product data
            scrapeproduct = tokopediaproductscrapper(urlproduk, 0, "")
            if scrapeproduct is False:
                flagperubahan = True
                stringlog = stringlog + "ERROR#\n"
                writerallproductdata.writerow({
                    fieldproduk[0]: row['Nama Produk'],
                    fieldproduk[1]: row['Harga Ecer'],
                    fieldproduk[2]: row['Minimal Pembelian'],
                    fieldproduk[3]: row['Berat Produk'],
                    fieldproduk[4]: row['Asuransi'],
                    fieldproduk[5]: row['Kondisi Produk'],
                    fieldproduk[6]: row['Kategori 1'],
                    fieldproduk[7]: row['Kategori 2'],
                    fieldproduk[8]: row['Kategori 3'],
                    fieldproduk[9]: row['Deskripsi'],
                    fieldproduk[10]: row['Kuantitas Grosir 1'],
                    fieldproduk[11]: row['Harga Grosir 1'],
                    fieldproduk[12]: row['Kuantitas Grosir 2'],
                    fieldproduk[13]: row['Harga Grosir 2'],
                    fieldproduk[14]: row['Kuantitas Grosir 3'],
                    fieldproduk[15]: row['Harga Grosir 3'],
                    fieldproduk[16]: row['Availability'],
                    fieldproduk[17]: row['URL Product'],
                    fieldproduk[18]: row['Image URL 1'],
                    fieldproduk[19]: row['Image URL 2'],
                    fieldproduk[20]: row['Image URL 3'],
                    fieldproduk[21]: row['Image URL 4'],
                    fieldproduk[22]: row['Image URL 5'],
                })
                filelog.write(stringlog)
            elif scrapeproduct is not False:
                # Proses Komparasi Data
                if scrapeproduct['Availability'].find("Stok produk kosong") >= 0:
                    stringlog = stringlog + "Out of stock#"
                else:
                    stringlog = stringlog + "In Stock#"
                if scrapeproduct['Nama Produk'] != row['Nama Produk']:
                    flagperubahan = True
                    stringlog = stringlog + "Nama Produk#"
                if scrapeproduct['Harga Ecer'] != row['Harga Ecer']:
                    flagperubahan = True
                    stringlog = stringlog + "Harga Ecer#"
                if scrapeproduct['Minimal Pembelian'] != row['Minimal Pembelian']:
                    flagperubahan = True
                    stringlog = stringlog + "Minimal Pembelian#"
                if scrapeproduct['Berat Produk'] != row['Berat Produk']:
                    flagperubahan = True
                    stringlog = stringlog + "Berat Produk#"
                if scrapeproduct['Asuransi'] != row['Asuransi']:
                    flagperubahan = True
                    stringlog = stringlog + "Asuransi#"
                if scrapeproduct['Kondisi Produk'] != row['Kondisi Produk']:
                    flagperubahan = True
                    stringlog = stringlog + "Kondisi Produk#"
                if scrapeproduct['Kategori 1'] != row['Kategori 1']:
                    flagperubahan = True
                    stringlog = stringlog + "Kategori 1#"
                if scrapeproduct['Kategori 2'] != row['Kategori 2']:
                    flagperubahan = True
                    stringlog = stringlog + "Kategori 2#"
                if scrapeproduct['Kategori 3'] != row['Kategori 3']:
                    flagperubahan = True
                    stringlog = stringlog + "Kategori 3#"
                if scrapeproduct['Deskripsi'] != row['Deskripsi']:
                    flagperubahan = True
                    stringlog = stringlog + "Deskripsi#"
                if scrapeproduct['Kuantitas Grosir 1'] != row['Kuantitas Grosir 1']:
                    flagperubahan = True
                    stringlog = stringlog + "Kuantitas Grosir 1#"
                if scrapeproduct['Kuantitas Grosir 2'] != row['Kuantitas Grosir 2']:
                    flagperubahan = True
                    stringlog = stringlog + "Kuantitas Grosir 2#"
                if scrapeproduct['Kuantitas Grosir 3'] != row['Kuantitas Grosir 3']:
                    flagperubahan = True
                    stringlog = stringlog + "Kuantitas Grosir 3#"
                if scrapeproduct['Harga Grosir 1'] != row['Harga Grosir 1']:
                    flagperubahan = True
                    stringlog = stringlog + "Harga Grosir 1#"
                if scrapeproduct['Harga Grosir 2'] != row['Harga Grosir 2']:
                    flagperubahan = True
                    stringlog = stringlog + "Harga Grosir 2#"
                if scrapeproduct['Harga Grosir 3'] != row['Harga Grosir 3']:
                    flagperubahan = True
                    stringlog = stringlog + "Harga Grosir 3#"
                if scrapeproduct['Availability'] != row['Availability']:
                    flagperubahan = True
                    stringlog = stringlog + "Availability#"
                if scrapeproduct['Image URL 1'] != row['Image URL 1']:
                    flagperubahan = True
                    stringlog = stringlog + "Image URL 1#"
                if scrapeproduct['Image URL 2'] != row['Image URL 2']:
                    flagperubahan = True
                    stringlog = stringlog + "Image URL 2#"
                if scrapeproduct['Image URL 3'] != row['Image URL 3']:
                    flagperubahan = True
                    stringlog = stringlog + "Image URL 3#"
                if scrapeproduct['Image URL 4'] != row['Image URL 4']:
                    flagperubahan = True
                    stringlog = stringlog + "Image URL 4#"
                if scrapeproduct['Image URL 5'] != row['Image URL 5']:
                    flagperubahan = True
                    stringlog = stringlog + "Image URL 5#"
                # write allproduct data
                writerallproductdata.writerow({
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
                # write new data
                if flagperubahan is True:
                    writernewdata.writerow({
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
                else:
                    stringlog = stringlog + "Data produk Tetap#"
                # membuat pembatas log
                stringlog = stringlog + "\n"
                # menulis log
                filelog.write(stringlog)
                # write the log file now
                filelog.flush()
            # print the product counter into terminal
            print "Selesai Produk ke = " + str(counter_produk)
            print "=======================================================\n"
            counter_produk = counter_produk + 1
            # give some short delay before scraping next product
            time.sleep(random.randrange(4, 9))

    return True


def main():
    # start time
    starttime = time.time()
    # print status
    print "================"
    print "Parsing Argumets/Settings"
    # get arguments from user
    usersarguments = parsing_arguments()
    input_file = usersarguments['input']
    output_file = usersarguments['output']
    # print user's arguments
    print_users_arguments(usersarguments)
    # Run main function
    compare_products_data(input_file, output_file)
    # print total execution time
    print("Completed in --- %s seconds ---" % (time.time() - starttime))
    print "================"
    # exiting
    return


if __name__ == "__main__":
    main()
    sys.exit()
