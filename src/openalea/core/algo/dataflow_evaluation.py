# -*- python -*-
#
#       OpenAlea.Core
#
#       Copyright 2006-2009 INRIA - CIRAD - INRA
#
#       File author(): Jerome Chopard <jerome.chopard@sophia.inria.fr>
#                       Samuel Dufour-Kowalski <samuel.dufour@sophia.inria.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite: http://openalea.gforge.inria.fr
#
###############################################################################
"""This module provide an algorithm to evaluate a dataflow"""

__license__ = "Cecill-C"
__revision__ = " $Id$ "

import sys
from time import clock
import traceback as tb
from openalea.provenance.simple_dict import Provenance as RVProvenance

from openalea.core import ScriptLibrary
from openalea.core.dataflow import SubDataflow
from openalea.core.interface import IFunction

import os
import time
import json

from openalea.core.data_manager import load_data, check_data_to_load, write_data

from openalea.distributed.cloud_infos.paths import TMP_PATH, PROVENANCE_PATH
import openalea.core.metadata.cloud_info

from openalea.distributed.index.cacheIndex import IndexCassandra
from openalea.distributed.index.id import get_id


# This variable has to be retrieve by the settings
quantify = False
# get the prov when evaluating
provenance = False

__evaluators__ = []


class EvaluationException(Exception):
    def __init__(self, vid, node, exception, exc_info):
        Exception.__init__(self)
        self.vid = vid
        self.node = node
        self.exception = exception
        self.exc_info = exc_info


# Sort functions

# order function sort by priority


def cmp_priority(x, y):
    """todo"""
    (xvid, xactor) = x
    (yvid, yactor) = y
    px = xactor.internal_data.get('priority', 0)
    py = yactor.internal_data.get('priority', 0)

    # reverse order
    return cmp(py, px)


# order function to sort by pos x


def cmp_posx(x, y):
    """todo"""
    (xpid, xvid, xactor) = x
    (ypid, yvid, yactor) = y
    # px = xactor.internal_data.get('posx', 0)
    # py = yactor.internal_data.get('posx', 0)
    px = xactor.get_ad_hoc_dict().get_metadata('position')[0]
    py = yactor.get_ad_hoc_dict().get_metadata('position')[0]

    ret = cmp(px, py)
    if (not ret):
        ret = cmp(xpid, ypid)
    # reverse order
    return ret


# Evaluation Algoithm

""" Abstract evaluation algorithm """


class AbstractEvaluation(object):
    def __init__(self, dataflow, record_provenance=False):
        """
        :param dataflow: to be done
        """
        self._dataflow = dataflow

        if record_provenance:
            self._prov = RVProvenance()
            self._provdb = ProvMongo()
        else:
            self._prov = None
            self._provdb = None


    def eval(self, *args):
        """todo"""
        raise NotImplementedError()

    def is_stopped(self, vid, actor):
        """ Return True if evaluation must be stop at this vertex. """
        return actor.block

    def eval_vertex_code(self, vid, *args, **kwargs):
        """
        Evaluate the vertex vid.
        Can raise an exception if evaluation failed.
        """

        node = self._dataflow.actor(vid)

        try:

            if self._prov is not None:
                self._prov.before_eval(self._dataflow, vid)

            t0 = clock()
            ret = node.eval()
            t1 = clock()

            if self._prov is not None:
                taskitem = self._prov.after_eval(self._dataflow, vid, dt)
                if self._provdb and taskitem:
                    self._provdb.add_task_item(taskitem)
                # print self._prov.as_wlformat()


            # When an exception is raised, a flag is set.
            # So we remove it when evaluation is ok.
            node.raise_exception = False
            # if hasattr(node, 'raise_exception'):
            #     del node.raise_exception
            node.notify_listeners(('data_modified', None, None))
            return ret

        except EvaluationException, e:
            e.vid = vid
            e.node = node
            # When an exception is raised, a flag is set.
            node.raise_exception = True
            node.notify_listeners(('data_modified', None, None))
            raise e

        except Exception, e:
            # When an exception is raised, a flag is set.
            node.raise_exception = True
            node.notify_listeners(('data_modified', None, None))
            raise EvaluationException(vid, node, e, \
                                      tb.format_tb(sys.exc_info()[2]))

    def get_parent_nodes(self, pid):
        """
        Return the list of parent node connected to pid
        The list contains tuples (port_pid, node_pid, actor)
        This list is sorted by the x value of the node
        """

        df = self._dataflow

        # For each connected node
        npids = [(npid, df.vertex(npid), df.actor(df.vertex(npid))) \
                 for npid in df.connected_ports(pid)]
        npids.sort(cmp=cmp_posx)

        return npids

    def set_provenance(self, provenance):
        self.provenance = provenance


