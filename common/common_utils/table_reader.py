#! /usr/bin/env python
# -*- coding: utf-8 -*-
#======================================================================
# 
# Author: adaws
# Fun: 读表器
# Date:  2011-10-20
#
#======================================================================
from ctypes import *
import types
import os

OUTPUT_SINGLE_SPACE = 15

class Record(Structure):
	'''表中的单条记录类 紧凑结构 note: 如果table字段超长的话这里会报错 需要注意 开服是注意 发现报错修改表 或者让程序修改字段长度
	'''
	_fields_ = []
	_char_to_lst_ = []
	_char_to_eval_ = []
	_char_to_compile_ = []

	#空串代替符
	NULL_CHAR = '-'

	#_char_to_lst_ 分割符
	SPLITE_CHAR = ','
	def __init__(self):
		self.lenth = len(self._fields_)

	def readdata(self, line):
		datalst = [i.strip() for i in line.strip().split('\t') if i.strip() != '']

		for fieldindex, data in enumerate(datalst[:self.lenth]):

			attr_name, attr_type = self._fields_[fieldindex]
			if attr_type in [c_short, c_ushort, c_int, c_uint, c_long, c_ulong, c_longlong, c_ulonglong, c_ubyte, c_float, c_double]:
				#@note:  可以将一些 字段很长的 但是服务端不需要记录的数据 类型字段设计成为c_int或其他上面的 这样这些字符串数据不会读到内存
				try:
					data = eval(data)
				except:
					data = 0
			else:
				#@warning: do something here if you want to prevent fields too long error 
				pass
			
			try:
				setattr(self, attr_name, data)
			except:
				print data, line, fieldindex
				raise
			
		for src_key, dest_key in self._char_to_lst_:
			src_data = getattr(self, src_key, None)

			dest_value = []
			if src_data.strip() != self.NULL_CHAR:
				try:
					replaced_data = src_data.replace(self.SPLITE_CHAR, ',')
					dest_value = eval("[%s]" % replaced_data)
				except:
					pass

			setattr(self, dest_key, dest_value)


		for src_key, dest_key in self._char_to_eval_:
			src_data = getattr(self, src_key, None)

			dest_value = None
			if src_data.strip() != self.NULL_CHAR:
				try:
					dest_value = eval(src_data)
				except:
					pass

			setattr(self, dest_key, dest_value)

		for src_key, dest_key in self._char_to_compile_:
			src_data = getattr(self, src_key, None)

			dest_value = None
			if src_data.strip() != self.NULL_CHAR:
				try:
					dest_value = compile(src_data, '', 'eval')
				except:
					pass

			setattr(self, dest_key, dest_value)

	def setdata(self, datalst):
		for fieldindex, data in enumerate(datalst):
			setattr(self, self._fields_[fieldindex][0], data)
			
	def get_data(self):
		data = {}
		for key,_ in self._fields_:
			data.update({key:getattr(self, key)})
		return data

	#单条记录的str
	def __str__(self):
		return ' '.join([(str(getattr(self, i[0]))[:OUTPUT_SINGLE_SPACE].center(OUTPUT_SINGLE_SPACE)) for i in self._fields_]) + '\n'

	#类的头 的输出str 需要给定具体的类 子类。
	@staticmethod
	def get_header(cls):
		return '|'.join([(str(i[0])[:OUTPUT_SINGLE_SPACE].center(OUTPUT_SINGLE_SPACE)) for i in cls._fields_]) + '\n'
	
	@staticmethod
	def reload_update(oldobj, newobj):
		'''
		用于reload
		@param oldobj:
		'''
		return newobj

class TableData(object):
	'''表的数据 有每行数据构成 维护  索引  提供通过索引获得行 通过index 获得行 获得行的总数 获得满足某些条件的行的列表等接口
	'''
	def __init__(self, filepath, classname, mainkeylist, startline='#------------'):
		'''建索引 读文件中的数据
		'''
		self.records = []
		self.indexs = {}
		self.classname = classname
		pf = open(filepath, 'r')
		lines = pf.readlines()
		
		start_line = 0
		if type(startline) == int:
			start_line = startline
			started = True
		else:started = False
		cur_effect_index = 0
		for line_no, line in enumerate(lines):
			if not started:
				if line.startswith(startline):
					started=True
					start_line = line_no + 2
				continue
			else:
				if line_no < start_line:continue
			
			line = line.strip()
			if not line:continue
			record = classname()
			record.readdata(line)
			index_key = [getattr(record, i) for i in mainkeylist]
			self.indexs[tuple(index_key)] = cur_effect_index
			cur_effect_index += 1
			self.records.append(record)
		pf.close()

	def get_record_by_index(self, index):
		assert index < len(self.records)
		return self.records[index]

	def get_record_by_mainkeylst(self, mainkeylst):
		'''根据主键的值获得对应的数据 主键是一开始剪标的时候定的 如果需要支持多个索引的话需要在这改
		'''
		if type(mainkeylst) not in [types.ListType, types.TupleType]: mainkeylst = [mainkeylst]
		getindex = self.indexs.get(tuple(mainkeylst))
		if getindex != None:
			return self.get_record_by_index(getindex)

	def get_record_by_key(self, value):
		return self.records[self.indexs[(value, )]]

	def get_records_by_matchdict(self, matchdict, maxcount=999):
		'''获得能够满足matchdict 给的键值和对应的值 找到满足条件的record 最多maxcount个 默认1000个
		'''
		reslst = []
		findcount = 0
		for record in self.records:
			match = True
			for key, value in matchdict.items():
				if getattr(record, key) != value:
					match = False
					break

			if match:
				findcount += 1
				reslst.append(record)
				if findcount >= maxcount:
					break
		return reslst

	def __str__(self):
		'''表的格式化输出
		'''
		headstr = self.classname.get_header(self.classname) + '—'*200+'\n'
		recordstr = ' '.join([str(i) for i in self.records])
		return ' %s %s\n' % (headstr, recordstr)

	def get_count(self):
		return len(self.records)
	
	def get_last_record(self):
		return self.get_record_by_index(self.get_count() - 1)
		
	def __iter__(self):
		for record in self.records:
			yield record


#PYTHON SLOTS 结构的类  考虑到有可能字段的可变性较大 不采用固定的 Struct 
class Record_Ex(object):
	_fields_ = []
	__slots__ = []
	def __init__(self):
		fields_set = set(self._fields_)
		for var in self.__slots__:
			if var not in fields_set:
				setattr(self, var, None)

	#读取数据 给定一行
	def readdata(self, line):
		lenth = len(self._fields_)
		datalst = [i.strip() for i in line.strip().split('\t') if i.strip() != '']
		for fieldindex, data in enumerate(datalst[:lenth]):
			setattr(self, self._fields_[fieldindex], data)

	#单条记录的str
	def __str__(self):
		return ' '.join([(str(getattr(self, attr_name))[:OUTPUT_SINGLE_SPACE].center(OUTPUT_SINGLE_SPACE)) for attr_name in self._fields_]) + '\n'

	#类的头 的输出str 需要给定具体的类 子类。
	@staticmethod
	def get_header(cls):
		return ' '.join([(str(attr_name)[:OUTPUT_SINGLE_SPACE].center(OUTPUT_SINGLE_SPACE)) for attr_name in cls._fields_]) + '\n'
