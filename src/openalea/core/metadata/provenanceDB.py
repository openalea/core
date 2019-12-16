from sshtunnel import SSHTunnelForwarder
import pymongo
from pymongo.errors import ConnectionFailure
from sshtunnel import BaseSSHTunnelForwarderError
import json

from openalea.core.path import path



class ProvFile():
    def __init__(self, *args, **kwargs):
        self.localpath = ""

    def add_prov_item(self, item, *args, **kwargs):
        print "START WRITING"
        prov_path = path(self.localpath) / item["workflow"] + '.json'
        print self.localpath
        with open(prov_path, 'a+') as fp:
            json.dump(item, fp, indent=4)

    def init(self, *args, **kwargs):
        self.localpath = kwargs["path"]

    def close(self):
        pass


class ProvMongo():
    def __init__(self, *args, **kwargs):
        self.client = None
        self.server = None
        # self.provdb = None
        self.taskdb = None
        self.wfdb = None
        self.remote = False

    def __set__(self, instance, value):
        self.instance = value

    def is_in(self, task_id=None, wf_id=None):
        # check if in mongodb
        if task_id:
            if self.taskdb.find_one({"task_id": task_id}):
                return self.taskdb.find_one({"task_id": task_id})
            else:
                return False
        if wf_id:
            if self.wfdb.find_one({"workflow": wf_id}):
                return self.wfdb.find_one({"workflow": wf_id})
            else:
                return False
        else:
            return False

    def add_task_item(self, item, *args, **kwargs):
        # add element to index db
        self.taskdb.insert_one(item)

    def add_list_task_item(self, itemlist, *args, **kwargs):
        for item in itemlist:
            self.taskdb.insert_one(item)

    def add_wf_item(self, item, *args, **kwargs):
        # add element to index db
        self.wfdb.insert_one(item)

    def add_list_wf_item(self, itemlist, *args, **kwargs):
        for item in itemlist:
            self.wfdb.insert_one(item)

    def show(self, task_id=None, wf_id=None):
        print("the task provenance has : ", self.taskdb.count(), " entries :")
        for doc in self.taskdb.find({}):
            print(doc)

    def start_sshtunnel(self, *args, **kwargs):
        try:
            self.server = SSHTunnelForwarder(
                ssh_address_or_host=kwargs['ssh_ip_addr'],
                ssh_pkey=kwargs['ssh_pkey'],
                ssh_username=kwargs['ssh_username'],
                remote_bind_address=kwargs['remote_bind_address']
                # ,
                # *args,
                # **kwargs
            )

            self.server.start()
        except BaseSSHTunnelForwarderError:
            print "Fail to connect to ssh device"

    def start_client(self, *args, **kwargs):
        if self.remote:
            if not self.server:
                print "SSH Server not started - cannot connect to Mongo"
                return
            try:
                client = pymongo.MongoClient(host=kwargs['mongo_ip_addr'],
                                             port=self.server.local_bind_port
                                             # ,
                                             # , # server.local_bind_port is assigned local port
                                             # username='admin',
                                             # password='admin'
                                             # *args,
                                             # **kwargs
                                             )

                self.client = client
                db = self.client.provdb
                self.taskdb = db.task_collection
                self.wfdb = db.workflow_collection
            except ConnectionFailure:
                print "failed to connect to mongodb"
        else:
            try:
                client = pymongo.MongoClient(host=kwargs['mongo_ip_addr'],
                                             port=kwargs['mongo_port']
                                             # ,
                                             # , # server.local_bind_port is assigned local port
                                             # username='admin',
                                             # password='admin'
                                             # *args,
                                             # **kwargs
                                             )

                self.client = client
                db = self.client.provdb
                self.taskdb = db.task_collection
                self.wfdb = db.workflow_collection
            except ConnectionFailure:
                print "failed to connect to mongodb"

    def close_sshtunel(self):
        return self.server.stop()

    def close_client(self):
        return self.client.close()

    def remove_all_item(self):
        self.taskdb.drop()
        self.wfdb.drop()
        return 0

    def init(self, *args, **kwargs):
        if kwargs['remote']:
            self.remote=True
            self.start_sshtunnel(*args, **kwargs)
            self.start_client(*args, **kwargs)
        else:
            self.remote=False
            self.start_client(*args, **kwargs)

    def close(self):
        if self.remote:
            self.close_client()
            self.close_sshtunel()
        else:
            self.close_client()
