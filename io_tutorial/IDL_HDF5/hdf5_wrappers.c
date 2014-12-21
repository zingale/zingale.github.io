#include <stdio.h>
#include "hdf_idl.h"

/* xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx */

int open_file(int argc, char** argv)
{
  /* 
   * open_file: open the HDF 5 file and return the file handle
   *
   * input:  filename (string)
   *
   * output: file handle (integer)
   *
   * IDL calling sequence:
   *
   *    file_identifier = (lonarr(1))[0]
   *    
   *    ierr = call_external('h5_wrappers.so', 'open_file', $
   *                         file_identifier, filename)
   *
   *
   */

  hid_t*      file_identifier = (hid_t *)      argv[0];
  IDL_STRING* filename_struct = (IDL_STRING *) argv[1];

  char* filename;

  int len = 0;
  char* string_index; 
  char local_filename[256];

  /* isolate the filename from the idl string structure */
  filename = filename_struct->s; 
  
  printf ("trying to open filename %s\n", filename);

  /* initialize the file identifier */
  *file_identifier = 0;


  strcpy(local_filename, filename);

  string_index = local_filename;
  
  while (*string_index != ' ') {
    len++;
    string_index++;
  }

  *(local_filename+len) = '\0';


  /* open the file */
  *file_identifier = H5Fopen(local_filename, H5F_ACC_RDONLY, H5P_DEFAULT); 
    

  if (*file_identifier < 0) {
    printf("Error opening file %s for input", local_filename);
    exit(1);
  }

  printf ("Opened the file with file_id %d \n",*file_identifier);

  return 0;
}


/* xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx */

int close_file(int argc, char** argv)
{
  /* 
   * close_file: close the HDF 5 file
   *
   * input:  file handle (integer)
   *
   * output: none
   *
   * IDL calling sequence:
   *
   *    ierr = call_external('h5_wrappers.so', 'close_file', $
   *                         file_identifier)
   *
   *
   */

  hid_t* file_identifier = (hid_t *) argv[0];

  H5Fclose(*file_identifier);

  return 0;
}


/* xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx */

int read_comment(int argc, char ** argv)
{
  /* 
   * read the comment stored in the HDF5 file
   *
   * input: file handle (integer)
   *
   * output: comment   (character string)
   *
   * IDL calling sequence:
   *
   * comment = 'comment               '
   *
   * ierr = call_external('hdf5_wrappers.so', 'read_comment', $
   *                      file_identifier, $
   *                      comment)
   *
   */

  hid_t      *file_identifier = (hid_t *)      argv[0];
  IDL_STRING *comment         = (IDL_STRING *) argv[1];

  hid_t dataset, dataspace, string_type;

  size_t string_type_size;
  int comment_length;

  int ierr;

  int i;
 
  char scratch[MAX_STRING_SIZE];

  /* get the dataset */
  dataset = H5Dopen(*file_identifier, "comment");

  /* get the dataspace */
  dataspace = H5Dget_space(dataset);

  /* get the string type from the file */
  string_type = H5Dget_type(dataset);

  /* read the comment into a buffer */
  ierr = H5Dread(dataset, string_type, H5S_ALL, dataspace, 
		 H5P_DEFAULT, scratch);

  string_type_size = H5Tget_size(string_type);
  comment_length = (int) string_type_size / sizeof(char);
  
  for (i=0; i< comment_length; i++) {
    comment->s[i] = scratch[i];
  }

  H5Sclose(dataspace);
  H5Tclose(string_type);
  H5Dclose(dataset);

}




/* xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx */
int get_data_dimens(int argc, char **argv) 
{
  /* 
   * return the rank and dimensions of the data array
   *
   * calling example:
   *
   *   rank = (lonarr(1))[0]
   *   dimens = lonarr(10)
   *
   *   ierr = call_external('hdf5_wrappers.so', $
   *                        'get_data_dimens', $
   *                        file_identifier, rank, dimens)
   *
   */

  hid_t *file_identifier = (hid_t *) argv[0];
  int   *rank            = (int *)   argv[1];
  int   *dimens          = (int *)   argv[2];

  hsize_t maximum_dims[10];
  hsize_t dataspace_dims[10];

  hid_t dataset, dataspace;

  int i;
 
  /* open the data array dataset */
  dataset = H5Dopen(*file_identifier, "data array");
  dataspace = H5Dget_space(dataset);

  /* get the dimensions of the dataspace */
  *rank = H5Sget_simple_extent_dims(dataspace, dataspace_dims, maximum_dims);

  for (i = 0; i < *rank; i++) {
    dimens[i] = dataspace_dims[i];
  }

  H5Dclose(dataset);
  H5Sclose(dataspace);

  return 0;
}




int read_data(int argc, char **argv) 
{
  hid_t  *file_identifier = (hid_t *)  argv[0];
  double *data            = (double *) argv[1];

  hid_t dataset, dataspace;
  
  int ierr;
  
  /* open the data array dataset */
  dataset = H5Dopen(*file_identifier, "data array");
  dataspace = H5Dget_space(dataset);

  /* read the data array */
  ierr = H5Dread(dataset, H5T_NATIVE_DOUBLE, H5S_ALL, dataspace, 
		 H5P_DEFAULT, data);

  H5Sclose(dataspace);
  H5Dclose(dataset);

  return 0;
}
