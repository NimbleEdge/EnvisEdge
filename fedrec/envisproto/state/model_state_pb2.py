# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: envisproto/state/model_state.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from envisproto.state import state_tensor_pb2 as envisproto_dot_state_dot_state__tensor__pb2
from envisproto.state import placeholder_pb2 as envisproto_dot_state_dot_placeholder__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='envisproto/state/model_state.proto',
  package='envisproto.state',
  syntax='proto3',
  serialized_options=_b('\n\036ai.nimbleedge.envisproto.state'),
  serialized_pb=_b('\n\"envisproto/state/model_state.proto\x12\x10\x65nvisproto.state\x1a#envisproto/state/state_tensor.proto\x1a\"envisproto/state/placeholder.proto\"7\n\x05State\x12.\n\x07tensors\x18\x02 \x03(\x0b\x32\x1d.envisproto.state.StateTensorB \n\x1e\x61i.nimbleedge.envisproto.stateb\x06proto3')
  ,
  dependencies=[envisproto_dot_state_dot_state__tensor__pb2.DESCRIPTOR,envisproto_dot_state_dot_placeholder__pb2.DESCRIPTOR,])




_STATE = _descriptor.Descriptor(
  name='State',
  full_name='envisproto.state.State',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='tensors', full_name='envisproto.state.State.tensors', index=0,
      number=2, type=11, cpp_type=10, label=3,
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
  serialized_start=129,
  serialized_end=184,
)

_STATE.fields_by_name['tensors'].message_type = envisproto_dot_state_dot_state__tensor__pb2._STATETENSOR
DESCRIPTOR.message_types_by_name['State'] = _STATE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

State = _reflection.GeneratedProtocolMessageType('State', (_message.Message,), dict(
  DESCRIPTOR = _STATE,
  __module__ = 'envisproto.state.model_state_pb2'
  # @@protoc_insertion_point(class_scope:envisproto.state.State)
  ))
_sym_db.RegisterMessage(State)


DESCRIPTOR._options = None
# @@protoc_insertion_point(module_scope)
