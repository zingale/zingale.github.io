/* 
 * Demonstrate how to store a 2-d array in an HDF5 file, using serial I/O. 
 * We will create 2 records in the file.  The array itself, and a simple
 * user comment.
 *
 * Our 2-d array will contain a perimeter of guardcells, which we do not
 * wish to store on disk.  Only the interior ny x nx region will be stored.
 *
 */


#include <stdio.h>
#include <stdlib.h>

#include "hdf5.h"


void print_array(int, int, int, double **);

void init_array(int, int, int, double **);


int main() {

  int i, j;

  int nx, ny;
  int ng;

  double *buffer;
  double **data;

  int rank;
  hsize_t dimens_1d, dimens_2d[2];
  hid_t err;

  hssize_t start_2d[2];
  hsize_t stride_2d[2];
  hsize_t count_2d[2];

  hid_t dataspace, memspace, dataset;

  hid_t string_type;

  char *filename = "example.hdf5";

  char comment[] = "This is an HDF5 example file";

  hid_t file_identifier;


  /* set the dimensions of our data array and the number of guardcells */
  nx = 10;
  ny = 10;

  ng = 2;


  /*--------------------------------------------------------------------------
   * allocate a 2-d contiguous array, data[ny][nx], and initialize it with
   * some random data.
   *-------------------------------------------------------------------------*/

  buffer = (double *) malloc(sizeof(double)*(nx+2*ng)*(ny+2*ng));

  data = (double **) malloc(sizeof(double *)*(ny+2*ng));

  for (i = 0; i < ny+2*ng; i++) {
    data[i] = buffer + i*(nx+2*ng);
  }


  init_array(nx, ny, ng, data);

  print_array(nx, ny, ng, data);

  /*--------------------------------------------------------------------------
   * Now open the HDF5 file for output and write out the data array 
   *-------------------------------------------------------------------------*/


  /* H5Fcreate takes several arguments in addition to the filename.  We 
     specify H5F_ACC_TRUNC to the second argument to tell it to overwrite 
     an existing file by the same name if it exists.  The next two 
     arguments are the file creation property list and the file access
     property lists.  These are used to pass options to the library about
     how to create the file, and how it will be accessed (ex. via mpi-io).
     For now we take the defaults. */

  file_identifier = H5Fcreate(filename, H5F_ACC_TRUNC, H5P_DEFAULT, 
			      H5P_DEFAULT);
  

  /*--------------------------------------------------------------------------
   * Start by creating a record that stores the comment 
   *-------------------------------------------------------------------------*/
  
  /* to store a string in HDF5, we need to build a special type out of 
     character types.  We use H5T_C_S1 -- a one-byte, null-terminated
     string -- as the basis for our type */
  string_type = H5Tcopy(H5T_C_S1);
  H5Tset_size(string_type, strlen(comment));

  /* next we create a dataspace -- these describes how the data is stored
     in the file.  We need to tell it the rank and the dimensions of the
     record we are storing */
  rank = 1;
  dimens_1d = 1;

  /* The data we are storing will be contiguous on disk, so we can just 
     create a simple dataspace.  H5Screate_simple takes 3 arguments, the
     rank, an array (or size rank) of the dimensions, and a maxdims argument
     that can be used to create unlimited sized datasets -- we use NULL 
     here */
  dataspace = H5Screate_simple(rank, &dimens_1d, NULL);
  
  /* next we create the dataset -- this tells the library the type of 
     data we are storing, a record name that we will refer to it by,
     and the dataspace that describes the data.  The last argument 
     refers to the dataset property list -- this can be used to tell
     the library to use compression, or various properties about how
     it is stored on disk.  We accept the defaults here */
  dataset = H5Dcreate(file_identifier, "comment", string_type, 
		      dataspace, H5P_DEFAULT);

  
  /* finally we write it to the file.  We give H5Dwrite the data set to write
     to, the type of data, information on how the data is stored in memory
     (in this case it is trivial, so we use H5S_ALL), the dataspace, a
     data transfer property list (we take the default), and a pointer to the 
     data buffer */
  err = H5Dwrite(dataset, string_type, H5S_ALL, dataspace, 
		 H5P_DEFAULT, comment);


  /* after the write, we are done with this dataspace and dataset, so we
     need to free the space we allocated for them. */
  H5Sclose(dataspace);
  H5Dclose(dataset);


  /*--------------------------------------------------------------------------
   * Now store the data array -- interior zones only
   *-------------------------------------------------------------------------*/

  rank = 2;

  /* create the dataspace (how it will be stored on disk).  Here we want to
     store just the interior of the array -- not the guardcells.  */
  dimens_2d[0] = ny;
  dimens_2d[1] = nx;

  dataspace = H5Screate_simple(rank, dimens_2d, NULL);
  
  /* now we need to create a memory space.  This describes the layout of the
     data in memory.  There must be the same number of elements in memory as
     we plan to store on disk, but the layouts need not be the same.  In our
     case, our memory space will not be contiguous, since we are skipping over
     the guardcells. */
  
  /* start by creating a memory space that includes the entire data array, 
     as it is stored in memory */
  dimens_2d[0] = ny+2*ng;
  dimens_2d[1] = nx+2*ng;


  memspace = H5Screate_simple(rank, dimens_2d, NULL);

  /* now, use the HDF5 hyperslab function to pick out the portion of the data
     array that we intend to store */

  start_2d[0] = ng;
  start_2d[1] = ng;

  stride_2d[0] = 1;
  stride_2d[1] = 1;

  count_2d[0] = ny;
  count_2d[1] = nx;

  err = H5Sselect_hyperslab(memspace, H5S_SELECT_SET, 
			    start_2d, stride_2d, count_2d, NULL);
     
  

  /* now create the dataset */
  dataset = H5Dcreate(file_identifier, "data array", H5T_NATIVE_DOUBLE,
		      dataspace, H5P_DEFAULT);


  /* and finally write the data to disk -- in this call, we need to include
   both the memory space and the data space. */
  err = H5Dwrite(dataset, H5T_NATIVE_DOUBLE, memspace, dataspace, 
		 H5P_DEFAULT, &(data[0][0]));

  H5Sclose(memspace);
  H5Sclose(dataspace);
  H5Dclose(dataset);



  /*--------------------------------------------------------------------------
   * finally, close the file
   *-------------------------------------------------------------------------*/
   
  H5Fclose(file_identifier);



}
  


  
void print_array(int nx, int ny, int ng, double **array) {

  int i, j;

  for (j = 0; j < ny+2*ng; j++) {
    for (i = 0; i < nx+2*ng; i++) {

      printf("%f ", array[j][i]);

    }
    printf("\n");
  }

}


void init_array(int nx, int ny, int ng, double **array) {

  /* initialize the guardcells to 0, and the interior
     i+j+1 */

  int i, j;

  for (j = 0; j < ny+2*ng; j++) {
    for (i = 0; i < nx+2*ng; i++) {

      array[j][i] = 0.0;

    }
  }

  
  for (j = ng; j < ny+ng; j++) {
    for (i = ng; i < nx+ng; i++) {

      array[j][i] = (double) (i+j+1);

    }
  }

}
