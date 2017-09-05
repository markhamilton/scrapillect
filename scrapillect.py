import requests
from BeautifulSoup import BeautifulSoup
import shutil
import os, sys, errno
import urlparse

print "starting..."

url = 'http://archillect.com'
response = requests.get(url)
html = response.content

soup = BeautifulSoup(html)

container = soup.find('div', attrs={'id':'container'})


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


# loop through all the thumbnails on the home page
for row in container.findAll('a'):
    sys.stdout.write(row.get('href'))
    sys.stdout.flush()

    # go through each subpage
    suburl = url + row.get('href')
    response2 = requests.get(suburl)
    html2 = response2.content
    soup2 = BeautifulSoup(html2)

    # get the image url from that subpage
    subpage = soup2.find('img', attrs={'id':'ii'})
    # sys.stdout.write('..' + subpage.get('src'))
    # sys.stdout.flush()

    # get the base filename from the server, we'll use this to write the file
    imagefilename = urlparse.urlsplit(subpage.get('src')).path.split('/')[-1]
    sys.stdout.write(".." + imagefilename)
    sys.stdout.flush()

    script_path = os.path.dirname(os.path.realpath(__file__))
    ensure_dir(script_path + '/images')

    # download the image
    response3 = requests.get(subpage.get('src'), stream=True)
    with open(script_path + "/images/" + imagefilename, 'wb') as out_file:
        shutil.copyfileobj(response3.raw, out_file)

    print "..done!"


print "...all done!"
