from urllib.parse import urlparse, urljoin
import re

str = '/ebook/test/fdadsadadsa23213231sdads?fr=booklist'
print(urlparse(str).path.split("/")[-1])
