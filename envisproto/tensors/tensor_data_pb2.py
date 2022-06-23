# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: envisproto/tensors/tensor_data.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from envisproto.tensors import shape_pb2 as envisproto_dot_tensors_dot_shape__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='envisproto/tensors/tensor_data.proto',
  package='envisproto.tensors',
  syntax='proto3',
  serialized_options=_b('\n ai.nimbleedge.envisproto.tensors'),
  serialized_pb=_b('\n$envisproto/tensors/tensor_data.proto\x12\x12\x65nvisproto.tensors\x1a\x1e\x65nvisproto/tensors/shape.proto\"\xbf\x03\n\nTensorData\x12(\n\x05shape\x18\x01 \x01(\x0b\x32\x19.envisproto.tensors.Shape\x12\r\n\x05\x64type\x18\x02 \x01(\t\x12\x14\n\x0cis_quantized\x18\x03 \x01(\x08\x12\r\n\x05scale\x18\x04 \x01(\x02\x12\x12\n\nzero_point\x18\x05 \x01(\x05\x12\x16\n\x0e\x63ontents_uint8\x18\x10 \x03(\r\x12\x15\n\rcontents_int8\x18\x11 \x03(\x05\x12\x16\n\x0e\x63ontents_int16\x18\x12 \x03(\x05\x12\x16\n\x0e\x63ontents_int32\x18\x13 \x03(\x05\x12\x16\n\x0e\x63ontents_int64\x18\x14 \x03(\x03\x12\x18\n\x10\x63ontents_float16\x18\x15 \x03(\x02\x12\x18\n\x10\x63ontents_float32\x18\x16 \x03(\x02\x12\x18\n\x10\x63ontents_float64\x18\x17 \x03(\x01\x12\x15\n\rcontents_bool\x18\x18 \x03(\x08\x12\x16\n\x0e\x63ontents_qint8\x18\x19 \x03(\x11\x12\x17\n\x0f\x63ontents_quint8\x18\x1a \x03(\r\x12\x17\n\x0f\x63ontents_qint32\x18\x1b \x03(\x11\x12\x19\n\x11\x63ontents_bfloat16\x18\x1c \x03(\x02\x42\"\n ai.nimbleedge.envisproto.tensorsb\x06proto3')
  ,
  dependencies=[envisproto_dot_tensors_dot_shape__pb2.DESCRIPTOR,])




_TENSORDATA = _descriptor.Descriptor(
  name='TensorData',
  full_name='envisproto.tensors.TensorData',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='shape', full_name='envisproto.tensors.TensorData.shape', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='dtype', full_name='envisproto.tensors.TensorData.dtype', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='is_quantized', full_name='envisproto.tensors.TensorData.is_quantized', index=2,
      number=3, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='scale', full_name='envisproto.tensors.TensorData.scale', index=3,
      number=4, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='zero_point', full_name='envisproto.tensors.TensorData.zero_point', index=4,
      number=5, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='contents_uint8', full_name='envisproto.tensors.TensorData.contents_uint8', index=5,
      number=16, type=13, cpp_type=3, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='contents_int8', full_name='envisproto.tensors.TensorData.contents_int8', index=6,
      number=17, type=5, cpp_type=1, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='contents_int16', full_name='envisproto.tensors.TensorData.contents_int16', index=7,
      number=18, type=5, cpp_type=1, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='contents_int32', full_name='envisproto.tensors.TensorData.contents_int32', index=8,
      number=19, type=5, cpp_type=1, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='contents_int64', full_name='envisproto.tensors.TensorData.contents_int64', index=9,
      number=20, type=3, cpp_type=2, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='contents_float16', full_name='envisproto.tensors.TensorData.contents_float16', index=10,
      number=21, type=2, cpp_type=6, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='contents_float32', full_name='envisproto.tensors.TensorData.contents_float32', index=11,
      number=22, type=2, cpp_type=6, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='contents_float64', full_name='envisproto.tensors.TensorData.contents_float64', index=12,
      number=23, type=1, cpp_type=5, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='contents_bool', full_name='envisproto.tensors.TensorData.contents_bool', index=13,
      number=24, type=8, cpp_type=7, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='contents_qint8', full_name='envisproto.tensors.TensorData.contents_qint8', index=14,
      number=25, type=17, cpp_type=1, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='contents_quint8', full_name='envisproto.tensors.TensorData.contents_quint8', index=15,
      number=26, type=13, cpp_type=3, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='contents_qint32', full_name='envisproto.tensors.TensorData.contents_qint32', index=16,
      number=27, type=17, cpp_type=1, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='contents_bfloat16', full_name='envisproto.tensors.TensorData.contents_bfloat16', index=17,
      number=28, type=2, cpp_type=6, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=93,
  serialized_end=540,
)

_TENSORDATA.fields_by_name['shape'].message_type = envisproto_dot_tensors_dot_shape__pb2._SHAPE
DESCRIPTOR.message_types_by_name['TensorData'] = _TENSORDATA
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

TensorData = _reflection.GeneratedProtocolMessageType('TensorData', (_message.Message,), dict(
  DESCRIPTOR = _TENSORDATA,
  __module__ = 'envisproto.tensors.tensor_data_pb2'
  # @@protoc_insertion_point(class_scope:envisproto.tensors.TensorData)
  ))
_sym_db.RegisterMessage(TensorData)


DESCRIPTOR._options = None
# @@protoc_insertion_point(module_scope)