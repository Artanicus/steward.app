import time
from concurrent import futures
from absl import logging, flags, app

import grpc

from bson.objectid import ObjectId
from bson.json_util import dumps, loads

from registry import storage

from steward import user_pb2 as u
from steward import registry_pb2_grpc

FLAGS = flags.FLAGS
_ONE_DAY_IN_SECONDS = 60 * 60 * 24

flags.DEFINE_string('listen_addr', '[::]:50051', 'Address to listen.')

class UserServiceServicer(registry_pb2_grpc.UserServiceServicer):
    def __init__(self, argv=None):
        self.storage = storage.StorageManager()
        logging.info('UserService initialized.')

    def GetUser(self, request, context):
        user_id = request._id
        email = request.email
        if user_id:
            user_id = ObjectId(user_id) # str -> ObjectId
            data_bson = self.storage.users.find_one({'_id': user_id})
        elif email:
            data_bson = self.storage.users.find_one({'email': email})
        else:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('No search parameter provided, one available field should be set.')
            return u.User()

        if data_bson is None:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('User "{}" not found.'.format(request))
            return u.User()

        return self.storage.decode(data_bson, u.User)

    def CreateUser(self, request, context):
        # only create if user doesn't exist
        existing_user = self.storage.users.find_one({'email': request.email})
        if existing_user is None:
            user = u.User(name=request.name, email=request.email, password=request.password, available_effort=request.available_effort)
            result = self.storage.users.insert_one(self.storage.encode(user))
            return self.GetUser(u.GetUserRequest(_id=str(result.inserted_id)), context)
        else:
            context.set_code(grpc.StatusCode.ALREADY_EXISTS)
            context.set_details('User "{}" already exists.'.format(request.email))
            return u.User()

    def UpdateUser(self, request, context):
        user_id = request._id
        if user_id:
            user_id = ObjectId(user_id)
            # only update if user exists
            existing_user = self.storage.users.find_one({'_id': user_id})
            if existing_user is not None:
                logging.info('UpdateUser, before update in dict: {}'.format(existing_user))
                existing_user = self.storage.decode(existing_user, u.User)
                existing_user.MergeFrom(request.user)
                logging.info('UpdateUser, merged Proto: {}'.format(existing_user))
                result = self.storage.users.replace_one(
                        {'_id': user_id},
                        self.storage.encode(existing_user)
                        )
                return self.GetUser(u.GetUserRequest(_id=request._id), context)
            else:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details('User id "{}" does not exist.'.format(user_id))
                return u.User()
        else:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('_id is mandatory'.format(user_id))
            return u.User()

    def DeleteUser(self, request, context):
        user_id = request._id
        if not isinstance(user_id, ObjectId):
            user_id = ObjectId(user_id)

        # only delete if user exists and we need to return the deleted user anyway
        existing_user = self.storage.users.find_one({'_id': user_id})
        if existing_user is not None:
            result = self.storage.users.delete_one({'_id': user_id})
            del existing_user['_id'] # delete id to signify the user doesn't exist
            return self.storage.decode(existing_user, u.User)
        else:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('User id "{}" does not exist.'.format(user_id))
            return u.User()

    def ListUsers(self, request, context):
        for user_bson in self.storage.users.find():
            user = u.User()
            yield self.storage.decode(user_bson, u.User)

def serve(argv):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    registry_pb2_grpc.add_UserServiceServicer_to_server(UserServiceServicer(), server)
    server.add_insecure_port(FLAGS.listen_addr)
    server.start()

    try:
        while True:
                time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    app.run(serve)
