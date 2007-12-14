# -*- python -*-
#
#       OpenAlea.Core
#
#       Copyright 2006-2007 INRIA - CIRAD - INRA  
#
#       File author(s): Jerome Chopard <jerome.chopard@sophia.inria.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
# 
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
################################################################################


__doc__="""
This module provide an actor interface
"""

__license__= "Cecill-C"
__revision__=" $Id$ "

class IActor (object) :
	"""
	interface to emulate a function
	"""
	def inputs (self) :
		"""
		iterate on all input description
		return iter of (input key,input interface)
		"""
		raise NotImplementedError
	
	def outputs (self) :
		"""
		iterate on all output descriptions
		return iter of (otuput key,output interface)
		"""
		raise NotImplementedError
	
	def eval (self) :
		"""
		function called after setting the input
		to compute output values
		"""
		raise NotImplementedError
	
	def set_input (self, key, value) :
		"""
		set input specified by a key to value
		"""
		raise NotImplementedError
	
	def output (self, key) :
		"""
		get value computed for output
		"""
		raise NotImplementedError
