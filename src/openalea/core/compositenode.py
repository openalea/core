# -*- python -*-
#
#       OpenAlea.Core
#
#       Copyright 2006-2007 INRIA - CIRAD - INRA  
#
#       File author(s): Samuel Dufour-Kowalski <samuel.dufour@sophia.inria.fr>
#                       Christophe Pradal <christophe.prada@cirad.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
# 
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
###############################################################################

__doc__="""
A CompositeNode is a Node that contains other nodes connected in a directed graph.
A CompositeNodeFactory instance is a factory that build CompositeNode instances.
Different instances of the same factory can coexist and can be modified in a
dataflow. 
"""


__license__= "Cecill-C"
__revision__=" $Id$ "

import string
import copy

from node import AbstractFactory, Node
from node import RecursionError, InstantiationError
from pkgmanager import PackageManager, UnknownPackageError
from package import UnknownNodeError
from dataflow import DataFlow, InvalidEdge, PortError
from algo.dataflow_copy import structural_copy
from settings import Settings


class CompositeNodeFactory(AbstractFactory):
    """
    The CompositeNodeFactory is able to create CompositeNode instances
    Each node has an unique id : the element id (elt_id)
    """

    def __init__ (self, *args, **kargs):
        """
        CompositeNodeFactory accept more optional parameters :
        inputs : list of dict(name = '', interface='', value='')
        outputs : list of dict(name = '', interface='', value='')
        doc : documentation
        elt_factory : map of elements with its corresponding factory
        elt_connections : map of ( dst_id , input_port ) : ( src_id, output_port )
        elt_data : Dictionary containing associated data
        elt_value : Dictionary containing Lists of 2-uples (port, value)
        """

        # Init parent (name, description, category, doc, node, widget=None)
        AbstractFactory.__init__(self, *args, **kargs)
        # A CompositeNode is composed by a set of element indexed by an elt_id
        # Each element is associated to NodeFactory
        # Each element will generate an node instance in the real CompositeNode

        # Dict mapping elt_id with its corresponding factory
        # the factory is identified by its unique id (package_id, factory_id)
        self.elt_factory = kargs.get("elt_factory", {})

        # Dictionnary which contains tuples describing connection
        # ( source_vid , source_port ) : ( target_vid, target_port )
        self.connections = kargs.get("elt_connections", {})

        self.elt_data =  kargs.get("elt_data", {})
        self.elt_value =  kargs.get("elt_value", {})


        # Documentation
        self.doc = kargs.get('doc', "")
        

    def clear(self) :
        
        self.elt_factory.clear()
        self.connections.clear()
        self.elt_data.clear()
        self.elt_value.clear()
        

    def get_writer(self):
        """ Return the writer class """

        return PyCNFactoryWriter(self)


    def instantiate(self, call_stack=None):
        """ Create a CompositeNode instance and allocate all elements
        This function overide default implementation of NodeFactory

        @param call_stack : the list of NodeFactory id already in recursion stack
        (in order to avoid infinite loop)
        """
        
        # Test for infinite loop
        if (not call_stack) : call_stack = []
        if (self.get_id() in call_stack):
            raise RecursionError()

        call_stack.append(self.get_id())

        new_df = CompositeNode(self.inputs, self.outputs)
        new_df.factory = self
        new_df.__doc__ = self.doc
        new_df.set_caption(self.get_id())

        error_nodes = set() # non instantiated nodes

        
        # Instantiate the node with each factory
        for vid in self.elt_factory:
            try:
                n = self.instantiate_node(vid, call_stack)
                new_df.add_node(n, vid, False)

            except (UnknownNodeError, UnknownPackageError):
                error_nodes.add(vid)
                print "WARNING : The graph is not fully operational "  
                (pkg, fact) = self.elt_factory[vid]
                print "-> Cannot find '%s.%s'"%(pkg, fact)


        # Set IO internal data
        try:
            new_df.node(new_df.id_in).internal_data = self.elt_data['__in__'].copy()
            new_df.node(new_df.id_out).internal_data = self.elt_data['__out__'].copy()
        except:
            pass

        # Create the connections
        for eid,link in self.connections.iteritems() :
            (source_vid, source_port, target_vid, target_port) = link

            if(source_vid in error_nodes or target_vid in error_nodes): 
                continue

            # Replace id for in and out nodes
            if(source_vid == '__in__') :  source_vid = new_df.id_in
            if(target_vid == '__out__') : target_vid = new_df.id_out
                
            new_df.connect(source_vid, source_port, target_vid, target_port)


        # Set call stack to its original state
        call_stack.pop()

        # Properties
        new_df.lazy = self.lazy
        new_df.graph_modified = False # Graph is not modifyied

        return new_df


    def paste(self, cnode, data_modifiers=[], call_stack=None):
        """ Paste to an existing CompositeNode instance
        @param cnode : composite node instance
        @param data_modifiers : list of 2 uple (key, function) to apply to internal
        data (for instance to move the node)
        @param call_stack : the list of NodeFactory id already in recursion stack
        (in order to avoid infinite loop)

        @return the list of created id
        """

        # map to convert id
        idmap = {}
        
        # Instantiate the node with each factory
        for vid in self.elt_factory:
            n = self.instantiate_node(vid, call_stack)
            
            # Apply modifiers
            for (key, func) in data_modifiers:
                try:
                    n.internal_data[key] = func(n.internal_data[key])
                except:
                    pass

            newid = cnode.add_node(n, None)
            idmap[vid] = newid

        # Create the connections
        for eid,link in self.connections.iteritems():
            (source_vid, source_port, target_vid, target_port) = link
            
            # convert id
            source_vid = idmap[source_vid]
            target_vid = idmap[target_vid]
            
            cnode.connect(source_vid, source_port, target_vid, target_port)

        return idmap.values()



    def instantiate_node(self, vid, call_stack=None):
        """
        Partial instantiation
        instantiate only elt_id in CompositeNode
        @param call_stack : a list of parent id (to avoid infinite recursion)
        """

        (package_id, factory_id) = self.elt_factory[vid]
        pkgmanager = PackageManager()
        pkg = pkgmanager[package_id]
        factory = pkg.get_factory(factory_id)
        node = factory.instantiate(call_stack)
        node.internal_data.update(self.elt_data[vid])

        # copy node input data if any
        values = self.elt_value.get(vid, ())
        for (port, v) in values:
            try:
               node.set_input(port, eval(v))
            except:
                continue
            
        return node

        
    def instantiate_widget(self, node=None, parent=None, edit=False):
        """
        Return the corresponding widget initialised with node
        if node is None, the node is allocated
        else a composite widget composed with the node sub widget is returned

        """
        if(edit):
            from openalea.visualea.compositenode_widget import EditGraphWidget
            return EditGraphWidget(node, parent)
            
        if(node == None):  node = self.instantiate()

        from openalea.visualea.compositenode_widget import DisplayGraphWidget
        return DisplayGraphWidget(node, parent)