class BrutEvaluation(AbstractEvaluation):
    """ Basic evaluation algorithm """
    __evaluators__.append("BrutEvaluation")

    def __init__(self, dataflow, record_provenance=False, *args, **kwargs):

        AbstractEvaluation.__init__(self, dataflow, record_provenance)
        # a property to specify if the node has already been evaluated
        self._evaluated = set()

    def is_stopped(self, vid, actor):
        """ Return True if evaluation must be stop at this vertex """

        if vid in self._evaluated:
            return True

        try:
            if actor.block:
                status = True
                n = actor.get_nb_output()
                outputs = [i for i in range(n) if
                           actor.get_output(i) is not None]
                if not outputs:
                    status = False
                return status
        except:
            pass
        return False

    def eval_vertex(self, vid, *args, **kwargs):
        """ Evaluate the vertex vid """

        df = self._dataflow
        actor = df.actor(vid)

        self._evaluated.add(vid)

        # For each inputs
        for pid in df.in_ports(vid):
            inputs = []

            cpt = 0
            # For each connected node
            for npid, nvid, nactor in self.get_parent_nodes(pid):
                if not self.is_stopped(nvid, nactor):
                    self.eval_vertex(nvid)

                inputs.append(nactor.get_output(df.local_id(npid)))
                cpt += 1

            # set input as a list or a simple value
            if (cpt == 1):
                inputs = inputs[0]
            if (cpt > 0):
                actor.set_input(df.local_id(pid), inputs)

        # Eval the node
        self.eval_vertex_code(vid)

    def eval(self, *args, **kwargs):
        """ Evaluate the whole dataflow starting from leaves"""

        t0 = time.time()
        df = self._dataflow

        if self._prov is not None:
            self._prov.init(df)
            self._prov.time_init = t0

        if self._provdb is not None:
            self._provdb.init(
                            remote=cloud_info.REMOTE,
                            path=cloud_info.FILEPATH,
                            ssh_ip_addr=cloud_info.PROVDB_SSH_ADDR,
                            ssh_pkey=cloud_info.SSH_PKEY,
                            ssh_username=cloud_info.SSU_USERNAME,
                            remote_bind_address=(cloud_info.MONGO_ADDR, cloud_info.MONGO_PORT),
                            mongo_ip_addr=cloud_info.MONGO_ADDR,
                            mongo_port=cloud_info.MONGO_PORT
                             )


        # Unvalidate all the nodes
        self._evaluated.clear()

        # Eval from the leaf
        for vid in (vid for vid in df.vertices() if df.nb_out_edges(vid) == 0):
            self.eval_vertex(vid)

        t1 = time.time()

        if self._prov is not None:
            self._prov.time_end = t1
            wfitem = self._prov.as_wlformat()
        if self._provdb is not None:
            self._provdb.add_wf_item(wfitem)
            # self._provdb.add_list_task_item(taskitemslist)

            # close remote connections
            self._provdb.close()

            # Save the provenance in a file
            # wf_id = str(df.factory.uid) + ".json"
            # home = os.path.expanduser("~")
            # provenance_path = os.path.join(home, ".openalea/provenance", wf_id)
            # if not os.path.exists(os.path.dirname(provenance_path)):
            #     os.makedirs(provenance_path)
            # provenance = self._prov.as_wlformat()
            # with open(provenance_path, "a+") as f:
            #     json.dump(provenance, f, indent=4)

        if quantify:
            print "Evaluation time: %s" % (t1 - t0)


class PriorityEvaluation(BrutEvaluation):
    """ Support priority between nodes and selective"""
    __evaluators__.append("PriorityEvaluation")

    def eval(self, vtx_id=None, *args, **kwds):
        """todo"""
        t0 = clock()

        is_subdataflow = False if not kwds else kwds.get('is_subdataflow',
                                                         False)
        df = self._dataflow
        # Unvalidate all the nodes
        if is_subdataflow:
            self._evaluated -= self._resolution_node
        else:
            self._evaluated.clear()

        if (vtx_id is not None):
            return self.eval_vertex(vtx_id, *args)

        # Select the leaves (list of (vid, actor))
        leaves = [(vid, df.actor(vid))
                  for vid in df.vertices() if df.nb_out_edges(vid) == 0]

        leaves.sort(cmp_priority)

        # Excecute
        for vid, actor in leaves:
            self.eval_vertex(vid, *args)

        t1 = clock()
        if quantify:
            print "Evaluation time: %s" % (t1 - t0)


class GeneratorEvaluation(AbstractEvaluation):
    """ Evaluation algorithm with generator / priority and selection"""
    __evaluators__.append("GeneratorEvaluation")

    def __init__(self, dataflow, record_provenance=False):

        AbstractEvaluation.__init__(self, dataflow, record_provenance)
        # a property to specify if the node has already been evaluated
        self._evaluated = set()
        self.reeval = False  # Flag to force reevaluation (for generator)

    def is_stopped(self, vid, actor):
        """ Return True if evaluation must be stop at this vertex """
        stopped = False
        try:
            stopped = actor.block or vid in self._evaluated
        except:
            pass
        return stopped

    def clear(self):
        """ Clear evaluation variable """
        self._evaluated.clear()
        self.reeval = False

    def eval_vertex(self, vid):
        """ Evaluate the vertex vid """

        df = self._dataflow
        actor = df.actor(vid)

        self._evaluated.add(vid)

        # For each inputs
        for pid in df.in_ports(vid):
            inputs = []

            cpt = 0
            # For each connected node
            for npid, nvid, nactor in self.get_parent_nodes(pid):
                # Do no reevaluate the same node
                if not self.is_stopped(nvid, nactor):
                    self.eval_vertex(nvid)

                inputs.append(nactor.get_output(df.local_id(npid)))
                cpt += 1

            # set input as a list or a simple value
            if (cpt == 1):
                inputs = inputs[0]
            if (cpt > 0):
                actor.set_input(df.local_id(pid), inputs)

        # Eval the node
        ret = self.eval_vertex_code(vid)

        # Reevaluation flag
        if (ret):
            self.reeval = ret

    def eval(self, vtx_id=None, step=False):
        t0 = clock()

        df = self._dataflow

        if (vtx_id is not None):
            leafs = [(vtx_id, df.actor(vtx_id))]

        else:
            # Select the leafs (list of (vid, actor))
            leafs = [(vid, df.actor(vid))
                     for vid in df.vertices() if df.nb_out_edges(vid) == 0]

        leafs.sort(cmp_priority)

        # Execute
        for vid, actor in leafs:
            if not self.is_stopped(vid, actor):
                self.reeval = True
                while (self.reeval):
                    self.clear()
                    self.eval_vertex(vid)

        t1 = clock()
        if quantify:
            print "Evaluation time: %s" % (t1 - t0)
        return False


