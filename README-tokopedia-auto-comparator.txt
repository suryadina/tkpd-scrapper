TOKOPEDIA AUTO COMPARATOR
=========================================
=========================================
Version history:
=> version 1.0: 10 Nopember 2016. Initial version
=> version 1.0.1: 15 January 2017. Minor updates
=> version 1.2: 19 January 2017. fix bug in sending email
=> version 1.3: 10 September 2017. Update tools and library. Reduce comparation frequency to once a day
=========================================
Description:

This script will run tokopedia-product-data-comparator.py and tokopedia-product-data-formatter twice in a day.
As input, a config file with specific format required (Config file format attached below this description).

USAGE:
tokopedia-auto-comparator-1.2.sh (config_file)
=========================================
Config File Format:

<tokopedia username>,<total product to compare>,<retail price min. margin>,<etalase>,<recipient email>

ex:
modisshop,152,0,Sale,rababyshop@gmail.com
chinatown,260,0,Unik,rababyshop@gmail.com
cherrybabykids,559,0,Baby,rababyshop@gmail.com
