from django.core.paginator import Paginator
from django.shortcuts import render
from django.http import Http404, HttpResponseNotFound
import requests
from bs4 import BeautifulSoup
from django.template import loader
from django.http import HttpResponse



def index(request):
    data_list = []
    page_number = request.GET.get('page', 1)
    start_page = max(1, int(page_number) - 5)
    end_page = min(start_page + 9, 14)

    for page in range(start_page, end_page + 1):
        url = 'https://www.jumia.com.tn/mlp-telephone-tablette/smartphones/?page=' + \
            str(page)+'#catalog-listing'
        r = requests.get(url)
        soup = BeautifulSoup(r.content, "html.parser")
        Articles = soup.find_all(
            'article', {'class': 'prd _fb col c-prd'})

        for item in Articles:
            name = item.find('h3', {'class': 'name'}).text
  
            name = name.split('-')[0].strip()
            data = {
                'brand' : item.find('a', {'class': 'core'}).get('data-brand'),
                'name': name,
                'det': item.find('h3', {'class': 'name'}).text,
                'price': item.find('div', {'class': 'prc'}).text.strip().replace(',','').replace('TND',''),
                'image': item.find('div', {'class': 'img-c'}).find('img')['data-src'],
                'url': item.find('a', {'class': 'core'})['href'],
                'link' : item.find('a', {'class': 'core'}).get('href')
            }
            data_list.append(data)

    brand = request.GET.get('brand', None)
    max_price = request.GET.get('max_price', None)
    data_list = filter_smartphones(data_list, brand, max_price)

    paginator = Paginator(data_list, 9)
    page_obj = paginator.get_page(page_number)

    context = {
        'data_list': page_obj,
        'page_range': range(start_page, end_page + 1),
        'current_page': int(page_number),
         'brand': brand,
        'max_price': max_price,
        
    }
    

    return render(request, 'index.html', context)


def filter_smartphones(data_list, brand=None, max_price=None):
    # Filter based on brand if provided
    if brand:
        data_list = [s for s in data_list if s['name'].lower().startswith(brand.lower())]

    # Filter based on max price if provided
    if max_price:
        max_price = float(max_price)
        data_list = [s for s in data_list if float(s['price'].replace(',', '.')) <= max_price]

    return data_list



def smartphone_detail(request, name):
   
    # Send a request to the URL
    url = 'https://www.jumia.com.tn/'+name
    response = requests.get(url)
    Caracteristics = []
    technicalDescription = []
    Description = []
    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')
    #get the product
    product = soup.find('section', {'class': 'col12 -df -d-co'})
    
    #get the name of the product
    
    name = product.find('h1', {'class': '-fs20 -pts -pbxs'}).text
    
    image  = product.find('img', {'class': '-fw -fh'}).get('data-src')
    
    price = product.find('span', {'class': '-b -ltr -tal -fs24'}).text
    
    
    caracteristics = soup.find('div', {'class': 'markup -pam'}).find_all('li')
    for     caracteristic in caracteristics:
        Caracteristics.append(caracteristic.text)
        
    technicalDesc = soup.find('ul', {'class': '-pvs -mvxs -phm -lsn'}).find_all('li')
    for technical in technicalDesc:
        technicalDescription.append(technical.text)
        
        
    
    
    description = soup.find('div', {'class': 'markup -mhm -pvl -oxa -sc'})
    if description != None:
       
        # if there is no p tag in the description get the text from the div
        if description.find_all('p') == []:
            Description.append(description.text)
            
        else:
            description = description.find_all('p')
            for desc in description:
                Description.append(desc.text)
                   
    
    template = loader.get_template('smartphone_detail.html')
    context = {
        'name': name,
        'Caracteristics': Caracteristics,
        'technicalDescription': technicalDescription,
        'Description': Description,
        'image': image,
        'price': price,
    }
    return HttpResponse(template.render(context, request))







def product_details(request, url):
    r = requests.get(url)
    if r.status_code == 404:
        return HttpResponseNotFound('Product not found')
    soup = BeautifulSoup(r.content, "html.parser")

    # Extract the product details from the page using BeautifulSoup

    name = soup.find('h1', {'class': 'title'}).text
    price = soup.find('span', {'class': 'price'}).text
    description = soup.find('div', {'class': 'body'}).text

    context = {
        'name': name,
        'price': price,
        'description': description,
    }

    return render(request, 'product_details.html', context)
    