class LambdaEvaluation(PriorityEvaluation):
    """ Evaluation algorithm with support of lambda / priority and selection"""
    __evaluators__.append("LambdaEvaluation")

    def __init__(self, dataflow, record_provenance=False):
        PriorityEvaluation.__init__(self, dataflow, record_provenance)

        self.lambda_value = {}  # lambda resolution dictionary
        self._resolution_node = set()

    def eval_vertex(self, vid, context, lambda_value, *args):
        """
        Evaluate the vertex vid

        This function is called both by the user (eval a node and its parents)
        and by the SubDataFlow evaluation.

        First the graph is traversed by the algorithm in a bottom-up way.
        The SubDataflow is stored in the inputs.


        :param context: is a list a value to assign to lambdas

        """

        df = self._dataflow
        actor = df.actor(vid)

        # Do not evaluate a node which is blocked
        if self.is_stopped(vid, actor):
            return

        self._evaluated.add(vid)

        use_lambda = False

        # For each inputs
        for pid in df.in_ports(vid):

            input_index = df.local_id(pid)
            inputs = []

            # Get input interface
            interface = actor.input_desc[input_index].get('interface', None)

            # Determine if the context must be transmitted
            # If interface is IFunction it means that the node is a consumer
            # We do not propagate the context
            if (interface is IFunction):
                transmit_cxt = None
                transmit_lambda = None
            else:
                transmit_cxt = context
                transmit_lambda = lambda_value

            cpt = 0  # parent counter

            # For each connected node
            for npid, nvid, nactor in self.get_parent_nodes(pid):

                # Do no reevaluate the same node
                if not self.is_stopped(nvid, nactor):
                    self.eval_vertex(nvid, transmit_cxt, transmit_lambda)

                outval = nactor.get_output(df.local_id(npid))
                # Lambda

                # We must consider 3 cases
                #  1) Lambda detection (receive a SubDataflow and
                # interface != IFunction)
                #
                #  2) Resolution mode (context is not None): we
                #      replace the lambda with value.

                if (isinstance(outval, SubDataflow)
                    and interface is not IFunction):

                    if (not context and not lambda_value):
                        # we are not in resolution mode
                        use_lambda = True
                        self._resolution_node.add(vid)
                    else:
                        # We set the context value for later use.
                        # We set resolved values into the dataflow.
                        # outval is a SubDataFlow. For this object, we have
                        # now a value.
                        # E.g. f(x=3). We replace x subdf by 3.
                        # If x is used elsewhere (f(x,x)), we referenced it
                        # in a dict.
                        if (not lambda_value.has_key(outval)):
                            try:
                                lambda_value[outval] = context.pop()
                            except Exception:
                                raise Exception(
                                    "The number of lambda variables is insuffisant")

                        # We replace the value with a context value
                        outval = lambda_value[outval]

                inputs.append(outval)
                cpt += 1

            # set input as a list or a simple value
            if (cpt == 1):
                inputs = inputs[0]
            if (cpt > 0):
                actor.set_input(input_index, inputs)

        # Eval the node
        if (not use_lambda):
            ret = self.eval_vertex_code(vid)

        else:
            # set the node output with subdataflow
            for i in xrange(actor.get_nb_output()):
                actor.set_output(i, SubDataflow(df, self, vid, i))

    def eval(self, vtx_id=None, context=None, is_subdataflow=False, step=False):
        """
        Eval the dataflow from vtx_id with a particular context

        :param vtx_id: vertex id to start the evaluation
        :param context: list a value to assign to lambda variables
        """
        t0 = clock()
        if self._prov is not None:
            self._prov.init(self._dataflow)
            self._prov.time_init = t0

        # if PROVENANCE and (not is_subdataflow):
        #     self.provenance.workflow_exec()
        #     self.provenance.start_time()

        self.lambda_value.clear()

        if (context):
            # The evaluate, due to the recursion, is done fisrt in last out.
            # thus, we have to reverse the arguments to evaluate the function (FIFO).
            context.reverse()

        PriorityEvaluation.eval(self, vtx_id, context, self.lambda_value,
                                is_subdataflow=is_subdataflow)
        self.lambda_value.clear()  # do not keep context in memory

        # if PROVENANCE:
        #     self.provenance.end_time()

        t1 = clock()
        if self._prov is not None:
            self._prov.time_end = t1

        if quantify:
            print "Evaluation time: %s" % (t1 - t0)

        if not is_subdataflow:
            self._resolution_node.clear()


DefaultEvaluation = LambdaEvaluation


# DefaultEvaluation = GeneratorEvaluation


# from collections import deque


# class LambdaEvaluation (PriorityEvaluation):
# 	""" Evaluation algorithm with support of lambda / priority and selection"""

# 	def __init__ (self, dataflow):

# 		PriorityEvaluation.__init__(self, dataflow)


