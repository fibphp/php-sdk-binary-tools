# 基础步骤

- cd D:\php_sdk\phpdev\vc15\x64\php-src

- phpsdk_buildtree phpdev
- phpsdk_deps --update
- buildconf
- configure --disable-all --enable-cli --disable-zts
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

