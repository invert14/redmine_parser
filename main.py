import urllib2
import sys
import libxml2dom

#dictionary with issues
#key - category
#value - list of issues
issues_dict=dict()


#if necessary adding "http://" to URL
def add_http_if_necessary(url):
    if not url.startswith('http'):
        url = '%s%s' % ('http://', url)
    return url

#getting base url of redmine system instance (from command line argument)
def get_base_url():
    url = sys.argv[1]
    url = add_http_if_necessary(url)
    return url

#getting command line arguments from sys.argv[]
def get_url_from_arguments():
    url = sys.argv[1] + "/projects/" + sys.argv[2] + "/issues"
    url = add_http_if_necessary(url)
    return url

#getting string with html content of a page
def get_page_string(url):
    f = urllib2.urlopen(url)
    s = f.read()
    f.close()
    return s

#getting links to issues on the current page
def get_issues_links(html_string):
    dom = libxml2dom.parseString(html_string, html=1)
    issues_dom = dom.xpath('.//td[@class="subject"]')

    return [i.getElementsByTagName('a')[0].getAttribute('href') for i in issues_dom ]

#parsing an issue page
#adding issue to issues dictionary
def parse_issue_page(link):
    ps = get_page_string(link)
    dom = libxml2dom.parseString(ps, html=1)

    #retrieve id
    id = link[link.rfind('/')+1:]

    #retrieve subject
    subject_dom = dom.xpath('.//div[@class="subject"]')[0]
    subject = subject_dom.xpath('.//h3/text()')[0].toString()

    attributes_dom = dom.xpath('.//table[@class="attributes"]')[0]

    #retrieve status
    status = attributes_dom.xpath('.//td[@class="status"]/text()')[0].toString()

    #retrieve priority
    priority = attributes_dom.xpath('.//td[@class="priority"]/text()')[0].toString()

    #retrieve category
    category = attributes_dom.xpath('.//td[@class="category"]/text()')[0].toString()

    #retrieve affected version
    aff_dom = attributes_dom.xpath('.//td[@class="cf_4"]/a/text()')
    aff_version = ""
    if (len(aff_dom) > 0):
        aff_version = aff_dom[0].toString()

    if not issues_dict.has_key(category):
        issues_dict[category] = []
    issues_dict[category].append([id, status, subject, priority, aff_version])

    print id + " " + category + " " + subject + " " + status + " " + priority + " " + aff_version

#parsing all issue pages (from given urls)
def parse_issue_pages(links):
    for l in links:
        l = get_base_url() + l
        parse_issue_page(l)

#comparator of issues - used during sorting
def issues_comparator(x, y):
    x_priority = x[3]
    y_priority = y[3]
    x_status = x[1]
    y_status = y[1]
    if (x_priority != y_priority):
        return x_priority - y_priority
    else:
        return x_status - y_status

#sort dictionary of issues (by priority and status)
def sort_issuse_dict():
    for cat in issues_dict.keys():
        issues_dict[cat].sort(issues_comparator)

#printing issues_dict fo CSV files (by categories)
def print_issues_to_files():
    for category_name in issues_dict.keys():

        #to make category name a valid file name we strip it down
        filename = "".join(c for c in category_name if c.isalnum() or c in ('-', '_')).rstrip()
        f = open('%s.dat' % filename, 'w+')
        for issue in issues_dict[category_name]:
            for i in range(len(issue)):
                s = issue[i]
                if i != len(issue)-1:
                    s += ';'
                if len(s)<1:
                    s='""'
                f.write(s)
            f.write('\n')
        f.close()

#parse single page with list of issues (to get links to these issues)
def parse_issues_list_page(url):
    html_string = get_page_string(url)
    issues_links = get_issues_links(html_string)
    parse_issue_pages(issues_links)

#parse all issues for the project
#we're iterating over pages till we get page with no data
def parse_all_issues_list_pages(url):
    i = 1
    while True:
        url_for_page = url + '?page=%s' % str(i)
        #if you want to parse just first N pages, uncomment following lines
        ###################################################################
        #N=15
        #if i>N:
        #    break
        ####################################################################
        if check_if_end_of_data(url_for_page):
            break
        parse_issues_list_page(url_for_page)
        i += 1

#returns if there are no issues on current page
#(no data)
def check_if_end_of_data(url_for_page):
    ps = get_page_string(url_for_page)
    dom = libxml2dom.parseString(ps, html=1)
    if len(dom.xpath('.//p[@class="nodata"]')) > 0:
        return True
    return False

def check_for_command_line_arguments():
    if len(sys.argv) != 3:
        print "usage: python main.py XXX YYY"
        print "XXX - address of redmine system instance"
        print "YYY - name of redmine project"
        exit()

###################################################

check_for_command_line_arguments()

URL = get_url_from_arguments()
parse_all_issues_list_pages(URL)

print_issues_to_files()