#         def scan_graph(self, vid, context):
#             """ Return the list of vextex id in the correct process order
#             starting from vid
#             @param vid: starting vertex id
#             @param context: variable context
#             """

#             df = self._dataflow

#             process_list = deque()
#             scan_list = deque([(vid, context)])

#             while(scan_list):

#                 (vid, context) = scan_list.popleft()
#                 process_list.appendleft((vid, context) )
#                 actor = df.actor(vid)

#                 # For each inputs
#                 for pid in df.in_ports(vid):

#                     # Determine if the context must be transmitted
#                     # If interface is IFunction it means that the node is a consumer
#                     # We do not propagate the context
#                     input_index = df.local_id(pid)
#                     interface = actor.input_desc[input_index].get('interface', None)
#                     transmit_cxt = None if (interface is IFunction) else context

#                     # For each connected node
#                     for npid in df.connected_ports(pid):
#                         nvid = df.vertex(npid)
#                         scan_list.append((nvid,  transmit_cxt))

#             return process_list



# 	def eval_vertex (self, vid, context, *args):
# 		""" Evaluate the graph starting at the vertex vid
#                 @param vid: starting vertex id
#                 @param context  list of values to assign to variables
#                 """

#                 lambda_value = {}

#                 # Get the node order
#                 process_list = self.scan_graph(vid, context)

#                 # Eval each node
#                 scanned = set()

#                 for vid, context in process_list:
#                     if (vid not in scanned):
#                         self.eval_one_vertex(vid, context, lambda_value)
#                     scanned.add(vid)


#         def get_output_value(self, nvid, nactor, npid):
#             """ Return the value of a node output """

#             return nactor.get_output(self._dataflow.local_id(npid))



#         def eval_one_vertex (self, vid, context, lambda_value):
# 		""" Evaluate only one vertex
#                 @param vid: id of vertex to evalaute
#                 @param context: list of values to assign to variables
#                 @param lambda_value: dictionary of previous assigned values
#                 """

#                 df = self._dataflow

#                 actor = df.actor(vid)
#                 use_lambda = False

#                 # Get inputs
#                 for pid in df.in_ports(vid):

#                     inputs = []
#                     cpt = 0 # parent counter

#                     # Get input interface
#                     input_index = df.local_id(pid)
#                     interface = actor.input_desc[input_index].get('interface', None)

#                     # For each connected node
#                     for npid, nvid, nactor in self.get_parent_nodes(pid):

#                         outval = self.get_output_value(nvid, nactor, npid)

#                         # Lambda

#                         # We must consider 2 cases
#                         #  1) Lambda detection (receive a SubDataflow and interface != IFunction)
#                         #
#                         #  2) Resolution mode (context is not None): we
#                         #      replace the lambda with value

#                         if (isinstance(outval, SubDataflow)
#                            and interface is not IFunction):

#                             if (not context and not lambda_value):
#                                 # we are not in resolution mode
#                                 use_lambda = True
#                             else:
#                                 # We set the context value for later use
#                                 if (not lambda_value.has_key(outval)):
#                                     try:
#                                         lambda_value[outval] = context.pop()
#                                     except Exception,e:
#                                         print e, context, lambda_value
#                                         raise Exception("The number of lambda variables is insuffisant")

#                                 # We replace the value with a context value
#                                 outval = lambda_value[outval]


#                         inputs.append(outval)
#                         cpt += 1

#                     # set input as a list or a simple value
#                     if (cpt == 1): inputs = inputs[0]
#                     if (cpt > 0): actor.set_input(input_index, inputs)


#                 # Eval the node
#                 if (not use_lambda):
#                     ret = self.eval_vertex_code(vid)
#                 else:
#                     # tranmit a SubDataflow to following node
#                     for i in xrange(actor.get_nb_output()):
#                         actor.outputs[i] = SubDataflow(df, self, vid, i)



#         def eval (self, vtx_id=None, context=None):
#             """
#             Eval the dataflow from vtx_id with a particular context
#             @param vtx_id: vertex id to start the evaluation
#             @param context: list a value to assign to lambda variables
#             """

#             PriorityEvaluation.eval(self, vtx_id, context)



# from openalea.core.threadmanager import ThreadManager
# import thread

# class ParallelEvaluation(LambdaEvaluation):
#     """ Parallel execution of a dataflow """


#     def get_output_value(self, nvid, nactor, npid):
#             """ Return the value of a node output """

#             l = self.locks[nvid]

#             l.acquire()
#             v = nactor.get_output(self._dataflow.local_id(npid))
#             l.release()

#             return v


#     def eval_one_vertex (self, vid, context, lambda_value):
#         """ Evaluate only one vertex
#         @param vid: id of vertex to evalaute
#         @param context: list of values to assign to variables
#         @param lambda_value: dictionary of previous assigned values
#         """
#         LambdaEvaluation.eval_one_vertex(self, vid, context, lambda_value)
#         self.locks[vid].release()



#     def eval_vertex (self, vid, context, *args):
#         """ Evaluate the graph starting at the vertex vid
#         @param vid: starting vertex id
#         @param context list of values to assign to variables
#         """

#         lambda_value = {}

#         tm = ThreadManager()
#         tm.clear()

#         # Get the node order
#         process_list = self.scan_graph(vid, context)

#         # Synchronisation locks
#         self.locks = {}

#         for vid, context in process_list:

#             if (self.locks.has_key(vid)): continue
#             l = thread.allocate_lock()
#             l.acquire()
#             self.locks[vid] = l


