/* 
 * Header file for IDL - HDF5 interface.  
 *
 *  At present, IDL does not support HDF5 files, so reading in a file
 *  must be done via the call_external function.  call_external uses
 *  argc/v to pass data into the C routines.  These pointers are then
 *  recast immediately inside these routines.
 *
 *  These wrappers need access to the HDF5 headers and library, and the
 *  IDL export.h header file -- for the definition of the string structure.
 *
 *  This must be compiled as a shared-object library.
 */

#ifndef _HDF5_IDL_H
#define _HDF5_IDL_H

#include "hdf5.h"
#include "export.h"

#define MAX_STRING_SIZE 100

#endif






