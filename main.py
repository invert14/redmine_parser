import urllib2
import libxml2dom
import re
import sys

#default URL
URL = "http://www.redmine.org/projects/redmine/issues"

def get_url_from_arguments():
    url = sys.argv[1] + "/projects/" + sys.argv[2] + "/issues"
    if not url.startswith('http'):
        url = '%s%s' % ('http://', url)
    return url

def get_page_string(url):
    f = urllib2.urlopen(url)
    s = f.read()
    f.close()
    return s



URL = get_url_from_arguments()
print str(get_page_string(URL))

