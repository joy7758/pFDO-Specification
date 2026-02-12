# Specification of the extended operations

## Op.Extended-Create

An operation to create a FAIR digital object within the DOIP service. The target of a creation operation is the DOIP service
itself.

### Request

* Request attributes:
    * record: A serialized object containing key value pairs, with a Profile Reference as minimal requirement attribute. All key value pairs that are specifid in the record attribute are directly entered into the FDO record.
    * dynamic_record: A serialized object given as list of key value pairs. The keys are directly written into the FDO record. The values used to dynamically generate new values that are written into the FDO record (see example below). 
* Input: a serialized digital object. The default serialization may be used if the object lacks element data; otherwise
  the serialization is a multi-segment DO serialization as described above. The "id" can be omitted to ask the DOIP
  service to automatically choose the id.

Here is an example for the `dynamic_record`:

```
"dynamic_record": {
  "21.T11966/1639bb8709dda583d357": "id_to_pid(file_id_1, ...)",
  "21.T11966/bb3f941a048bc3b2dd3f": "id_to_uri(file_id_2, ...)"
}
```

The functions `id_to_pid` and `id_to_url`are internal functions implemented by the DOIP service.
* `id_to_pid`: takes the `file_id` and builds a PID record that contains the file's storage location after the upload
* `id_to_uri`: takes the file_id and returns the file's storage location after the upload
Other functions may be implemented by the DOIP service to dynamically generate other relevant values that should be written into the FDO record.

### Response 

* Response attributes:
    * record: a serialized object which contains all attributes in the FDO record
* Output: the default serialization of the created object omitting element data. Notably, includes the identifier of the
  object (even if chosen by the client) and any changes to the object automatically performed by the DOIP service.

## Op.Extended-Update

### Request
TODO

### Response
TODO

## Op.Extended-Retrieve

### Request
TODO

### Response
TODO

## Op.Validate

The operation can be used to check whether a PID belongs to a valid FDO or not. The target of a validation operation is
the FDO PID. The operation may be performed by any DOIP service.

### Request

* Request attributes: none
* Input: none

### Response 

* Response attributes: none
* Output: a serialized object with properties
  * `valid`: the value is a boolean indicating whether the FDO is valid or not
  * `message`: optional message, e.g. to show validation errors to the client

## Op.Nanopub2Handle
 
The Nanopub2Handle operation is a concatenation of Extended-Retrieve invoked on the Nanopub FDO and an Extended-Create 
to build a Handle-based FDO out of the result from the Extended-Retrieve operation.

## Op.Extended-QueryFreeText
### Request
* Request attributes:
      * input: The text to be searched for.
  
### Response 

The response follows the specification of 0.DOIP_Op.Search-Response.json

## Op.QueryRef

### Request
* Request attributes:
      * input: The PID or URI to be searched for.
  
### Response 

The response follows the specification of 0.DOIP_Op.Search-Response.json
