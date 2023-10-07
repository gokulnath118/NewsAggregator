from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
import requests
from bs4 import BeautifulSoup
import lxml

# GEtting news from Times of India
def getIndia():
    toi_r = requests.get("https://timesofindia.indiatimes.com/briefs")
    toi_soup = BeautifulSoup(toi_r.content, 'lxml')
    toi_img=toi_soup.find_all("div",class_="posrel")
    
    toi_headings = toi_soup.find_all('h2')
    toi_headings = toi_headings[2:-13] # removing footers
    toi_news = []
    for th,img in zip(toi_headings,toi_img):
        a=th.find('a',href=True)
        image=img.find("img")['data-src']
        toi_news.append([th.text,a['href'],image])
    return toi_news



#Getting news from nd tv
def getWorld():
    url="https://www.ndtv.com/world-news/"
    ht_r = requests.get(url)
    ht_soup = BeautifulSoup(ht_r.content, 'lxml')
    ht_pages = int(ht_soup.find("div",class_="listng_pagntn clear").find_all("a")[-2].get_text())   
    ht_news = []
    i=1
    while True:
        ht_headings = ht_soup.find_all("h2", class_="newsHdng")
        ht_images = ht_soup.find_all("div", class_="news_Itm-img")
        for hth,img in zip(ht_headings,ht_images):
            a=hth.find('a',href=True)
            image=img.find('a').find('img')
            ht_news.append([hth.text,a['href'],image['src']])
        if i == ht_pages:
            break
        i+=1
        ht_r = requests.get(url+"page-"+str(i))
        ht_soup = BeautifulSoup(ht_r.content, 'lxml')
    return ht_news


def getIndiaOne(url):
    # print(url)
    one_r = requests.get('https://timesofindia.indiatimes.com/'+url)
    one_soup = BeautifulSoup(one_r.content, 'lxml')
    one_content=one_soup.find("div",class_="_s30J")
    one_head=one_soup.find("h1",class_="HNMDR").get_text()
    one_img=(one_soup.find("div",class_="wJnIp") or one_soup.find("div",class_="LVN95")).find('img')['src']
    for br in one_content.select("br"):
        br.replace_with("\n")
    return (one_head,one_content.get_text(),one_img)


def getWorldOne(url):
    # print(url)
    one_r = requests.get(url)
    one_soup = BeautifulSoup(one_r.content, 'lxml')
    l_content=((one_soup.find("div",class_="sp-cn ins_storybody")).find_all('p'))
    one_content=""
    for i in l_content:
        temp=i.get_text()
        one_content+=temp if temp !="" else '\n'
    one_head=one_soup.find("h1",class_="sp-ttl").get_text()
    one_img=one_soup.find("div",class_="ins_instory_dv_cont").find('img')  or one_soup.find("div",class_="ins_instory_dv").find('meta',{"itemprop":"thumbnailUrl"})
    if one_img.has_attr('src'):
        one_img=one_img['src']
    else:
        one_img=one_img['content']
    # for br in one_content.select("br"):
    #     br.replace_with("\n")
    return (one_head,one_content,one_img)
    # one_content.get_text()

def index(req,id=None):
    if req.method == "POST" and id:
        l=req.POST.get("fetch", "")
        # print(l)
        # print(l)
        if id==1:
        #     # print(getIndiaOne(l[1]))
        #     return render(req, 'news/onenews.html', {'h1':l[0],'oneContent':getIndiaOne(l),'imgUrl':l[2]})
        #     # return render(req, 'news/index.html', {'toi_news':getIndia(), 'ht_news': []})
            heading,content,img=getIndiaOne(l)
        if id==2:
            heading,content,img=getWorldOne(l)

        return render(req,'news/onenews.html',{'h1':heading,'oneContent':content.split('\n'),'imgUrl':img})
    else:
        if id==1:
           return render(req, 'news/index.html', {'toi_news':getIndia(), 'ht_news': []})
        elif id==2:
            return render(req, 'news/index.html', {'toi_news':[], 'ht_news': getWorld()})
        else:
            return render(req, 'news/index.html', {'toi_news':getIndia(), 'ht_news': getWorld()})
    


@login_required(login_url='login')
def HomePage(request):
    return render (request,'news/index.html')

def SignupPage(request):
    if request.method=='POST':
        uname=request.POST.get('username')
        email=request.POST.get('email')
        pass1=request.POST.get('password1')
        pass2=request.POST.get('password2')
        if pass1!=pass2:
            return HttpResponse("Your password and confrom password are not Same!!")
        else:
            my_user=User.objects.create_user(uname,email,pass1)
            my_user.save()
            return redirect('login')
    return render (request,'signup.html')

def LoginPage(request):
    if request.method=='POST':
        username=request.POST.get('username')
        pass1=request.POST.get('pass')
        user=authenticate(request,username=username,password=pass1)
        if user is not None:
            login(request,user)
            return redirect('index')
        else:
            return HttpResponse ("Username or Password is incorrect!!!")

    return render (request,'login.html')

def LogoutPage(request):
    return render (request,'login.html')

        


