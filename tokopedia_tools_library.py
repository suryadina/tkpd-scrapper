'''
LIBRARY TOOL TOKOPEDIA
Versi 1.3.1 created 13 September 2017 by Ardya

Log Update:
version 1.1   :
    - perbaikan di fungsi downloadproductimage untuk menghindari error
      karena gagal save dan menambah kualitas image
version 1.2   :
    - perbaiki perubahan di bagian ambil data berat. versi sebelumnya
      gak bisa jalan lagi.
version 1.3.1 :
    - mengambil url gambar dari tokopedia. menyimpan url gambar
      sebagai output
    - memperbaiki pengambilan nilai nilai yang sudah tidak sesuai
      dengan format tokopedia
    - add retry functionality when opening product url
    - fix bug when user giving image-directory without "\" or "/"
      at the end of the image-directory name
    - now using eventlet to set timeout when downloading images
    - use signal when running on linux. only use eventlet on windows

Description:
Kumpulan fungsi fungsi tool tokopedia. dibutuhkan oleh tool lainnya
External Module:
01. https://github.com/python-pillow/Pillow/blob/master/docs/installation.rst
02. BeautifulSoup
03. https://pypi.python.org/pypi/fake-useragent
'''

# import module
import re
import urllib2
import urllib
import socket
import ssl
import platform
# import requests
# import maketrans
from string import maketrans
# import beautifulsoup module
from bs4 import BeautifulSoup
# import Pillow
from PIL import Image
# import fake useragent
from fake_useragent import UserAgent
ua = UserAgent()

# update user agent database
# ua.update()


# Register an handler for the timeout
def handler(signum, frame):
    print "Time Out!"
    raise Exception("end of time")


# creating function to download product image
def downloadproductimage(imageurl, namafoldergambarproduk, namaproduk, image_counter):
    imageurl = imageurl
    # target size for the image
    targetsize = 600
    # check system platform
    system_platform = platform.system()
    if system_platform == "Windows":
        zzzz = "\\"
        import eventlet
        eventlet.monkey_patch()

    else:
        zzzz = "/"
        import signal
    # check if namafoldergambarproduk ends with "/" or "\"
    if namafoldergambarproduk[-1] != zzzz:
        namafoldergambarproduk = namafoldergambarproduk + zzzz
    # create image file name
    imagefilename = namafoldergambarproduk + namaproduk + "-" + str(image_counter) + ".jpg"
    # download status flag
    download_flag = False
    # initialize response
    response = None
    # download image if running on windows
    if system_platform == "Windows":
        for coba in range(1, 6):
            try:
                with eventlet.Timeout(15, False):
                    response = urllib.urlretrieve(imageurl, imagefilename)
                if response is None:
                    print "Request timed out after 15 seconds. " + imageurl + "    (Tries = " + str(coba) + ")"
                    download_flag = False
                    continue
                download_flag = True
                print "Image downloaded succesfully"
                break
            except IOError:
                print "Unable to download image" + imageurl + "    (Tries = " + str(coba) + ")"
                download_flag = False
                continue
            except urllib.ContentTooShortError:
                print "Image url contents less data than expected"
                download_flag = False
                continue
    else:
        # downloading images on Linux or other UNIX platform
        # Register the signal function handler
        signal.signal(signal.SIGALRM, handler)
        for coba in range(1, 6):
            # define a timeout for downloading
            signal.alarm(15)
            try:
                response = urllib.urlretrieve(imageurl, imagefilename)
                signal.alarm(0)
                download_flag = True
                print "Image downloaded succesfully"
                break
            except IOError:
                print "Unable to download image" + imageurl + "    (Tries = " + str(coba) + ")"
                download_flag = False
                signal.alarm(0)
                continue
            except urllib.ContentTooShortError:
                print "Image url contents less data than expected"
                download_flag = False
                signal.alarm(0)
                continue
            except Exception:
                print "Request timed out after 15 seconds. " + imageurl + "    (Tries = " + str(coba) + ")"
                download_flag = False
                continue

    if download_flag is False:
        print "Download image failed after 5 tries."
        return

    # try to open image
    try:
        originalimage = Image.open(imagefilename)
    except IOError:
        print "Unable to load image"
        return

    # calculate image size
    imagewidth, imageheight = originalimage.size
    resizeimageby = float(targetsize) / float(max(imagewidth, imageheight))
    print "resize factor = " + str(resizeimageby)
    # if image size is smaller than 400 px, do enlargement
    imagewidth = int(resizeimageby * float(imagewidth))
    imageheight = int(resizeimageby * float(imageheight))
    if imagewidth < 300:
        resizeimageby = float(350) / float(imagewidth)
        print "image width < 300. recalculate size"
        imagewidth = int(resizeimageby * float(imagewidth))
        imageheight = int(resizeimageby * float(imageheight))
    if imageheight < 300:
        resizeimageby = float(350) / float(imageheight)
        print "image height < 300. recalculate size"
        imagewidth = int(resizeimageby * float(imagewidth))
        imageheight = int(resizeimageby * float(imageheight))
    print "Ukuran gambar = " + str(imagewidth) + " " + str(imageheight)
    # resize the image
    originalimage = originalimage.resize([imagewidth, imageheight], Image.ANTIALIAS)
    # save resized image. overwrite the old image file
    originalimage.convert("RGB").save(imagefilename, 'JPEG', quality=90)
    return


