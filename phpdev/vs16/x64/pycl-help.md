# 基础步骤

- cd D:\php_sdk\phpdev\vs17\x64\php-src

- phpsdk_buildtree phpdev
- phpsdk_deps --update
- buildconf
- configure --disable-all --enable-cli --disable-zts --enable-debug
- 
- configure --disable-all --enable-cli --disable-zts --enable-debug --disable-opcache-jit --disable-filter
- 
- configure --disable-all --enable-cli --disable-zts --disable-debug --disable-opcache-jit --disable-filter
- 
- nmake

# 编译参数

Install PHP 7.4, being sure to enable the FFI extension, OpenSSL extension, mbstring extension, and zlib extension (--with-ffi --with-openssl --enable-mbstring --with-zlib).

configure --disable-all --with-ffi --with-openssl --enable-mbstring --with-zlib --enable-cli --disable-zts

# 自定义生成

configure --disable-all --with-ffi --with-openssl --enable-mbstring --with-zlib --enable-cli --disable-zts

configure --disable-all --enable-cli --enable-zts

configure --disable-all --enable-cli --enable-opcache --enable-zts --enable-debug --enable-phpdbg --enable-vld --with-all-shared

configure --disable-all --enable-cli --enable-opcache --enable-vld --with-all-shared


configure --disable-all --enable-cli --enable-debug --enable-phpdbg --with-xdebug --enable-opcache --enable-vld --with-all-shared

php -dvld.active=1 -dvld.execute=0 -dvld.dump_json=1 -dvld.format main.php

configure --disable-zts --enable-debug --disable-all --enable-cli --enable-opcache

## release lib 

configure --disable-zts --disable-all --enable-cli --enable-opcache

configure --disable-all --enable-cli --disable-zts --disable-debug --disable-opcache-jit --disable-filter

configure --disable-all --enable-cli --disable-zts --enable-debug --disable-opcache-jit --disable-filter

nmake clean

nmake

nmake clean

nmake /N > nmake_cl.txt

python2 ..\\pycl.py clbuild

preprocess.bat

python2 ..\\pycl.py clean_pp

nmake clean

clbuild.bat

cllink.bat



TIME END 2023-11-19 10:08:09

=====================================================================
TEST RESULT SUMMARY
---------------------------------------------------------------------
Exts skipped    :    65 (bcmath, bz2, calendar, com_dotnet, ctype, curl, dba, dl_test, dom, enchant, exif, ffi, fileinfo, filter, ftp, gd, gettext, gmp, iconv, imap, intl, ldap, libxml, mbstring, mysqli, mysqlnd, oci8, odbc, opcache, openssl, pcntl, pdo, pdo_dblib, pdo_firebird, pdo_mysql, pdo_oci, pdo_odbc, pdo_pgsql, pdo_sqlite, pgsql, phar, posix, pspell, readline, session, shmop, simplexml, skeleton, snmp, soap, sockets, sodium, sqlite3, sysvmsg, sysvsem, sysvshm, tidy, tokenizer, xml, xmlreader, xmlwriter, xsl, zend_test, zip, zlib)
Exts tested     :    10
---------------------------------------------------------------------

Number of tests : 18585             10057
Tests skipped   :  8528 ( 45.9%) --------
Tests warned    :     0 (  0.0%) (  0.0%)
Tests failed    :    13 (  0.1%) (  0.1%)
Tests passed    : 10044 ( 54.0%) ( 99.9%)
---------------------------------------------------------------------
Time taken      :  1112 seconds
=====================================================================

=====================================================================
FAILED TEST SUMMARY
---------------------------------------------------------------------
Testing bug #65371 [D:\php_sdk\phpdev\vs16\x64\php-src\ext\date\tests\bug65371.phpt]
SPL: RecursiveDirectoryIterator::hasChildren() follow symlinks test [D:\php_sdk\phpdev\vs16\x64\php-src\ext\spl\tests\RecursiveDirectoryIterator_hasChildren.phpt]
Test fileatime(), filemtime(), filectime() & touch() functions : usage variation [D:\php_sdk\phpdev\vs16\x64\php-src\ext\standard\tests\file\005_variation-win32.phpt]
Test disk_free_space and its alias diskfreespace() functions : error conditions [D:\php_sdk\phpdev\vs16\x64\php-src\ext\standard\tests\file\disk_free_space_error-win32.phpt]
Test disk_total_space() function : error conditions [D:\php_sdk\phpdev\vs16\x64\php-src\ext\standard\tests\file\disk_total_space_error-win32.phpt]
Test realpath() with relative paths [D:\php_sdk\phpdev\vs16\x64\php-src\ext\standard\tests\file\realpath_basic4.phpt]
Test rename() function: usage variations [D:\php_sdk\phpdev\vs16\x64\php-src\ext\standard\tests\file\rename_variation-win32.phpt]
Test rename() function : variation - various relative, absolute paths [D:\php_sdk\phpdev\vs16\x64\php-src\ext\standard\tests\file\rename_variation11-win32.phpt]
Test rename() function : variation - various relative, absolute paths [D:\php_sdk\phpdev\vs16\x64\php-src\ext\standard\tests\file\rename_variation12-win32.phpt]
Test rename() function : variation - various invalid paths [D:\php_sdk\phpdev\vs16\x64\php-src\ext\standard\tests\file\rename_variation13-win32.phpt]
Test rename() function: usage variations [D:\php_sdk\phpdev\vs16\x64\php-src\ext\standard\tests\file\rename_variation3-win32.phpt]
Test rename() function: variation [D:\php_sdk\phpdev\vs16\x64\php-src\ext\standard\tests\file\rename_variation8-win32.phpt]
Bug #71273 A wrong ext directory setup in php.ini leads to crash [D:\php_sdk\phpdev\vs16\x64\php-src\tests\basic\bug71273.phpt]
=====================================================================

You may have found a problem in PHP.
This report can be saved and used to open an issue on the bug tracker at
https://github.com/php/php-src/issues
This gives us a better understanding of PHP's behavior.
