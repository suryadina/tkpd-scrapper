=======================================================
COMPARATOR DATA PRODUK TOKOPEDIA
Versi 2.5 by Ardya (deenata.com)
=======================================================
Log Update:
versi 1.0: initial release
versi 2.0: perubahan format output tools
versi 2.1: 2 Oktober 2016: perubahan cara pembuatan nama file output
versi 2.2: 2 Oktober 2016: perbaikan bug yang membuat kalo scrapeproduct gagal, maka data menjadi gak ketulis
versi 2.3: 1 Nopember 2016: 
    => penambahan argumen parse
    => pengubahan pencatatan log
versi 2.4: 12 Nopember 2016:
    => perubahan format penulisan log
versi 2.5: 15 January 2017:
	=> change log format
	=> add feature: use config file as source of arguments
versi 2.5.1: 15 January 2017:
	=> bug fixing
versi 2.5.2: 16 January 2017:
	=> change log format
	=> bug fix (DebugPrint removed)
versi 2.5.3: 17 January 2017:
	=> change log format. remove trailing space after "#" and change log information
versi 2.6: 16 August 2017:
	=> add image urls comparation. this feature will allow us to check if there is a change in product image.
versi 2.7: 31 August 2017:
	=> use tokopedia_tools_library_1_3_1
=======================================================
Pre-requirements:
01. Pengguna menyediakan file data produk (yang merupakan output dari tool "tokopedia-product-data-scrapper.py").

Input Argument:
01. File data produk (yang merupakan output dari tool "tokopedia-product-data-scrapper.py" atau output dari tools ini) 
02. Nama file output (data produk "baru")  yang diinginkan

Output Program:
01. File Log (berisi catatan proses komparasi dan perubahan pada produk)
02. File data produk yang "baru" yang berbeda dengan data dari file inputan
03. File data "allproduct" yang baru dengan format sama seperti output tokopedia-product-data-scrapper.py

Notes:
01. After run this script, please inspect the results manually
02. Gambar produk tidak dibandingkan
=======================================================
Config File Format example:

[settings]
input: 20161212-1-modisshop-raw-data-all-product.csv
output: tes-output.csv

=======================================================
Future Development

1. Use config file. ==> Done
2. Make this tool ready to run repeatedly using cron or windows task scheduler. ==> Canceled
3. Reformat results file ==> Canceled. new results format will be produced by another new script. not this one.
4. Results verification ==> Canceled
5. Change log format ==> Done
=======================================================
Bugs:

