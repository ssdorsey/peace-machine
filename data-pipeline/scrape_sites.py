

def parse_guardianng(html):
    '''
    GUARDIAN NIGERIA. site_url = "https://guardian.ng/sitemap.xml"
    example url: https://guardian.ng/news/putin-warns-of-consequences-over-orthodox-split/        
    '''
    hold_dict = {}    
    soup = BeautifulSoup(html, 'lxml')
    hold_dict['title'] = soup.find(class_=re.compile(r'after-category')).text.replace("\xa0", "") 
    author = soup.find(class_=re.compile(r'author')).text.strip().replace("By ", "")
    hold_dict['authors'] = author.split(',')[0] # remove cities or positions
    hold_dict['date'] = ' '.join(soup.find(class_=re.compile(r'manual-age')).text.split())
    hold_dict['image_urls'] = []
    hold_dict['image_captions'] = []
    if soup.article.find_all('img'):
        hold_dict['image_urls'] = [i['src'] for i in soup.article.find_all('img') if '/plugins/' not in i['src']]
        captions = soup.find_all(class_=re.compile(r'caption'))
        hold_dict['image_captions'] = list(set([c.text.strip() for c in captions]))
    body = soup.find('article').text 
    hold_dict['paragraphs'] =  list(filter(None, body.split('\n'))) # getting paragraphs indexed by line breaks; if by 'p', first par is lost. Remove potential empty ones.
    if hold_dict['image_captions']:
        hold_dict['paragraphs'][0] = hold_dict['paragraphs'][0].replace(hold_dict['image_captions'][0], '') #remove caption match
        hold_dict['paragraphs'] = list(filter(None,  hold_dict['paragraphs'])) # Remove empty ones. Important to do this again in case all caption was first par  
    return(hold_dict)

    
def parse_punch(html):
    '''
    PUNCH NIGERIA. site_url = "https://punchng.com/sitemap.xml"
    example url: https://punchng.com/nigerian-air-force-redeploys-27-air-marshals-45-senior-officers/
    '''
    hold_dict = {}    
    soup = BeautifulSoup(html, 'lxml')
    hold_dict['title'] = soup.find('h1', class_='post_title').text    
    hold_dict['authors'] = []
    if soup.article.find("strong"):
        hold_dict['authors'] = soup.article.find("strong").text.split(',')[0]
    if "Copyright PUNCH." in hold_dict['authors'] or "READ ALSO" in hold_dict['authors']:
        hold_dict['authors'] = []
    hold_dict['date'] = soup.find('time', class_=re.compile(r'entry-date published')).text   
    pars = [paragraph.text.strip() for paragraph in soup.find('div', class_='entry-content').find_all('p')] # there were some empty paragraphs        
    if len(pars)==0: 
        pars = soup.find('div', class_='col-md-12 col-lg-8').find_all('div')
        pars = [p.text.replace("\n","") for p in pars]  
    if hold_dict['authors']:
        if hold_dict['authors'] in pars[0]:
            pars = pars[1:len(pars)]
    hold_dict['paragraphs'] =  list(filter(None, pars)) # assign pars and remove empty ones
    if ('AFP' or 'Reuters' or 'NAN' or 'AP') in pars[len(pars)-1]:
        hold_dict['authors'] = pars[len(pars)-1].replace('(', '').replace(')', '')
    image_url = soup.find_all('div', class_='blurry')[0]['style']
    hold_dict['image_urls'] = image_url[image_url.find("(")+2:image_url.find(")")-1] # can't split here, have to substring
    hold_dict['image_captions'] = []
    if soup.find('span', class_='caption'):
        hold_dict['image_captions'] = soup.find('span', class_='caption').text              
    return(hold_dict)


