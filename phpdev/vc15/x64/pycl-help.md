# 基础步骤

- phpsdk_buildtree phpdev
- phpsdk_deps --update
- buildconf
- configure --disable-all --enable-cli –disable-zts
- nmake

# 编译参数

Install PHP 7.4, being sure to enable the FFI extension, OpenSSL extension, mbstring extension, and zlib extension (--with-ffi --with-openssl --enable-mbstring --with-zlib).

configure --disable-all --with-ffi --with-openssl --enable-mbstring --with-zlib --enable-cli --disable-zts

# 自定义生成

configure --disable-all --with-ffi --with-openssl --enable-mbstring --with-zlib --enable-cli --disable-zts

nmake

nmake clean

nmake /N > nmake_cl.txt

python ..\\pycl.py clbuild

preprocess.bat

python ..\\pycl.py clean_pp

nmake clean

clbuild.bat

cllink.bat