def tokopediaproductscrapper(urlproduk, mode=0, namafoldergambarproduk=""):
    # set global timeout setting
    socket.setdefaulttimeout(30)
    # print "URL Produk = " + urlproduk
    request = urllib2.Request(urlproduk, headers={'User-Agent': ua.chrome})

    # initialize dataproduk
    dataproduk = None
    # opening URL. max tries = 5 times
    for coba in range(1, 6):
        try:
            dataproduk = urllib2.urlopen(request).read()
            # break from loop
            break
        except urllib2.HTTPError:
            print "Error opening URL = " + urlproduk + "    (Tries = " + str(coba) + ")"
            continue
            # continue
        except urllib2.URLError:
            print "URL Error not valid = " + urlproduk + "    (Tries = " + str(coba) + ")"
            continue
            # continue
        except ssl.SSLError:
            print "SSL Error = " + urlproduk + "    (Tries = " + str(coba) + ")"
            continue
            # continue
    # if after 5 tries dataproduct still an ampty variable, exit function
    if dataproduk is None:
        print "Failed after 5 tries"
        return False
    # else:
    #    print "Other Error occured = " + urlproduk
    #    continue

    # creating soup
    dataproduk = BeautifulSoup(dataproduk, 'html.parser')
    # print dataproduk
    # get product name.
    for temp in dataproduk.find_all('h1'):
        namaproduk = temp.get_text().encode("utf-8", "replace")
        # delete this characters < > : " / \ | ? * from namaproduk
        # because namaproduk will also be used as image filename
        trantab = maketrans(r'<>:"/\|?*', r'---------')
        namaproduk = namaproduk.translate(trantab)
        # remove trailing spaces from namaproduk
        namaproduk = ' '.join(namaproduk.split())
        print "Nama Produk = " + namaproduk

    # get product availability status
    productavailability = ""
    for temp in dataproduk.find_all("div", class_="alert alert-block"):
        productavailability = temp.get_text().encode("utf-8", "replace")

    # get detail information of product
    for temp in dataproduk.find_all("div", "detail-info"):
        info = temp.get_text().encode("utf-8", "replace").replace("\n", "").strip(' \t\n\r')
        info = " ".join(info.split())
        berat = re.search(r'Berat(.*?)Terjual', info)
        berat = berat.group(1)
        print "Berat = " + str(berat)
        # print ":".join("{:02x}".format(ord(c)) for c in berat)

        # get insurance (there are two option, wajib = need insurance or opsional = insurance is optional)
        asuransi = re.search(r'Asuransi(.*?)Kondisi', info)
        asuransi = asuransi.group(1)
        print "Asuransi = " + asuransi

        # get product condition (new or used/secondhand)
        kondisi = re.search(r'Kondisi(.*?)Pemesanan', info)
        kondisi = kondisi.group(1)
        print "Kondisi = " + kondisi

        # get minimum purchase quantity. I get problem using regex for this one, so I just use find
        minpemesanan = info[(info.find("Min") + 4):]
        for s in minpemesanan.split():
            if s.isdigit():
                minpemesanan = s
        print "Pemesanan Min. = " + str(minpemesanan)

    # replace br with new line
    for temp in dataproduk.find_all("br"):
        temp.replace_with("\n")
    # get product description
    for temp in dataproduk.find_all("p", itemprop="description"):
        deskripsi = temp.get_text().encode("utf-8", "replace")
        if len(deskripsi) > 30:
            print "Deskripsi = " + deskripsi[:30]
        else:
            print "Deskripsi = " + deskripsi

    # get retail price of product
    for temp in dataproduk.find_all("div", class_="product-pricetag"):
        hargaproduk = temp.get_text().encode("utf-8", "replace")
        print "Harga Produk = " + hargaproduk

    # initialize empty list for product category
    kategoriproduk = []
    # get product category. from h2 tag
    kategoriproduk_soup = dataproduk.find_all("h2")
    # the category can be divided into. MAIN CATEGORY => SUB-MAIN CATEGORY => MINOR CATEGORY.
    # and when using h2 tag to get category, there will be also 2 unnecessary result
    # the unnecessary result or data located at the beginning and at the end.
    # thats why i use for loop starting from 1 (not 0) until category result - 1 (not just category result)
    for x in range(0, len(kategoriproduk_soup) - 1):
        kategoriproduk.append(kategoriproduk_soup[x].get_text().encode("utf-8", "replace"))
        print "Kategori Produk = " + kategoriproduk[x]

    # get data for wholesale price if any. if there is no wholesale price for the product,
    # this process will return an empty list.
    for temp in dataproduk.find_all("ul", class_="product-ratingstat", limit=1):
        # create a new string data to be "soup-ed".
        grosirhtml = str(temp)
        # this is the new soup
        grosirdata = BeautifulSoup(grosirhtml, 'html.parser')
        # get wholesale quantity
        grosirdata_kuantiti = grosirdata.find_all("span", class_="product-ratingstat_quantity")
        # get wholesale price
        hargagrosir_list = grosirdata.find_all("span", class_="bold")
        kuantitigrosir = []
        hargagrosir = []
        for x in range(0, len(grosirdata_kuantiti)):
            # tried to group wholesale quantity
            # with it corresponding wholesale price
            kuantitigrosir_text = grosirdata_kuantiti[x].get_text().encode("utf-8", "replace")
            kuantitigrosir.append(kuantitigrosir_text)
            hargagrosir_text = hargagrosir_list[x].get_text().encode("utf-8", "replace")
            hargagrosir.append(hargagrosir_text)
            print "Range kuantitas = " + kuantitigrosir[x] + " Harga Grosir = " + hargagrosir[x]

    # get url for product image. using same method
    # with scraping wholesale quantity and prices above.
    list_url_gambar = []
    for temp in dataproduk.find_all("div", class_="product-image-holder", limit=1):
        # create a new string data to be soup-ed
        datagambar = str(temp)
        # make a new soup
        datagambar_soup = BeautifulSoup(datagambar, 'html.parser')

        # extracting image url
        image_counter = 0
        for linkgambar_list in datagambar_soup.find_all('a'):
            temp_gambar = linkgambar_list.get('href')
            # remove "#" from result
            if temp_gambar != "#":
                image_counter = image_counter + 1
                list_url_gambar.append(temp_gambar)
                print "Url Gambar = ", temp_gambar
                # if mode = 1 download product images
                if mode == "1":
                    downloadproductimage(temp_gambar, namafoldergambarproduk, namaproduk, image_counter)
        # check how many image urls extracted and add additional element to make list_url_gambar has 5 element
        total_url_gambar = len(list_url_gambar)
        print "Total url gambar = ", total_url_gambar
        if total_url_gambar < 5:
            for x in range(total_url_gambar, 5):
                list_url_gambar.append("")
    # check the category result. if there are less than 3 category
    # (sub-category) than, append "-" to make it three.
    if len(kategoriproduk) < 3:
        for x in range(len(kategoriproduk), 3):
            kategoriproduk.append("-")
    if len(kuantitigrosir) < 3:
        for x in range(len(kuantitigrosir), 3):
            kuantitigrosir.append("")
    if len(hargagrosir) < 3:
        for x in range(len(hargagrosir), 3):
            hargagrosir.append("")
    # print new line to give some space
    print "\n"
    dictdataproduk = {
        'Nama Produk': namaproduk,
        'Harga Ecer': hargaproduk,
        'Minimal Pembelian': minpemesanan,
        'Berat Produk': berat,
        'Asuransi': asuransi,
        'Kondisi Produk': kondisi,
        'Kategori 1': kategoriproduk[0],
        'Kategori 2': kategoriproduk[1],
        'Kategori 3': kategoriproduk[2],
        'Deskripsi': deskripsi,
        'Kuantitas Grosir 1': kuantitigrosir[0],
        'Harga Grosir 1': hargagrosir[0],
        'Kuantitas Grosir 2': kuantitigrosir[1],
        'Harga Grosir 2': hargagrosir[1],
        'Kuantitas Grosir 3': kuantitigrosir[2],
        'Harga Grosir 3': hargagrosir[2],
        'Availability': productavailability,
        'URL Product': urlproduk,
        'Image URL 1': list_url_gambar[0],
        'Image URL 2': list_url_gambar[1],
        'Image URL 3': list_url_gambar[2],
        'Image URL 4': list_url_gambar[3],
        'Image URL 5': list_url_gambar[4],
    }
    return dictdataproduk