#         # Eval each node
#         scanned = set()

#         for vid, context in process_list:
#             if (vid not in scanned):
#                 tm.add_task( self.eval_one_vertex, (vid, context, lambda_value))
#             scanned.add(vid)



# DefaultEvaluation = ParallelEvaluation
# #DefaultEvaluation = LambdaEvaluation
class ToScriptEvaluation(AbstractEvaluation):
    """ Basic transformation into script algorithm """
    __evaluators__.append("ToScriptEvaluation")

    def __init__(self, dataflow):

        AbstractEvaluation.__init__(self, dataflow)
        # a property to specify if the node has already been evaluated
        self._evaluated = set()

    def is_stopped(self, vid, actor):
        """ Return True if evaluation must be stop at this vertex """
        return actor.block or vid in self._evaluated

    def eval_vertex(self, vid, *args):
        """ Evaluate the vertex vid """

        df = self._dataflow
        actor = df.actor(vid)

        self._evaluated.add(vid)

        script = ""
        # For each inputs
        for pid in df.in_ports(vid):
            # For each connected node
            for npid, nvid, nactor in self.get_parent_nodes(pid):
                if not self.is_stopped(nvid, nactor):
                    script += self.eval_vertex(nvid)

        # Eval the node
        script += actor.to_script()

        return script

    def eval(self, *args, **kwds):
        """ Evaluate the whole dataflow starting from leaves"""
        df = self._dataflow

        # Unvalidate all the nodes
        self._evaluated.clear()
        ScriptLibrary().clear()

        # Eval from the leaf
        script = ""
        for vid in (vid for vid in df.vertices() if df.nb_out_edges(vid) == 0):
            script += self.eval_vertex(vid)

        return script


############################################################################
# Evaluation with scheduling

# The objective is to take

class DiscreteTimeEvaluation(AbstractEvaluation):
    """ Evaluation algorithm with generator / priority and selection"""
    __evaluators__.append("DiscreteTimeEvaluation")

    def __init__(self, dataflow):

        AbstractEvaluation.__init__(self, dataflow)
        # a property to specify if the node has already been evaluated
        self._evaluated = set()
        self.reeval = False  # Flag to force reevaluation (for generator)

        # CPL
        # At each evaluation of the dataflow, increase the current cycle of
        # one unit.

        self._current_cycle = 0
        # timed nodes are a dict with vid, time >0
        # when time is 0, remove the node from the dict
        self._timed_nodes = dict()
        self._stop = False
        self._nodes_to_reset = []

    def is_stopped(self, vid, actor):
        """ Return True if evaluation must be stop at this vertex """
        stopped = False
        try:
            if hasattr(actor, 'block'):
                stopped = actor.block
            stopped = stopped or vid in self._evaluated
        except:
            pass

        return stopped

    def clear(self):
        """ Clear evaluation variable """
        self._evaluated.clear()
        self.reeval = False
        self._stop = False
        self._nodes_to_reset = []

    def next_step(self):
        """ Update the scheduler of one step. """
        self._current_cycle += 1
        for vid in self._timed_nodes:
            self._timed_nodes[vid] -= 1

    def eval_vertex(self, vid):
        """ Evaluate the vertex vid """

        # print "Step ", self._current_cycle

        df = self._dataflow
        actor = df.actor(vid)

        self._evaluated.add(vid)

        # For each inputs
        # Compute the inputs of the node
        for pid in df.in_ports(vid):
            inputs = []

            cpt = 0
            # For each connected node
            for npid, nvid, nactor in self.get_parent_nodes(pid):
                # Do no reevaluate the same node
                if not self.is_stopped(nvid, nactor):
                    self.eval_vertex(nvid)

                inputs.append(nactor.get_output(df.local_id(npid)))
                cpt += 1

            # set input as a list or a simple value
            if (cpt == 1):
                inputs = inputs[0]
            if (cpt > 0):
                actor.set_input(df.local_id(pid), inputs)

        # Eval the node
        delay = 0
        # When a node return no delay, we stopped the simulation
        stop_when_finished = False

        if vid in self._timed_nodes:
            delay = self._timed_nodes[vid]
            if delay == 0:
                del self._timed_nodes[vid]
                stop_when_finished = True

        if delay == 0:
            delay = self.eval_vertex_code(vid)

        # Reevaluation flag
        # TODO: Add the node to the scheduler rather to execute
        if (delay):
            self._timed_nodes[vid] = int(delay)
            self.reeval = delay
        elif stop_when_finished:
            self._stop = True
            self._nodes_to_reset.append(vid)
        elif self._current_cycle > 1000:
            self._stop = True

    def eval(self, vtx_id=None, step=False):
        t0 = clock()

        self.clear()

        df = self._dataflow

        if (vtx_id is not None):
            leafs = [(vtx_id, df.actor(vtx_id))]

        else:
            # Select the leafs (list of (vid, actor))
            leafs = [(vid, df.actor(vid))
                     for vid in df.vertices() if df.nb_out_edges(vid) == 0]

        leafs.sort(cmp_priority)

        # Execute
        for vid, actor in leafs:
            if not self.is_stopped(vid, actor):
                self.reeval = True
                if not step:
                    while (self.reeval and not self._stop):
                        self.clear()
                        self.eval_vertex(vid)
                        self.next_step()
                elif (self.reeval and not self._stop):
                    self.clear()
                    self.eval_vertex(vid)
                    self.next_step()

        if self._stop:
            self._nodes_to_reset.extend(self._timed_nodes)
            for vid in self._nodes_to_reset:
                df.actor(vid).reset()

        # print 'Run %d times the dataflow'%(self._current_cycle,)

        # Reset the state
        if not step:
            self.clear()
            self._current_cycle = 0

        t1 = clock()
        if quantify:
            print "Evaluation time: %s" % (t1 - t0)

        return False