################################################################################

class CompositeNode(Node, DataFlow):
    """
    The CompositeNode is a container that interconnect 
    different node instances between them in directed graph.
    """


    def __init__(self, inputs=(), outputs=()):
        """ Inputs and outputs are list of dict(name='', interface='', value='') """

        DataFlow.__init__(self)

        self.id_in = None
        self.id_out = None
        
        Node.__init__(self, inputs, outputs)
     
        # graph modification status
        self.graph_modified = False


    def reset(self):
        """ Reset nodes """

        Node.reset(self)

        for vid in set(self.vertices()):
            node = self.actor(vid)
            node.reset()

    
    def invalidate(self):
        """ Invalidate nodes """

        Node.invalidate(self)

        for vid in set(self.vertices()):
            node = self.actor(vid)
            node.invalidate()


    def set_io(self, inputs, outputs):
        """
        Define inputs and outputs
        Inputs and outputs are list of dict(name='', interface='', value='') 
        """

        #I/O ports
        # Remove node if nb of input has changed
        if(self.id_in is not None
           and len(inputs) != self.node(self.id_in).get_nb_output()):
            self.remove_vertex(self.id_in)
            self.id_in = None

            
        if(self.id_out is not None
           and len(outputs) != self.node(self.id_out).get_nb_input() ):
            self.remove_vertex(self.id_out)
            self.id_out = None

        # Create new io node if necessary
        if(self.id_in is None):
            self.id_in = self.add_node(CompositeNodeInput(inputs))
        else:
            self.node(self.id_in).set_io((),inputs)
            
        if(self.id_out is None):
            self.id_out = self.add_node(CompositeNodeOutput(outputs))
        else:
            self.node(self.id_out).set_io(outputs,())
            
            
        Node.set_io(self, inputs, outputs)
                
        
    def set_input (self, index_key, val=None, *args) :
        """ Copy val into input node output ports """
        self.node(self.id_in).set_input(index_key, val)


    def get_input (self, index_key) :
        """ Return the composite node input"""
        return self.node(self.id_in).get_input(index_key)
        
    
    def get_output (self, index_key) :
        """ Retrieve values from output node input ports """

        return self.node(self.id_out).get_output(index_key)

    def set_output (self, index_key, val) :
        """ Set a value to an output """

        return self.node(self.id_out).set_output(index_key, val)
    

    def get_eval_algo(self):
        """ Return the evaluation algo instance """

