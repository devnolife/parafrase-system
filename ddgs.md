a) text:

query='neurophysiology of the flickering light perception'
region='cn'
language='zh'
max_results=5
backend='google, brave'
proxy='socks5h://127.0.0.1:9150' ('tb' is an alias for the Tor browser)
ddgs text -q 'neurophysiology of the flickering light perception' -r cn-zh -m 5 -b google -b brave -pr tb

b) news:

query='etna eraption'
region='it'
language='it'
max_results=10
ddgs news -q 'etna eruption' -r it-it -m 10

c) books:

query='dolphins cousteau'
max_results=100
output='csv' (save as csv file)
ddgs books -q 'dolphins cousteau' -m 100 -o /tmp/books.csv

Go To TOP

DDGS search operators
Query example	Result
cats dogs	Results about cats or dogs
"cats and dogs"	Results for exact term "cats and dogs". If no results are found, related results are shown.
cats -dogs	Fewer dogs in results
cats +dogs	More dogs in results
cats filetype:pdf	PDFs about cats. Supported file types: pdf, doc(x), xls(x), ppt(x), html
dogs site:example.com	Pages about dogs from example.com
cats -site:example.com	Pages about cats, excluding example.com
intitle:dogs	Page title includes the word "dogs"
inurl:cats	Page url includes the word "cats"
