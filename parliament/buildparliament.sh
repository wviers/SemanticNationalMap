#!/bin/ksh

BUILD_PATH=$1
INSTALL_PATH=$2
BDB_URL=http://ftp.de.debian.org/debian/pool/main/d/db/db_5.1.25.orig.tar.gz
BDB_NAME=db-5.1.25

build_bdb() {
    mkdir $BUILD_PATH/src/
    wget $BDB_URL -O $BUILD_PATH/src/bdb.tar.gz
    tar xfz $BUILD_PATH/src/bdb.tar.gz -C $BUILD_PATH/src/
    cd $BUILD_PATH/src/$BDB_NAME/build_unix
    echo 'Unpacked BDB!'
    mkdir $INSTALL_PATH
    env CFLAGS="-m32" ../dist/configure --prefix=$INSTALL_PATH/BDB/32
    make
    make install
    make realclean
    env CFLAGS="-m64" ../dist/configure --prefix=$INSTALL_PATH/BDB/64
    make 
    make install
    make realclean

}

mkdir $BUILD_PATH
build_bdb