###############################################################################
class SciFlowareEvaluation(AbstractEvaluation):
    """ Distributed Evaluation algorithm with SciFloware backend"""
    __evaluators__.append("SciFlowareEvaluation")

    def __init__(self, dataflow):

        AbstractEvaluation.__init__(self, dataflow)

        # a property to specify if the node has already been evaluated
        self._evaluated = set()

        self._scifloware_actors = set()

    @staticmethod
    def is_operator(actor):
        from openalea.scifloware.operator import algebra
        factory = actor.factory
        if factory is None:
            return False
        if 'SciFloware' not in factory.package.name:
            return False
        elif factory.name in algebra:
            return True
        else:
            return False

    def scifloware_actors(self):
        """ Compute the scifloware actors.

        Only those actors will be evaluated.
        """

        df = self._dataflow
        self._scifloware_actors.clear()
        for vid in df.vertices():
            actor = df.actor(vid)
            if self.is_operator(actor):
                self._scifloware_actors.add(vid)

    def eval_vertex(self, vid):
        """ Evaluate the vertex vid 

        This evaluation is both a kind of compilation and real evaluation.
        Algorithm
        ---------
        For each vertex which is a SciFloware operator (e.g. map, reduce, ...),
            - select the vertices connected to each input port
            - if the name of the port is Dataflow:
                - get its name and send it as input to the operator
            - else
                - normal evaluation 

        """

        # print "Step ", self._current_cycle

        df = self._dataflow
        actor = df.actor(vid)

        is_op = vid in self._scifloware_actors
        self._evaluated.add(vid)

        # assert self.is_operator(actor)

        # For each inputs
        # Compute the nodes
        for pid in df.in_ports(vid):
            inputs = []

            is_dataflow = False
            if is_op:
                name = actor.get_input_port(df.local_id(pid))['name']
                if name.lower() == 'dataflow':
                    is_dataflow = True

            if is_dataflow:
                out_ports = list(df.connected_ports(pid))
                nb_out = len(out_ports)
                if nb_out > 1:
                    raise Exception(
                        'Too many nodes connected to the SciFloware operator.')
                elif nb_out == 1:
                    out_actor = df.actor(df.vertex(out_ports[0]))
                    dataflow_name = out_actor.factory.package.name + ':' + out_actor.factory.name
                    actor.set_input(df.local_id(pid), dataflow_name)
            else:
                cpt = 0
                # For each connected node
                for npid, nvid, nactor in self.get_parent_nodes(pid):
                    # Do no reevaluate the same node


                    if not self.is_stopped(nvid, nactor):
                        self.eval_vertex(nvid)

                    inputs.append(nactor.get_output(df.local_id(npid)))
                    cpt += 1

                # set input as a list or a simple value
                if (cpt == 1):
                    inputs = inputs[0]
                if (cpt > 0):
                    actor.set_input(df.local_id(pid), inputs)

        self.eval_vertex_code(vid)

    def eval(self, vtx_id=None, **kwds):
        t0 = clock()

        df = self._dataflow
        self.scifloware_actors()

        if (vtx_id is not None):
            leafs = [(vtx_id, df.actor(vtx_id))]
        else:
            # Select the leafs (list of (vid, actor))
            leafs = [(vid, df.actor(vid))
                     for vid in df.vertices() if df.nb_out_edges(vid) == 0]

        leafs.sort(cmp_priority)

        # Execute
        for vid, actor in leafs:
            self.eval_vertex(vid)

        t1 = clock()
        if quantify:
            print "Evaluation time: %s" % (t1 - t0)

        return False


############################################################
class TestEvaluation(AbstractEvaluation):
    """ Basic evaluation algorithm with provenance capture in file """
    __evaluators__.append("TestEvaluation")

    def __init__(self, dataflow, record_provenance=False, *args, **kwargs):

        AbstractEvaluation.__init__(self, dataflow, record_provenance)
        # a property to specify if the node has already been evaluated
        self._evaluated = set()

    def is_stopped(self, vid, actor):
        """ Return True if evaluation must be stop at this vertex """

        if vid in self._evaluated:
            return True

        try:
            if actor.block:
                status = True
                n = actor.get_nb_output()
                outputs = [i for i in range(n) if
                           actor.get_output(i) is not None]
                if not outputs:
                    status = False
                return status
        except:
            pass
        return False

    def eval_vertex(self, vid, *args, **kwargs):
        """ Evaluate the vertex vid """

        df = self._dataflow
        actor = df.actor(vid)

        self._evaluated.add(vid)

        # For each inputs
        for pid in df.in_ports(vid):
            inputs = []

            cpt = 0
            # For each connected node
            for npid, nvid, nactor in self.get_parent_nodes(pid):
                if not self.is_stopped(nvid, nactor):
                    self.eval_vertex(nvid)

                inputs.append(nactor.get_output(df.local_id(npid)))
                cpt += 1

            # set input as a list or a simple value
            if (cpt == 1):
                inputs = inputs[0]
            if (cpt > 0):
                actor.set_input(df.local_id(pid), inputs)

        # Eval the node
        self.eval_vertex_code(vid)

    def eval(self, *args, **kwargs):
        """ Evaluate the whole dataflow starting from leaves"""

        t0 = time.time()
        df = self._dataflow

        if self._prov is not None:
            self._prov.init(df)
            self._prov.time_init = t0


        # Unvalidate all the nodes
        self._evaluated.clear()
        
        # Eval from the leaf
        for vid in (vid for vid in df.vertices() if df.nb_out_edges(vid) == 0):
            self.eval_vertex(vid)

        t1 = time.time()

        if self._prov is not None:
            self._prov.time_end = t1
            # Save the provenance in a file
            wf_id = str(df.factory.uid) + ".json"
            home = os.path.expanduser("~")
            provenance_path = os.path.join(home, ".openalea/provenance", wf_id)
            if not os.path.exists(os.path.dirname(provenance_path)):
                os.makedirs(provenance_path)
            provenance = self._prov.as_wlformat()
            with open(provenance_path, "a+") as f:
                json.dump(provenance, f, indent=4)

        if quantify:
            print "Evaluation time: %s" % (t1 - t0)


