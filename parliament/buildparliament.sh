#!/bin/ksh

BUILD_PATH=$1
INSTALL_PATH=$2
START_PATH=`pwd`
BDB_URL=http://ftp.de.debian.org/debian/pool/main/d/db/db_5.1.25.orig.tar.gz
BDB_NAME=db-5.1.25

BOOST_URL='http://downloads.sourceforge.net/project/boost/boost/1.47.0/boost_1_47_0.tar.bz2?r=&ts=1314710663&use_mirror=iweb'
BOOST_NAME=boost_1_47_0

build_bdb() {
    wget $BDB_URL -O $BUILD_PATH/src/bdb.tar.gz
    tar xfz $BUILD_PATH/src/bdb.tar.gz -C $BUILD_PATH/src/
    cd $BUILD_PATH/src/$BDB_NAME/build_unix
    echo 'Unpacked BDB!'
    mkdir $INSTALL_PATH
    env CFLAGS="-m32" ../dist/configure --prefix=$INSTALL_PATH/BDB/32
    make
    make install
    make realclean
    if [[ `uname -p` != 'i686' ]]; then
	env CFLAGS="-m64" ../dist/configure --prefix=$INSTALL_PATH/BDB/64
	make 
	make install
	make realclean
    fi
    cd $START_PATH
}

build_boost() {
    wget $BOOST_URL -O $BUILD_PATH/src/boost.tar.bz2
    tar xfj $BUILD_PATH/src/boost.tar.bz2 -C $INSTALL_PATH/
    cd $INSTALL_PATH/$BOOST_NAME
    echo 'Changing to path: ' $INSTALL_PATH/$BOOST_NAME
    sh bootstrap.sh --show-libraries


    mkdir $INSTALL_PATH/bin
    export PATH=$PATH:$INSTALL_PATH/bin
    cp $BOOST_ROOT/bjam $INSTALL_PATH/bin

    bjam -q --build-dir=gcc-32/build --stagedir=gcc-32/stage \
	--layout=versioned --with-test address-model=32 \
	variant=debug,release threading=multi link=shared \
	runtime-link=shared stage

    if [[ `uname -p` != 'i686' ]]; then
	 bjam -q --build-dir=gcc-64/build --stagedir=gcc-64/stage \
	--layout=versioned --with-test address-model=64 \
	variant=debug,release threading=multi link=shared \
	runtime-link=shared stage
    fi
    
    cd $START_PATH
}

build_parliament() {
    cd $BUILD_PATH/
#    svn checkout --username anonsvn --password anonsvn \
#	https://projects.semwebcentral.org/svn/parliament/trunk parliament
    export PATH=$INSTALL_PATH/bin:$PATH
    cp site-config.jam $BOOST_BUILD_PATH
    cp user-config.jam $BOOST_BUILD_PATH
    cd $START_PATH
    cd $BUILD_PATH/parliament
    ant
   

}

mkdir $BUILD_PATH
mkdir $BUILD_PATH/src
build_bdb
export BDB_HOME=$INSTALL_PATH/BDB/

mbuild_boost
export BOOST_ROOT=$INSTALL_PATH/$BOOST_NAME
export BOOST_BUILD_PATH=$BOOST_ROOT/tools/build/v2
build_parliament