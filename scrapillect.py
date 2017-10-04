import requests
from BeautifulSoup import BeautifulSoup
import shutil
import os, sys, errno
import urlparse
from simplejson import loads, dumps

print "starting..."

url = 'http://archillect.com'
response = requests.get(url)
html = response.content

soup = BeautifulSoup(html)

container = soup.find('div', attrs={'id': 'container'})

try:
    state = loads(open(os.path.join(os.path.dirname(__file__), 'scrape.state'), 'r').read())
except IOError:
    state = {}

if 'last_image' not in state:
    state['last_image'] = ''


# create the output images folder if it doesn't exist
def ensure_dir(directory):
    if not os.path.exists(directory):
        try:
            print ""
            print "making,,," + directory
            print ""
            os.makedirs(directory)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise


first_image = ''

# loop through all the thumbnails on the home page
try:
    for row in container.findAll('a'):
        if first_image == '':
            first_image = row.get('href')

        if state['last_image'] == row.get('href'):
            print "...the rest of these look familiar"
            break

        sys.stdout.write(row.get('href'))
        sys.stdout.flush()

        # go through each sub_page
        sub_url = url + row.get('href')
        response2 = requests.get(sub_url)
        html2 = response2.content
        soup2 = BeautifulSoup(html2)

        # get the image url from that sub_page
        sub_page = soup2.find('img', attrs={'id': 'ii'})

        # get the base filename from the server, we'll use this to write the file
        image_filename = urlparse.urlsplit(sub_page.get('src')).path.split('/')[-1]
        sys.stdout.write(".." + image_filename)
        sys.stdout.flush()

        script_path = os.path.dirname(os.path.realpath(__file__))
        ensure_dir(script_path + '/images')

        # download the image
        response3 = requests.get(sub_page.get('src'), stream=True)
        with open(script_path + "/images/" + image_filename, 'wb') as out_file:
            shutil.copyfileobj(response3.raw, out_file)

        print "..done!"
except KeyboardInterrupt:
    print ""
    print "KeyboardInterrupt: Quitting without saving state"
    exit(1)


state['last_image'] = first_image

print "...all done!"
open(os.path.join(os.path.dirname(__file__), 'scrape.state'), 'w').write(dumps(state))
