#encoding=utf-8
from tkinter import _flatten
import re
from string import ascii_uppercase
import os 
from time import sleep
import graphviz

# 测试：https://cyberzhg.github.io/toolbox/nfa2dfa

string = ""
special_char = ['(', ')', '*', '|']
nfa = []
dfa_closure = []
dfa_closure_stack = []
dfa = []

def save_and_show(filename, string, end_node):
  file_dir = filename + '.dot'
  template = open('template.dot').read()
  for e in end_node:
    string += '%s [shape=doublecircle];'%e
  string = template%string
  with open(file_dir, 'w') as f:
    f.write(string)
  f.close()
  dot=graphviz.Source(string)
  dot.render(filename)

def remove_parenthesis(string):
  '''
  作用是删除括号将原式子化成类似数的形式
  '''
  processed = []
  for char in string:
    if char == ')':
      tmp = []
      while True:
        pop_char = processed.pop()
        if pop_char == '(':
          break
        tmp.append(pop_char)
      processed.append(tmp[::-1])
    else:
      processed.append(char) 
  node = list(set(_flatten(processed)) - set(special_char))
  node.sort()
  return processed, node

def get_operator(processed):
  '''
  None, *, |
  注意 "|" 是三元运算符
  '''
  tmp = []
  for i, section in enumerate(processed):
    if type(section) == list:
      tmp.append(get_operator(section))
    elif section == '*':
      sec = tmp.pop()
      tmp.append(('*', [sec]))
    elif section == '|':
      tmp = []
      left = get_operator(processed[0:i])
      right= get_operator(processed[i+1:])
      tmp.append(('|', left, right))
      return tmp
    else:
      tmp.append(('', section))    
  return tmp

def regex2nfa(processed, node_index=0):
  '''
  processed就是去掉括号后的字符串形成的list
  node_index就是现在用到的结点字符
  '''
  template = open('template.dot').read()
  edge = ''
  for i, section in enumerate(processed):
    if type(section) == list:
      temp_edge, node_index = regex2nfa(section, node_index)
      edge += temp_edge
    elif section not in special_char:
      edge += '\t{} -> {} [label={}];\n'.format(node[node_index], node[node_index+1], section)
      node_index += 1
    elif section == '|':
      edge += '\t{} -> {} [label={}];\n'.format(node[node_index], node[node_index+1], processed[i-1])
      edge += '\t{} -> {} [label={}];\n'.format(node[node_index], node[node_index+1], processed[i+1])
      node_index += 1

  save_and_show('nfa', template%edge)
  return edge, node_index

def draw_edge(start, end, operator, node):
  edge = ''
  start_node = start
  end_node = end
  
  for i, op in enumerate(operator):
    sign = op[0]
    if sign=='' and i == len(operator) - 1:
      edge += node2edge(start, end, op[1])
      return edge

    if sign == '|':
      start_node_l = node.pop()
      end_node_l = node.pop()
      tmp_l = draw_edge(start_node_l, end_node_l, op[1], node)
      edge += tmp_l
      start_node_r = node.pop()
      end_node_r = node.pop()
      tmp_r = draw_edge(start_node_r, end_node_r, op[2], node)
      edge += tmp_r
      edge += node2edge(start, start_node_l)
      edge += node2edge(start, start_node_r)
      edge += node2edge(end_node_l, end)
      edge += node2edge(end_node_r, end)
    elif sign == '*':
      start_node_c = node.pop()
      end_node_c = node.pop()
      tmp_c = draw_edge(start_node_c, end_node_c, op[1], node)
      edge += tmp_c
      edge += node2edge(start, start_node_c)
      edge += node2edge(end_node_c, end)
      edge += node2edge(end_node_c, start_node_c)
    elif sign == '':
      # if i == len(operator) - 1:
      #   end_node = node.pop()
      #   edge += node2edge(start_node, end_node, op[1])
      #   start = end_node
      end_node = node.pop()
      edge += node2edge(start, end_node, op[1])
      start = end_node
    else:
      edge += draw_edge(start_node, end_node, op, node)
  return edge

def optimize(edge):
  '''
  删除多余的空边
  '''
  label_line_pattern = re.compile('(\w -> \w \[.+\];)')
  label_line = re.findall(label_line_pattern, edge)
  print(label_line)
  pattern = re.compile('(\w) -> (\w);')
  match = [list(m) for m in re.findall(pattern, edge)]
  for k in range(len(match)):
    for i in range(len(match)):
      for j in range(len(match)):
        if match[i][1] == match[j][0]:
          match[i][1] = match[j][1]
          match[j] = match[i]

  match = list(set([(m[0], m[1]) for m in match]))
  tmp = ''
  for m in label_line:
    tmp += ('\t' + m + '\n')
  for m in match:
    tmp += node2edge(m[0], m[1])
  return tmp

