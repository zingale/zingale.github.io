# Makefile to build a shared library interface to the serial HDF5 IO 
# routines so they can be read into IDL

# Linux version

# Note, you need to have the HDF5 shared-object library in your library 
# path, or call_external will fail.  
#
#Try setting LD_LIBRARY_PATH to the proper location

HDF5path = /opt/HDF5-1.4.2-patch1-serial

IDLpath = /usr/local/rsi/idl_5.4/external

OBJS = hdf5_wrappers.o

CCFLAGS = -fPIC -I $(HDF5path)/include -I $(IDLpath)

.c.o : 
	gcc ${CCFLAGS} -c $<



LDFLAGS = -shared -fPIC

LIB = -L ${HDF5path}/lib -lhdf5

hdf5_wrappers.so: ${OBJS}
	cc -o $@ ${LDFLAGS} ${OBJS} ${LIB}

