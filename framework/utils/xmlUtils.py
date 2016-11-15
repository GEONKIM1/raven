'''
Tools used to format, edit, and print XML in a RAVEN-like way
talbpaul, 2016-05
'''

from __future__ import division, print_function, unicode_literals, absolute_import
import warnings
warnings.simplefilter('default',DeprecationWarning)

import numpy as np
import xml.etree.ElementTree as ET
import xml.dom.minidom as pxml
import re
import os

#define type checking
def isComment(node):
  """
    Determines if a node is a comment type (by checking its tag).
    @ In, node, xml.etree.ElementTree.Element, node to check
    @ Out, isComment, bool, True if comment type
  """
  if type(node.tag).__name__ == 'function':
    return True
  return False

def prettify(tree):
  """
    Script for turning XML tree into something mostly RAVEN-preferred.  Does not align attributes as some devs like (yet).
    The output can be written directly to a file, as file('whatever.who','w').writelines(prettify(mytree))
    @ In, tree, xml.etree.ElementTree object, the tree form of an input file
    @Out, towrite, string, the entire contents of the desired file to write, including newlines
  """
  def prettifyNode(node,tabs=0):
    child = None #putting it in namespace
    space = ' '*2*tabs
    if node.text is None:
      node.text = ''
    if len(node)>0:
      node.text = node.text.strip()
      node.text = node.text + os.linesep+space+'  '
      for child in node:
        prettifyNode(child,tabs+1)
      #remove extra tab from last child
      child.tail = child.tail[:-2]
    if node.tail is None:
      node.tail = ''
    else:
      node.tail = node.tail.strip()
    #custom: RAVEN likes spaces between first-level tab objects
    if tabs == 1 and not isComment(node):
      lines = os.linesep + os.linesep
    else:
      lines = os.linesep
    node.tail = node.tail + lines + space
    #custom: except if you're the last child
    if tabs == 0 and child is not None:
      child.tail = child.tail.replace(os.linesep+os.linesep,os.linesep)
  #end prettifyNode
  if isinstance(tree,ET.ElementTree):
    prettifyNode(tree.getroot())
    return ET.tostring(tree.getroot())
  else:
    prettifyNode(tree)
    return ET.tostring(tree)


  #### OLD WAY ####
  #make the first pass at pretty.  This will insert way too many newlines, because of how we maintain XML format.
  #pretty = pxml.parseString(ET.tostring(tree.getroot())).toprettyxml(indent='  ')
  #loop over each "line" and toss empty ones, but for ending main nodes, insert a newline after.
  #toWrite=''
  #for line in pretty.split('\n'):
  #  if line.strip()=='':
  #    continue
  #  toWrite += line.rstrip()+'\n'
  #  if line.startswith('  </'):
  #    toWrite+='\n'
  return toWrite

def newNode(tag,text='',attrib={}):
  """
    Creates a new node with the desired tag, text, and attributes more simply than can be done natively.
    @ In, tag, string, the name of the node
    @ In, text, string, optional, the text of the node
    @ In, attrib, dict{string:string}, attribute:value pairs
    @ Out, el, xml.etree.ElementTree.Element, new node
  """
  tag = fixXmlTag(tag)
  text = str(text)
  cleanAttrib = {}
  for key,value in attrib.items():
    value = str(value)
    cleanAttrib[fixXmlTag(key)] = fixXmlText(value)
  el = ET.Element(tag,attrib=cleanAttrib)
  el.text = fixXmlText(text)
  return el

def newTree(name,attrib={}):
  """
    Creates a new tree with named node as its root
    @ In, name, string, name of root node
    @ In, attrib, dict, optional, attributes for root node
    @ Out, tree, xml.etree.ElementTree.ElementTree, tree
  """
  name = fixXmlTag(name)
  tree = ET.ElementTree(element=newNode(name))
  tree.getroot().attrib = dict(attrib)
  return tree

def findPath(root,path):
  """
    Navigates path to find a particular element
    @ In, root, xml.etree.ElementTree.Element, the node to start searching along
    @ In, path, string, |-seperated xml path (as "Simulation|RunInfo|JobName")
    @ Out, findPath, None or xml.etree.ElementTree.Element, None if not found or element if found
  """
  path = path.split("|")
  if len(path)>1:
    oneUp = findPath(root,'|'.join(path[:-1]))
    if oneUp is not None:
      return oneUp.find(path[-1])
    else:
      return None
  else:
    return root.find(path[-1])

def loadToTree(filename):
  """
    loads a file into an XML tree
    @ In, filename, string, the file to load
    @ Out, root, xml.etree.ElementTree.Element, root of tree
    @ Out, tree, xml.etree.ElementTree.ElementTree, tree read from file
  """
  tree = ET.parse(filename)
  root = tree.getroot()
  return root,tree

def fixXmlText(msg):
  """
    Removes unallowable characters from xml
    @ In, msg, string, tag/text/attribute
    @ Out, msg, string, fixed string
  """
  #if not a string, pass it back through
  if not isinstance(msg,basestring): return msg
  #otherwise, replace illegal characters with "?"
  # from http://boodebr.org/main/python/all-about-python-and-unicode#UNI_XML
  RE_XML_ILLEGAL = u'([\u0000-\u0008\u000b-\u000c\u000e-\u001f\ufffe-\uffff])' + \
                 u'|' + \
                 u'([%s-%s][^%s-%s])|([^%s-%s][%s-%s])|([%s-%s]$)|(^[%s-%s])' % \
                  (unichr(0xd800),unichr(0xdbff),unichr(0xdc00),unichr(0xdfff),
                   unichr(0xd800),unichr(0xdbff),unichr(0xdc00),unichr(0xdfff),
                   unichr(0xd800),unichr(0xdbff),unichr(0xdc00),unichr(0xdfff))
  msg = re.sub(RE_XML_ILLEGAL, "?", msg)
  return msg

def fixXmlTag(msg):
  """
    Does the same things as fixXmlText, but with additional tag restrictions.
    @ In, msg, string, tag/text/attribute
    @ Out, msg, string, fixed string
  """
  #if not a string, pass it back through
  if not isinstance(msg,basestring): return msg
  #define some presets
  letters = u'([a-zA-Z])'
  notAllTagChars = '(^[a-zA-Z0-9-_.]+$)'
  notTagChars = '([^a-zA-Z0-9-_.])'
  #rules:
  #  1. Can only contain letters, digits, hyphens, underscores, and periods
  if not bool(re.match(notAllTagChars,msg)):
    pre = msg
    msg = re.sub(notTagChars,'.',msg)
    print('XML UTILS: Replacing illegal tag characters in "'+pre+'":',msg)
  #  2. Start with a letter or underscore
  if not bool(re.match(letters+u'|([_])',msg[0])) or bool(re.match(u'([xX][mM][lL])',msg[:3])):
    print('XML UTILS: Prepending "_" to illegal tag "'+msg+'"')
    msg = '_' + msg
  return msg
