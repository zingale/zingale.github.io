pro read_data, filename

; allocate space for the file identifier -- note, it must be a 4-byte
; integer.
file_identifier = (lonarr(1))[0]

; open the file
ierr = call_external('hdf5_wrappers.so', $
		     'open_file', $
		     file_identifier, filename)

; note, IDL strings are funny -- you must allocate enough space in the
; string before passing the pointer to it to the wrapper function.
comment = 'comment                              '

ierr = call_external('hdf5_wrappers.so', $
                     'read_comment', $
                     file_identifier, comment)

print, comment

rank = (lonarr(1))[0]
dimens = lonarr(10)

ierr = call_external('hdf5_wrappers.so', $
                     'get_data_dimens', $
                     file_identifier, rank, dimens)

print, rank, dimens

if (rank EQ 2) then begin
    data = dblarr(dimens[0], dimens[1])
endif else begin
    print, 'ERROR: rank should be 2'
endelse

ierr = call_external('hdf5_wrappers.so', $
                     'read_data', $
                     file_identifier, data)

help, data
print, data

; close the HDF5 file
ierr = call_external('hdf5_wrappers.so', $
                     'close_file', $
                     file_identifier)




end
