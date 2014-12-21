HDF5path = /opt/HDF5-1.4.2-patch1-serial

CCOMP = mpicc

CFLAGS = -I ${HDF5path}/include -c -O2


OBJS = hdf5_serial.o


default: hdf5_serial_example


.c.o :
	$(CCOMP) $(CFLAGS) $*.c


LIB = -L ${HDF5path}/lib -lhdf5


hdf5_serial_example : ${OBJS}
	$(CCOMP) -o $@ ${OBJS} ${LIB}