def node2edge(start, end, value=None):
  if value != None:
    nfa.append((start, end, value))
    return '\t{} -> {} [label={}];\n'.format(start, end, value)
  nfa.append((start, end, 'ϵ'))
  return '\t{} -> {}[label=ϵ];\n'.format(start, end)

def nfa2dfa(nfa):
  move_set = set(string) - set(special_char)  

  start_closure = set(move_util(nfa, 'Start', 'ϵ'))
  start_closure.add('Start')
  print("开始的closure %s"%start_closure)
  dfa_closure.append(start_closure)
  dfa_closure_stack.append(start_closure)

  while dfa_closure_stack:
    current_closure = dfa_closure_stack.pop()

    for move in move_set:
      closure = e_closure(current_closure, nfa, move)

      if closure and closure != current_closure:
        dfa.append((current_closure, closure, move))
        if closure not in dfa_closure:
          dfa_closure.append(closure)
          dfa_closure_stack.append(closure)

      elif closure == current_closure and closure:
        if e_closure(current_closure, nfa, 'ϵ'):
          dfa.append((current_closure, closure, move))


def e_closure(closure, nfa, move):
  # tmp_closure = set()
  # while closure and tmp_closure != closure:
  tmp_closure = set(closure)
  closure = set()
  for c_node in tmp_closure:
    if move_util(nfa, c_node, move):
      closure = closure.union(set(move_util(nfa, c_node, move)))
  return closure
           
def move_util(nfa, current_node, move):
  # util_list = epsilon_closure(nfa, current_node)
  util_list = []
  # if move != 'ϵ':
  #   current_move= set()
  #   for e in nfa:
  #     for n in util_list:
  #       if e[0] == n and e[2] == move:
  #         current_move.add(e[2])
  #   util_list = set()
  #   for nod in current_move:
  #     util_list = util_list.union(epsilon_closure(nfa,nod))
  for e in nfa:
    if e[0] == current_node:
      if move != 'ϵ':
        if e[2] == 'ϵ':
          util_list += move_util(nfa, e[1], move)
        elif e[2] == move:
          util_list.append(e[2])
          util_list += move_util(nfa, e[1], 'ϵ')
          return util_list
      else:
        util_list += epsilon_closure(nfa, current_node)
  return util_list

def epsilon_closure(nfa, current_node):
  closure = [current_node]
  for e in nfa:
    if current_node == e[0] and e[2] == 'ϵ':
      closure.append(e[1])
      closure += epsilon_closure(nfa, e[1])
  closure = list(set(closure))
  return closure

def dfatograph(dfa, dfa_closure):
  dfa_map = {}
  tmp_dfa = []
  endnode = []
  edge = ''
  nodes = list(ascii_uppercase)[::-1]
  for dfa_node in dfa_closure:
    char = nodes.pop() 
    dfa_map[tuple(dfa_node)] = char
    if 'End' in dfa_node:
      endnode.append(char)
  for e in dfa:
    tmp0 = dfa_map[tuple(e[0])]
    tmp1 = dfa_map[tuple(e[1])]
    tmp2 = e[2]
    tmp_dfa.append((tmp0, tmp1, tmp2))
    edge += node2edge(tmp0, tmp1, tmp2)
  return tmp_dfa, edge, endnode

# def minimize(dfa_graph, endnode):

if __name__ == "__main__":
  string = input("输入你需要转换的正则式：")

  line = '-'*80
  processed, edge_list = remove_parenthesis(string)
  print("处理后的正则式：%s"%str(processed))
  operator = get_operator(processed)
  print("获取带有符号：%s"%str(operator))

  # 打印NFA
  nodes = list(ascii_uppercase)[::-1]
  edge = draw_edge('Start', 'End', operator, nodes)
  print(line + "\n所得到的NFA如下：")
  for e in nfa:
    print("%s->%s;\t符号为%s"%e)
  print(line)
  save_and_show('nfa', edge, ['End'])

  # 打印DFA
  nfa2dfa(nfa)
  dfa_graph, dfa_edge, endnode = dfatograph(dfa, dfa_closure)
  print(line + "\n所得到的DFA如下：")
  for e in dfa_graph:
    print("%s->%s;\t符号为%s"%e)
  print(line)
  save_and_show('dfa', dfa_edge, endnode)