def parse_vanguard(html):
    '''
    VANGUARD NIGERIA. site_url = "http://www.vanguardngr.com/sitemap_index.xml"
    example url: https://www.vanguardngr.com/2019/01/video-kwara-apcs-governorship-candidate-abdulrazaq-shuts-down-ilorin/
    '''
    hold_dict = {}    
    soup = BeautifulSoup(html, 'lxml')
    hold_dict['title'] = soup.find('h1', {'class': 'entry-title'}).text    
    if soup.find('time', {'class': 'entry-date published'}): # some don't have date
        hold_dict['date'] = soup.find('time', {'class': 'entry-date published'}).text
    else:
        hold_dict['date'] = soup.find('meta', property='article:published_time')['content'].split('T')[0]
    hold_dict['authors'] = []
    if soup.find('div', id="rtp-author-box"):
        hold_dict['authors'] = soup.find('div', id="rtp-author-box").find('h2').text # Is nested finds an elegant solution? 
    pars = [p.text for p in soup.find('article').find_all('p') if p.text is not ''] # there were some empty paragraphs
    if 'By' in str(pars[0:2]):     
        pos = int(np.where(["By" in s for s in pars[0:2]])[0])
        hold_dict['paragraphs'] = pars[pos+1:len(pars)]
        hold_dict['authors'] += ''.join(", " + pars[pos][3:len(pars[pos])])
    elif len(pars) is 0: 
        hold_dict['paragraphs'] = soup.find('article').text
    else:   
        hold_dict['paragraphs'] = pars
    if '\n' in hold_dict['authors']:
        hold_dict['paragraphs'] = [hold_dict['authors'].split('\n')[1]] + hold_dict['paragraphs']   
        hold_dict['authors'] = hold_dict['authors'].split('\n')[0]
    imgs = soup.article.find_all('img', class_=re.compile(r'size-full'))[1::2] # only odd elements. Even elements are irrelevant 
    hold_dict['image_urls'] = [s['src'] for s in imgs]
    if soup.find('figcaption'):
        hold_dict['image_captions'] = [c.text for c in soup.findAll('figcaption')]
    else:
        hold_dict['image_captions'] = []       
    return(hold_dict)


   
def parse_champion(html):
    '''
    CHAMPION NIGERIA. site_url = "http://www.championnews.com.ng/sitemap_index.xml"
    example url: "http://www.championnews.com.ng/inec-speaks-possibility-postponing-elections/"
    '''
    hold_dict = {}    
    soup = BeautifulSoup(html, 'lxml')
    hold_dict['title'] = soup.find('h1', {'class': 'entry-title'}).text
    hold_dict['date'] = soup.find('time', {'class':re.compile(r'entry-date')}).text
    body = soup.article.find_all('p')
    pars = [par.text for par in body]  
    if soup.find(class_=re.compile(r'caption')):
        hold_dict['image_captions'] = soup.find(class_=re.compile(r'caption')).text 
        pars = [par.split('\n') for par in pars if par != hold_dict['image_captions']]
        pars = sum(pars,[])
    else:
         hold_dict['image_captions'] = []
    if pars[0].split(' ')[0].isupper():
        hold_dict['author'] = pars[0].split(',')[0]
        hold_dict['paragraphs'] = [par.split('\n') for par in pars if hold_dict['author'] not in par]
    else:
        hold_dict['author'] = []
        hold_dict['paragraphs'] = [par.split('\n') for par in pars]
    if not hold_dict['paragraphs']:
        hold_dict['paragraphs'] = pars
    hold_dict['image_urls'] = []
    if soup.article.find('img', {'class':'entry-thumb'}):
        hold_dict['image_urls'] = soup.article.find('img', {'class':'entry-thumb'})['src']
    return(hold_dict)
   
    


def parse_tribune(html):
    '''
    TRIBUNE NIGERIA. site_url = "https://www.tribuneonlineng.com/sitemap_index.xml"
    example url: https://www.tribuneonlineng.com/172684/
    Body of text should be cleaner at bottom, but the page is really inconsistent 
    '''
    hold_dict = {}    
    soup = BeautifulSoup(html, 'lxml')
    hold_dict['title'] = soup.find(class_=re.compile(r'post-title')).text     
    hold_dict['authors'] = soup.find(class_=re.compile(r'author')).text.strip().replace("By ", "").split(' -')[0]    
    hold_dict['date'] = soup.time.find('b').text
    article_body = soup.find('article').find_all('p')
    pars = [paragraph.text.strip() for paragraph in article_body]   
    hold_dict['paragraphs'] = [p.replace('\xa0', '') for p in pars if p is not '']
    if soup.article.find_all('img'):
        names = [i['data-src'] for i in soup.article.find_all('img')]
        hold_dict['image_urls'] = list(set(names))
        captions = soup.find_all(class_=re.compile(r'caption'))
        captions = list(set([c.text.strip() for c in captions]))
        hold_dict['image_captions'] = [c for c in captions if c is not '']
    else: 
        hold_dict['image_urls'] = []
        hold_dict['image_captions'] = []
    return(hold_dict)
    