class ZMQEvaluation(AbstractEvaluation):
    """ Basic evaluation algorithm """
    __evaluators__.append("ZMQEvaluation")

    def __init__(self, dataflow, record_provenance=False, *args, **kwargs):

        AbstractEvaluation.__init__(self, dataflow, record_provenance)
        # a property to specify if the node has already been evaluated
        self._evaluated = set()
        self.socket=None

    def is_stopped(self, vid, actor):
        """ Return True if evaluation must be stop at this vertex """

        if vid in self._evaluated:
            return True

        try:
            if actor.block:
                status = True
                n = actor.get_nb_output()
                outputs = [i for i in range(n) if
                           actor.get_output(i) is not None]
                if not outputs:
                    status = False
                return status
        except:
            pass
        return False

    def eval_vertex(self, vid, *args, **kwargs):
        """ Evaluate the vertex vid """

        df = self._dataflow
        actor = df.actor(vid)

        self._evaluated.add(vid)

        # For each inputs
        for pid in df.in_ports(vid):
            inputs = []

            cpt = 0
            # For each connected node
            for npid, nvid, nactor in self.get_parent_nodes(pid):
                if not self.is_stopped(nvid, nactor):
                    self.eval_vertex(nvid)

                inputs.append(nactor.get_output(df.local_id(npid)))
                cpt += 1

            # set input as a list or a simple value
            if (cpt == 1):
                inputs = inputs[0]
            if (cpt > 0):
                actor.set_input(df.local_id(pid), inputs)

        # Get the best worker
        # TODO
        worker_id = 0

        # Eval the node
        self.eval_vertex_code(vid, worker_id)

    def eval(self, *args, **kwargs):
        """ Evaluate the whole dataflow starting from leaves"""

        # Init the provenance
        t0 = clock()
        df = self._dataflow
        if self._prov is not None:
            self._prov.init(df)
            self._prov.time_init = t0

            self._provdb.init(
                            remote=cloud_info.REMOTE,
                            path=cloud_info.FILEPATH,
                            ssh_ip_addr=cloud_info.PROVDB_SSH_ADDR,
                            ssh_pkey=cloud_info.SSH_PKEY,
                            ssh_username=cloud_info.SSU_USERNAME,
                            remote_bind_address=(cloud_info.MONGO_ADDR, cloud_info.MONGO_PORT),
                            mongo_ip_addr=cloud_info.MONGO_ADDR,
                            mongo_port=cloud_info.MONGO_PORT
                             )
        # Init the workers
        # context = zmq.Context()
        # socket = context.socket(zmq.REQ)
        # socket.connect("tcp://localhost:5559")
        # self.socket = socket
        # TODO: FIND A WAY TO INIT WF ON ALL WORKER - for now the worker are started by hand
        # msg=dict()
        # msg['pkg_name'] = self._dataflow.get_factory().package.name
        # msg['wf_name'] = self._dataflow.get_factory().name
        # socket.send(json.dumps(msg))
        # state=socket.recv()
        # state=json.loads(state)
        # if not state['Initialization']=="success":
        #     print "Eval failed due to failed init workers"
        #     return

        # Unvalidate all the nodes
        self._evaluated.clear()

        # Eval from the leaf
        for vid in (vid for vid in df.vertices() if df.nb_out_edges(vid) == 0):
            self.eval_vertex(vid)

        # Update workflow provenance
        t1 = clock()
        if self._prov is not None:
            self._prov.time_end = t1
            wfitem = self._prov.as_wlformat()
            self._provdb.add_wf_item(wfitem)

            # close remote connections
            self._provdb.close()

        if quantify:
            print "Evaluation time: %s" % (t1 - t0)

    def eval_vertex_code(self, vid, *args, **kwargs):
        """
                Evaluate the vertex vid.
                Can raise an exception if evaluation failed.
                """

        node = self._dataflow.actor(vid)

        try:
            t0 = clock()
            if self._prov is not None:
                self._prov.before_eval(self._dataflow, vid)

            # Send value to worker
            context = zmq.Context()
            socket = context.socket(zmq.REQ)
            print "Start evaluating node : ", vid
            socket.connect("tcp://localhost:5559")

            msg = dict()
            # msg['pkg_name'] = self._dataflow.get_factory().package.name
            # msg['wf_name'] = self._dataflow.get_factory().name
            msg['vid'] = vid
            inputs = node.input_desc
            for inp in inputs:
                inp['interface']=None
                inp['value']=node.get_input(inp['name'])
            msg['inputs'] = inputs

            if (vid != 0) & (vid != 1):
                socket.send(json.dumps(msg))
                outputs = socket.recv()
                outputs = json.loads(outputs)
                for out in outputs:
                    node.set_output(out['name'], val=out['value'])
            else:
                ret = node.eval()
            # ret = node.eval()

            dt = clock() - t0
            if self._prov is not None:
                taskitem=self._prov.after_eval(self._dataflow, vid, dt)
                if taskitem:
                    self._provdb.add_task_item(taskitem)

            # When an exception is raised, a flag is set.
            # So we remove it when evaluation is ok.
            node.raise_exception = False
            # if hasattr(node, 'raise_exception'):
            #     del node.raise_exception
            node.notify_listeners(('data_modified', None, None))
            # return ret
            return

        except EvaluationException, e:
            e.vid = vid
            e.node = node
            # When an exception is raised, a flag is set.
            node.raise_exception = True
            node.notify_listeners(('data_modified', None, None))
            raise e

        except Exception, e:
            # When an exception is raised, a flag is set.
            node.raise_exception = True
            node.notify_listeners(('data_modified', None, None))
            raise EvaluationException(vid, node, e, \
                                      tb.format_tb(sys.exc_info()[2]))
        return

