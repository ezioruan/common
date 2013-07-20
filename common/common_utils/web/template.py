#! /usr/bin/env python
# coding=utf-8
'''
Created on 2012-7-24

@author: ezioruan
'''

from jinja2 import Environment,FileSystemLoader

class TemplateManager(object):
    
    def __init__(self,template_folder):
        self.env = Environment(loader=FileSystemLoader(template_folder))
        
    
    def render(self,template_name,var_dict={}):
        template = self.env.get_template(template_name)
        if template:
            return str(template.render(var_dict))
        
        