#         config = Settings()
        
#         try:
#             str = config.get("eval", "type")

#             str = str.strip('"'); str = str.strip("'")

#             # import module
#             baseimp = "algo.dataflow_evaluation"
#             module = __import__(baseimp, globals(), locals(), [str])
#             classobj = module.__dict__[str]
#             return classobj(self)

#         except Exception, e:
        from  openalea.core.algo.dataflow_evaluation import DefaultEvaluation
        return DefaultEvaluation(self)


    def eval_as_expression(self, vtx_id=None):
        """
        Evaluate a vtx_id
        if node_id is None, then all the nodes without sons are evaluated
        """

        if(vtx_id != None) : self.node(vtx_id).modified = True
        algo = self.get_eval_algo()
        algo.eval(vtx_id)


    # Functions used by the node evaluator
    def eval(self):
        """
        Evaluate the graph
        Return True if the node need a reevaluation (like generator)
        """
        self.__call__()

        self.modified = False
        self.notify_listeners( ("status_modified",self.modified) )
        
        return False


    def __call__(self, inputs=()):
        """
        Evaluate the graph
        """

        if(self.id_out and self.get_nb_output()>0):
            self.eval_as_expression(self.id_out)
        else:
            self.eval_as_expression(None)

        return ()


    def node (self, vid):
        """ Convenience function """
        return self.actor(vid)


    ############################################################################

    def compute_external_io(self, vertex_selection, new_vid):
        """ 
        Return the list of input and output edges to connect the composite node
        """

        ins, in_edges = self._compute_inout_connection(vertex_selection, is_input=True)
        outs, out_edges = self._compute_inout_connection(vertex_selection, is_input=False)
        
        in_edges = self._compute_outside_connection(vertex_selection, in_edges, new_vid, is_input=True)
        out_edges = self._compute_outside_connection(vertex_selection, out_edges, new_vid, is_input=False)
        
        return in_edges + out_edges


    def _compute_outside_connection(self, vertex_selection, new_connections, new_vid, is_input = True):
        """ 
        Return external connections of a composite node 
        with input and output ports.
        - vertex_selection is a sorted set of node.
        """
        connections = []
        selected_port = {}
        if is_input:
            ports = self.in_ports
            get_vertex_io = self.source
            get_my_vertex = self.target
        else:
            ports = self.out_ports
            get_vertex_io = self.target
            get_my_vertex = self.source

        # For each selected vertices
        for vid in vertex_selection:
            for pid in ports(vid):
                connected_edges = self.connected_edges(pid)
                
                for e in connected_edges:
                    s = get_vertex_io(e)
                    if s not in vertex_selection:
                        pname = self.local_id(pid)
                        selected_port.setdefault((vid, pname), []).append(e)
                        
        for edge in new_connections:
            if is_input:
                if not (edge[0] == '__in__'):
                    continue
                target_id, target_port = edge[2:]
                if (target_id, target_port) in selected_port:
                    target_edges = selected_port[(target_id, target_port)]
                    for e in target_edges:
                        vid = self.source(e)
                        port_id = self.local_id(self.source_port(e))
                        connections.append((vid, port_id, new_vid, edge[1]))
            else:
                if not (edge[2] == '__out__'):
                    continue
                source_id, source_port = edge[0:2]
                if (source_id, source_port) in selected_port:
                    source_edges= selected_port[(source_id, source_port)]
                    for e in source_edges:
                        vid = self.target(e)
                        port_id = self.local_id(self.target_port(e))
                        connections.append((new_vid, edge[3], vid, port_id))

        return connections


    def _compute_inout_connection(self, vertex_selection, is_input=True):
        """ Return internal connections of a composite node 
            with input port or output port.
            - vertex_selection is a sorted set of node.
            - is_input is a boolean indicated if connection
             have to be created with input or output ports.
        """
        nodes = []
        connections = []

        # just to select unique name
        name_port = []

        if is_input:
            ports = self.in_ports
            get_vertex_io = self.source
            io_desc = lambda n: n.input_desc
        else:
            ports = self.out_ports
            get_vertex_io = self.target
            io_desc = lambda n: n.output_desc

        # For each input port
        for vid in vertex_selection:
            for pid in ports(vid):
                connected_edges = list(self.connected_edges(pid))
                
                is_io = False
                for e in connected_edges:
                    s = get_vertex_io(e)
                    if s not in vertex_selection:
                        is_io = True

                if connected_edges:
                    if not is_io:
                        continue

                pname = self.local_id(pid)
                n = self.node(vid)
                desc = dict(io_desc(n)[pname])

                caption= '(%s)'%(n.get_caption())
                count = '' 
                name = desc['name']
                while name+str(count)+caption in name_port:
                    if count:
                        count+=1
                    else: 
                        count = 1
                desc['name'] = name+str(count)+caption
                name_port.append(desc['name'])

                if is_input:
                    # set default value on cn imput port
                    if n.inputs[pname]:
                        desc['value'] = n.inputs[pname]
                    elif 'value' not in desc:
                        if 'interface' in desc:
                            desc['value']=desc['interface'].default()

                    connections.append( ('__in__', len(nodes), vid, pname) )
                else: # output
                    connections.append( (vid , pname, '__out__', len(nodes)) )
                
                nodes.append(desc)

        return (nodes, connections)

        
    def compute_io(self, v_list=None):
        """
        Return (inputs, outputs, connections)
        representing the free port of node
        v_list is a vertex id list 
        """

        
        ins, in_edges = self._compute_inout_connection(v_list, is_input=True)
        outs, out_edges = self._compute_inout_connection(v_list, is_input=False)
        connections = in_edges + out_edges

        return (ins, outs, connections)


    def to_factory(self, sgfactory, listid = None, auto_io=False):
        """
        Update CompositeNodeFactory to fit with the graph
        listid is a list of element to export. If None, select all id.
        if auto_io is true :  inputs and outputs are connected to the free
        ports
        """
        
        # Clear the factory
        sgfactory.clear()

        # Properties
        sgfactory.lazy = self.lazy
        
        # I / O
        if(auto_io):
            (ins, outs, sup_connect) = self.compute_io(listid)
            sgfactory.inputs = ins
            sgfactory.outputs = outs
        else:
            sgfactory.inputs = [dict(val) for val in self.input_desc]
            sgfactory.outputs = [dict(val) for val in self.output_desc]
            sup_connect = []

        if listid is None: 
            listid = set(self.vertices())

        # Copy Connections
        for eid in self.edges() :

            src = self.source(eid)
            tgt = self.target(eid)

            if((src not in listid) or (tgt not in listid)) : continue
            if(src == self.id_in) : src = '__in__'
            if(tgt == self.id_out) : tgt = '__out__'
            
            source_port = self.local_id(self.source_port(eid))
            target_port = self.local_id(self.target_port(eid))
            sgfactory.connections[id(eid)] = (src, source_port, tgt, target_port)

        # Add supplementary connections
        for e in  sup_connect:
            sgfactory.connections[id(e)] = e
            

        # Copy node
        for vid in listid:

            node = self.actor(vid)
            kdata = node.internal_data
                
            # Do not copy In and Out
            if(vid == self.id_in):  vid = "__in__"
            elif(vid == self.id_out): vid = "__out__"                
            else:
                pkg_id = node.factory.package.get_id()
                factory_id = node.factory.get_id()
                sgfactory.elt_factory[vid] = (pkg_id, factory_id)

            # Copy internal data
            sgfactory.elt_data[vid] = copy.deepcopy(kdata)

            # Copy value
            if(not node.get_nb_input()):
                sgfactory.elt_value[vid] = []
            else:
                sgfactory.elt_value[vid] = \
                                         [(port, repr(node.get_input(port))) for port
                                          in xrange(len(node.inputs))
                                          if node.input_states[port] is not "connected"]
     
        self.graph_modified = False

        # Set node factory if all node have been exported
        if(listid is None):
            self.factory = sgfactory
        


    def add_node(self, node, vid = None, modify=True):
        """
        Add a node in the Graph with a particular id
        if id is None, autogenrate one
        
        @param node : the node instance
        @param vtx_id : element id

        @param return the id
        """
        vid = self.add_vertex( vid )
        
        for local_pid in xrange(node.get_nb_input()) :
            self.add_in_port(vid, local_pid)
            
        for local_pid in xrange(node.get_nb_output()) :
            self.add_out_port(vid, local_pid)
            
        self.set_actor(vid, node)
        #self.id_cpt += 1
        if(modify):
            self.notify_listeners(("graph_modified",))
            self.graph_modified = True

        return vid
    

    def remove_node(self, vtx_id):
        """
        remove a node from the graph
        @param vtx_id : element id
        """

        if(vtx_id == self.id_in or vtx_id == self.id_out): return
        self.remove_vertex(vtx_id)

        self.notify_listeners(("graph_modified",))
        self.graph_modified = True
               

    def connect(self, src_id, port_src, dst_id, port_dst):
        """ Connect 2 elements :
        @param src_id : source node id
        @param port_src : source output port number
        @param dst_id : destination node id
        @param port_dst : destination input port number
        """
        
        source_pid = self.out_port(src_id, port_src)
        target_pid = self.in_port(dst_id, port_dst)
        DataFlow.connect(self, source_pid, target_pid)
        
        self.actor(dst_id).set_input_state(port_dst, "connected")
        self.notify_listeners(("connection_modified",))
        self.graph_modified = True


    def disconnect(self, src_id, port_src, dst_id, port_dst):
        """ Deconnect 2 elements :
        @param src_id : source node id
        @param port_src : source output port number
        @param dst_id : destination node id
        @param port_dst : destination input port number
        """

        source_pid = self.out_port(src_id, port_src)
        target_pid = self.in_port(dst_id, port_dst)
        for eid in self.connected_edges(source_pid) :
            if self.target_port(eid) == target_pid :
                #DataFlow.disconnect(self,eid)
                self.remove_edge(eid)
                self.actor(dst_id).set_input_state(port_dst, "disconnected")
                self.notify_listeners(("connection_modified",))
                self.graph_modified = True
                return
            
        raise InvalidEdge("Edge not found")

    



