# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

from steward import registry_pb2 as steward_dot_registry__pb2
from steward import user_pb2 as steward_dot_user__pb2


class UserServiceStub(object):
  # missing associated documentation comment in .proto file
  pass

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.GetUser = channel.unary_unary(
        '/steward.UserService/GetUser',
        request_serializer=steward_dot_user__pb2.GetUserRequest.SerializeToString,
        response_deserializer=steward_dot_user__pb2.User.FromString,
        )
    self.CreateUser = channel.unary_unary(
        '/steward.UserService/CreateUser',
        request_serializer=steward_dot_user__pb2.CreateUserRequest.SerializeToString,
        response_deserializer=steward_dot_user__pb2.User.FromString,
        )
    self.ListUsers = channel.unary_stream(
        '/steward.UserService/ListUsers',
        request_serializer=steward_dot_registry__pb2.ListRequest.SerializeToString,
        response_deserializer=steward_dot_user__pb2.User.FromString,
        )


class UserServiceServicer(object):
  # missing associated documentation comment in .proto file
  pass

  def GetUser(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def CreateUser(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def ListUsers(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_UserServiceServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'GetUser': grpc.unary_unary_rpc_method_handler(
          servicer.GetUser,
          request_deserializer=steward_dot_user__pb2.GetUserRequest.FromString,
          response_serializer=steward_dot_user__pb2.User.SerializeToString,
      ),
      'CreateUser': grpc.unary_unary_rpc_method_handler(
          servicer.CreateUser,
          request_deserializer=steward_dot_user__pb2.CreateUserRequest.FromString,
          response_serializer=steward_dot_user__pb2.User.SerializeToString,
      ),
      'ListUsers': grpc.unary_stream_rpc_method_handler(
          servicer.ListUsers,
          request_deserializer=steward_dot_registry__pb2.ListRequest.FromString,
          response_serializer=steward_dot_user__pb2.User.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'steward.UserService', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))
