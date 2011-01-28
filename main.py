# -*- coding: utf-8 -*-
import os
import logging

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

from django.template import TemplateDoesNotExist
from urllib import quote

TEMPLATE_DIR = "templates"
MAIL = "toveseest@supersundt.dk"
# MAIL = "jakob.a.dam@gmail.com"

def render(file_name, handler, **values):

    path = os.path.join(TEMPLATE_DIR, file_name)
    handler.response.headers['Content-Type'] = 'text/html'
    values['config'] = {
        'host': os.environ['HTTP_HOST']
        }
    try:
        handler.response.out.write(template.render(path, values))
    except TemplateDoesNotExist:
        path = os.path.join(TEMPLATE_DIR, '404.html')
        handler.response.out.write(template.render(path, values))
    
class Page(webapp.RequestHandler):
    def get(self):
        path = os.environ['PATH_INFO'].rstrip("/").lstrip("/")
        if path == "":
            path = "index"
        render("%s.html" % (path), self)


class ContactHandler(webapp.RequestHandler):

    def get(self):
        message = self.request.get('besked')
        render("kontakt.html", self, message=message)

    def post(self):
        from google.appengine.api import mail
        errors = []
        name = self.request.get('name')
        email = self.request.get('email')
        subject = self.request.get('subject')
        message = self.request.get('message')
        if not name:
            errors.append("Du skal angive navn.")
        if not email:
            errors.append("Du skal angive email.")
        if not subject:
            errors.append("Du skal angive et emne.")
        if not message:
            errors.append("Du skal skrive noget.")
        if len(errors) > 0:
            error_message = errors.join("<br />")
            logging.info("Message form errors: %s" % (error_message))
            self.redirect("/kontakt/?besked=%s" % error_message)
        user_message = quote("Tak for din henvendelse") 
        try:
            mail.send_mail(
                sender="%s <%s>" % (name, email),
                to=MAIL,
                subject=subject,
                body=message)        
            logging.info("Sending mail from: %s, subject: %s" % (email, subject))
            self.redirect("/kontakt/?besked=%s" % user_message)
        except mail.InvalidEmailError:
            logging.info("Invalid email error trying to send mail from: %s, subject: %s" % (email, subject))
            self.redirect("/kontakt/?besked=%s" % "Ugyldig email addresse!")
            

application = webapp.WSGIApplication([
        ('^/kontakt/$', ContactHandler),
        ('^.*$', Page)
        ],debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