class CompositeNodeInput(Node):
    """Dummy node to represent the composite node inputs"""

    def __init__(self, inputs):
        """
        inputs : list of dict(name='', interface='', value'',...)
        """

        Node.__init__(self)
        
        for d in inputs:
            self.add_output(**d)

        self.internal_data['posx'] = 20
        self.internal_data['posy'] = 5
        self.internal_data['caption'] = "In"


    def set_input (self, input_pid, val=None, *args) :
        """ Define input value """
        index = self.map_index_out[input_pid]
        self.outputs[index] = val


    def get_input (self, input_pid) :
        """ Return the input value """
        index = self.map_index_out[input_pid]
        return self.outputs[index]

   
    def eval(self):
        return False



class CompositeNodeOutput(Node):
    """Dummy node to represent the composite node outputs"""

    def __init__(self, outputs):
        """
        outputs : list of dict(name='', interface='', value'',...)
        """
        Node.__init__(self)
        
        for d in outputs:
            self.add_input(**d)

        self.internal_data['posx'] = 20
        self.internal_data['posy'] = 250
        self.internal_data['caption'] = "Out"


    def get_output(self, output_pid) :
        """ Return Output value """

        index = self.map_index_in[output_pid]
        return self.inputs[index]
    

    def set_output(self, output_pid, val) :
        """ Define output """
 
        index = self.map_index_in[output_pid]
        self.inputs[index] = val


    def eval(self):
        return False