class FragmentEvaluation(AbstractEvaluation):
    """ Evaluation with By fragments """
    __evaluators__.append("FragmentEvaluation")

    # TODO: It doesn't work with provenance
    def __init__(self, dataflow, record_provenance=False, fragment_infos=None, *args, **kwargs):

        AbstractEvaluation.__init__(self, dataflow, record_provenance)
        # a property to specify if the node has already been evaluated
        self._evaluated = set()
        self._fragment_infos = fragment_infos
        self._index = None

    def is_stopped(self, vid, actor):
        """ Return True if evaluation must be stop at this vertex """

        if vid in self._evaluated:
            return True

        try:
            if actor.block:
                status = True
                n = actor.get_nb_output()
                outputs = [i for i in range(n) if
                           actor.get_output(i) is not None]
                if not outputs:
                    status = False
                return status
        except:
            pass
        return False

    def eval_vertex(self, vid, *args, **kwargs):
        """ Evaluate the vertex vid """

        df = self._dataflow
        actor = df.actor(vid)

        self._evaluated.add(vid)

        # For each inputs
        for pid in df.in_ports(vid):
            inputs = []

            # check if the data has to be loaded | and get path
            ituple = check_data_to_load(vid, pid, self._fragment_infos)
            if ituple:
                cpt = 1
                for npid, nvid, nactor in self.get_parent_nodes(pid):
                    data_id = get_id(ituple[0], ituple[1])
                    row = self._index.find_one(data_id=data_id)
                    inputs.append(load_data(row[0].path[0]))
            else:
                cpt = 0
                # For each connected node
                for npid, nvid, nactor in self.get_parent_nodes(pid):
                    if not self.is_stopped(nvid, nactor):
                        self.eval_vertex(nvid)

                    
                    inputs.append(nactor.get_output(df.local_id(npid)))
                    cpt += 1

            # set input as a list or a simple value
            if (cpt == 1):
                inputs = inputs[0]
            if (cpt > 0):
                actor.set_input(df.local_id(pid), inputs)

        # Eval the node
        self.eval_vertex_code(vid)

    def eval(self, *args, **kwargs):
        """ Evaluate the whole dataflow starting from leaves"""
        print "START fragment evaluation"
        t0 = time.time()

        self._index = IndexCassandra()
        self._index.initialize()
        
        df = self._dataflow

        if self._prov is not None:
            self._prov.init(df)
            self._prov.time_init = t0


        # Unvalidate all the nodes
        self._evaluated.clear()
        # Start by stoping all parents node of input fragments nodes
        if self._fragment_infos:
            for ivid, ipid in self._fragment_infos['inputs_vid']:
                for npid, nvid, nactor in self.get_parent_nodes(ipid):
                    self._evaluated.add(nvid)
                    print "Set : ", nvid, " as EVALUATED"
        
        
        # Eval from the leaf
        for vid in (vid for vid in df.vertices() if df.nb_out_edges(vid) == 0):
            self.eval_vertex(vid)

        t1 = time.time()

        # Save the outputs of the fragment into file
        if not os.path.exists(os.path.dirname(TMP_PATH)):
                os.makedirs(TMP_PATH)
        for i, vid in enumerate([v[0] for v in self._fragment_infos['outputs_vid']]):
            for port in range(df.node(vid).get_nb_output()):
                data_id = get_id(vid, port)
                write_data(data_id=data_id, data=df.node(vid).get_output(port), path=TMP_PATH)
                self._index.add_data(data_id=data_id, path=str(os.path.join(TMP_PATH, data_id)))


        if self._prov is not None:
            self._prov.time_end = t1
            # Save the provenance in a file
            wf_id = str(df.factory.uid) + ".json"
            provenance_path = os.path.join(PROVENANCE_PATH, wf_id)
            if not os.path.exists(os.path.dirname(provenance_path)):
                os.makedirs(provenance_path)
            provenance = self._prov.as_wlformat()
            with open(provenance_path, "a+") as f:
                json.dump(provenance, f, indent=4)

        if quantify:
            print "Evaluation time: %s" % (t1 - t0)