def parse_sahararep(html):
    '''
    SAHARA REPORTERS NIGERIA. site_url = "http://saharareporters.com/sitemap.xml"
    example url: http://saharareporters.com/2006/10/22/fayose-lagos-plot-return-him-power-thickens
    Very hacky addressing issues
    '''
    hold_dict = {}    
    soup = BeautifulSoup(html, 'lxml')
    hold_dict['title'] = soup.find('title').text.strip().split(' By')[0].split('|')[0].split('-')[0].encode('ascii', 'ignore').decode()
    author = soup.find('span', {'class':re.compile(r'attribution')}).text.replace("By ", "").replace("by ", "")
    hold_dict['authors'] = author.encode('ascii', 'ignore').decode() 
    hold_dict['date'] = soup.find('span', {'class':re.compile(r'date')}).text.strip()
    article_body = soup.find('div', {'class':'story-content'})
    pars = [p.text.strip() for p in article_body.find_all('p')]
    hold_dict['paragraphs'] = list(filter(None, pars))
    hold_dict['image_urls'] = [] # No captions in any link I've explored
    if soup.find('div', {'class':'story-content'}).find('img'):
        hold_dict['image_urls'] = soup.find('div', {'class':'story-content'}).find('img')['src']
    hold_dict['image_captions'] = [] 
    if 'Saharareporters' in hold_dict['paragraphs'][0]:
        hold_dict['paragraphs'] = hold_dict['paragraphs'][1:len(hold_dict['paragraphs'])]
    if 'By' in str(hold_dict['paragraphs'][0:2]):     
        pars = hold_dict['paragraphs']
        pos = int(np.where(["By" in s for s in pars[0:2]])[0])
        hold_dict['paragraphs'] = pars[pos+1:len(pars)]
        hold_dict['authors'] += ''.join(", " + pars[pos][3:len(pars[pos])].encode('ascii', 'ignore').decode('utf-8'))
    hold_dict['paragraphs'] = [p.replace(u'\xa0', u' ') for p in hold_dict['paragraphs']]
    return(hold_dict)
         



    
def parse_sun(html):
    '''
    THE SUN NIGERIA. site_url = "https://www.sunnewsonline.com/sitemap-index-1.xml"
    example url: https://www.sunnewsonline.com/unilag-student-sets-new-record-graduates-with-5-cgpa
    '''
    hold_dict = {}    
    soup = BeautifulSoup(html, 'lxml')
    hold_dict['title'] = soup.find('h1', {'class':re.compile(r'title')}).text
    hold_dict['date'] = soup.find('div', {'class':re.compile(r'date')}).text.strip()
    hold_dict['authors'] = soup.find('h3', {'class':re.compile(r'jeg_author_name')}).text.strip()
    article_body = soup.find('div', {'class':'content-inner'})
    pars = [p.text.encode('ascii', 'ignore').decode().split('\n') for p in article_body.find_all('p')]
    hold_dict['paragraphs'] = [y for x in pars for y in x] #flatten list of lists
    hold_dict['image_urls'] = []
    try:
        hold_dict['image_urls'] = soup.find('div', {'class':'jeg_inner_content'}).find('img')['data-src']
    except:
        pass
    hold_dict['image_captions'] = [] # no captions in many links I looked at
    preps = ['From', 'By', 'BY']
    if any([prep in str(hold_dict['paragraphs'][0:4]) for prep in preps]) and len(hold_dict['paragraphs'])>=4:       
        pars = hold_dict['paragraphs'] # just to make code more legible
        pos = np.where([prep in str(s) for s in pars[0:4] for prep in preps])[0][0]
        pos = int(np.where(pos<=2, 0, 
                           (np.where(pos>2 and pos<=5, 1, 
                                     (np.where(pos>5 and pos<=8,2,3))))))
        hold_dict['paragraphs'] = pars[pos+1:len(pars)]
        author = ' '.join(pars[pos].split(" ")[1:3]).replace(',','').replace('-','')
        hold_dict['authors'] += ''.join(', ' + author)
    if 'Source:' in str(hold_dict['paragraphs'][0]) and len(hold_dict['paragraphs'])>2:
        hold_dict['paragraphs'] = hold_dict['paragraphs'][1:len(hold_dict['paragraphs'])]
    return(hold_dict)   
    



