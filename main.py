# -*- coding: utf-8 -*-
"""
Created on Thu Nov  1 00:10:03 2012

@author: bugra
"""

import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)

class Handler(webapp2.RequestHandler):
    
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)
        
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)
        
    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Blog(db.Model):
    
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
        
class MainPage(Handler):
    
    def render_front(self, subject="", content ="", error=""):
        blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC")                
        self.render("index.html", subject=subject, content=content,
                    error=error , blogs=blogs)
    
    def get(self):
        self.render_front()     

class NewPost(Handler):
    
    def render_front(self, subject="", content="", error=""):    
        self.render("newpost.html", subject=subject, content=content,
                    error=error)
                    
    def get(self):
        self.render_front()     
    
    def post(self):
        content = self.request.get("content")
        subject = self.request.get("subject")
    
        if content and subject:
            b = Blog(subject=subject, content=content)
            b_key = b.put()            
            self.redirect("/%d" % b_key.id())
        else:
            error = "we need both a subject a blog post"
            self.render_front(subject, content, error)
            
class PermaLink(MainPage):

    def get(self, blog_id):
        permalink_id = Blog.get_by_id(int(blog_id))
        self.render('index.html', blogs = [permalink_id])
        
app = webapp2.WSGIApplication([('/', MainPage),
                               ('/newpost', NewPost),
                               ('/(\d+)', PermaLink)],
                                debug=True)