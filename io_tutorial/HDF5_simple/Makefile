HDF5path = /opt/HDF5-1.4.2-patch1-serial

CCOMP = gcc

CFLAGS = -I ${HDF5path}/include -c -O2


OBJS = hdf5_simple.o


default: hdf5_simple_example


.c.o :
	$(CCOMP) $(CFLAGS) $*.c


LIB = -L ${HDF5path}/lib -lhdf5


hdf5_simple_example : ${OBJS}
	$(CCOMP) -o $@ ${OBJS} ${LIB}