################################################################################

class PyCNFactoryWriter(object):
    """ CompositeNodeFactory python Writer """

    sgfactory_template = """

    nf = CompositeNodeFactory(name=$NAME, 
                              description=$DESCRIPTION, 
                              category=$CATEGORY,
                              doc=$DOC,
                              inputs=$INPUTS,
                              outputs=$OUTPUTS,
                              elt_factory=$ELT_FACTORY,
                              elt_connections=$ELT_CONNECTIONS,
                              elt_data=$ELT_DATA,
                              elt_value=$ELT_VALUE,
                              lazy=$LAZY,
                              )

    pkg.add_factory(nf)
"""

    def __init__(self, factory):
        self.factory = factory
        

    def __repr__(self):
        """ Return the python string representation """
        from pprint import pprint
        from StringIO import StringIO

        def pprint_repr(obj):
            stream = StringIO()
            pprint(obj, stream=stream)
            s=stream.getvalue()[:-1]
            if '\n' not in s: 
                return s
            else:
                return '\\\n'+s

        f = self.factory
        fstr = string.Template(self.sgfactory_template)

        result = fstr.safe_substitute(NAME=pprint_repr(f.name),
                                      DESCRIPTION=pprint_repr(f.description),
                                      CATEGORY=pprint_repr(f.category),
                                      DOC=pprint_repr(f.doc),
                                      INPUTS=pprint_repr(f.inputs),
                                      OUTPUTS=pprint_repr(f.outputs),
                                      ELT_FACTORY=pprint_repr(f.elt_factory),
                                      ELT_CONNECTIONS=pprint_repr(f.connections),
                                      ELT_DATA=pprint_repr(f.elt_data),
                                      ELT_VALUE=pprint_repr(f.elt_value),
                                      LAZY=pprint_repr(f.lazy),
                                      )
        return result





    
