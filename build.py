#!/usr/bin/env python3
"""Build the complete, crawlable Entwistle Paving site using Python's standard library."""
from pathlib import Path
from html import escape
from urllib.parse import quote
import json
import shutil
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'dist'
ORIGIN = 'https://entwistlepaving.co.uk'
NAME = 'George Entwistle Driveways & Paving'
PHONE = '07581 223870'
EMAIL = 'george_entwistle@hotmail.co.uk'
PHOTOS = json.loads((ROOT / 'content/photos.json').read_text())
SERVICES = json.loads((ROOT / 'content/services.json').read_text())
PHOTO = {p['slug']: p for p in PHOTOS}
ARROW = '<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M4 12h15m-6-6 6 6-6 6"/></svg>'

def e(value):
    return escape(str(value), quote=True)

def image(slug, sizes='(max-width: 640px) 100vw, 50vw', cls='', eager=False, thumb=False):
    p = PHOTO[slug]
    variants = sorted(p['thumbnails'] if thumb else p['variants'], key=lambda v: v['width'])
    default = min(variants, key=lambda v: abs(v['width'] - 960))
    srcset = ', '.join('/assets/photos/' + v['src'] + ' ' + str(v['width']) + 'w' for v in variants)
    priority = 'fetchpriority="high"' if eager else 'fetchpriority="low"'
    width, height = (default['width'],default['height']) if thumb else (p['width'],p['height'])
    return f'<img src="/assets/photos/{e(default["src"])}" srcset="{e(srcset)}" sizes="{e(sizes)}" width="{width}" height="{height}" alt="{e(p["alt"])}" class="{e(cls)}" loading="{"eager" if eager else "lazy"}" decoding="async" {priority}>'

def button(label, href='/contact/', style=''):
    return f'<a class="button {style}" href="{e(href)}">{e(label)}{ARROW}</a>'

NAV = [('Home', '/'), ('Services', '/services/'), ('Our work', '/gallery/'), ('About', '/about/'), ('Reviews', '/testimonials/')]
def header(path):
    links = ''.join(f'<a class="nav-link" href="{url}"' + (' aria-current="page"' if path == url or (url == '/services/' and path.startswith('/services/')) else '') + f'>{label}</a>' for label, url in NAV)
    return f'''<a class="skip" href="#main">Skip to content</a>
    <div class="topbar"><div class="wrap"><span class="coverage">Colne · Burnley · Pendle · Barnoldswick · Skipton</span><a href="tel:+447581223870">Call {PHONE}</a></div></div>
    <header class="site-header"><div class="wrap nav-wrap"><a class="brand" href="/" aria-label="{NAME} home"><img src="/assets/logo.png" width="1294" height="445" alt="{NAME}" loading="eager"></a>
    <button class="menu-toggle" type="button" data-menu-toggle aria-controls="main-navigation" aria-expanded="false" aria-label="Open navigation"><span></span><span></span><span></span></button>
    <nav class="nav" id="main-navigation" data-nav aria-label="Main navigation">{links}{button('Free quote')}</nav></div></header>'''

SERVICE_INFO = {
    'driveways': ('Driveways', 'Tarmac, resin and block paving options for a practical, welcoming entrance.', 'finished-block-paved-driveway-wide'),
    'block-paving': ('Block paving', 'Thoughtful patterns, neat borders and paving shaped around your property.', 'block-paved-driveway-house-16'),
    'patios': ('Patios & garden paving', 'Indian stone, porcelain and paving to make more of your outdoor space.', 'grey-paved-patio-seating-area'),
    'landscaping': ('Garden landscaping', 'Bring patios, lawns, paths and changes of level together in one plan.', 'landscaped-garden-patio-and-lawn'),
    'fencing': ('Fencing & boundaries', 'Timber fencing and screening to finish and define your garden.', 'wooden-fence-garden-backyard'),
}

def cta():
    return f'<section class="cta"><div class="wrap"><div><h2>Let’s make more of your outside space.</h2><p>Tell George what you have in mind. Arrange a free site visit and a no-obligation quote.</p></div>{button("Let’s talk", "/contact/", "light")}</div></section>'

def footer():
    links = ''.join(f'<li><a href="/services/{slug}/">{e(info[0])}</a></li>' for slug, info in SERVICE_INFO.items())
    return f'''<footer class="site-footer"><div class="wrap"><div class="footer-grid">
    <div><a href="/" aria-label="{NAME} home"><img class="footer-logo" src="/assets/logo.png" width="1294" height="445" loading="lazy" alt="{NAME}"></a><p>Driveways, patios and thoughtfully finished gardens. Based in Colne, working across Pendle and the surrounding areas.</p></div>
    <div><h3>What we do</h3><ul>{links}</ul></div>
    <div><h3>Explore</h3><ul><li><a href="/about/">Meet George & the team</a></li><li><a href="/gallery/">Project gallery</a></li><li><a href="/testimonials/">Customer feedback</a></li><li><a href="/areas/">Areas we cover</a></li><li><a href="/contact/">Get a free quote</a></li></ul></div>
    <div><h3>Start your project</h3><a class="footer-phone" href="tel:+447581223870">{PHONE}</a><a class="footer-email" href="mailto:{EMAIL}">{EMAIL}</a><p>Based in Colne, Lancashire<br>Site visits by arrangement</p></div></div>
    <div class="footer-bottom"><span>© 2026 {NAME}</span><span>Website by <a href="https://madereal.uk/" target="_blank" rel="noopener">MadeReal</a></span></div></div></footer>
    <div class="mobile-call" aria-label="Quick contact">{button('Call George', 'tel:+447581223870')}{button('Free quote', '/contact/', 'outline')}</div>'''

def lightbox():
    return '''<dialog class="lightbox" data-lightbox aria-labelledby="photo-title"><div class="lightbox-top"><p id="photo-title" data-lightbox-title></p><button type="button" data-close aria-label="Close photo">✕</button></div><img class="lightbox-image" alt=""><div class="lightbox-bottom"><button type="button" data-prev aria-label="Previous photo">←</button><span data-lightbox-position aria-live="polite"></span><button type="button" data-next aria-label="Next photo">→</button></div></dialog>'''

PAGES = []
def write_page(path, title, description, body, breadcrumbs=None, extra_schema=None, noindex=False, hero=None):
    url = ORIGIN + path
    social_photo = PHOTO[hero or 'finished-block-paved-driveway-wide']
    social = ORIGIN + '/assets/photos/' + max(social_photo['variants'], key=lambda v:v['width'])['src']
    graph = [
        {'@type':'WebSite','@id':ORIGIN+'/#website','url':ORIGIN+'/','name':NAME,'inLanguage':'en-GB'},
        {'@type':'HomeAndConstructionBusiness','@id':ORIGIN+'/#business','name':NAME,'url':ORIGIN+'/','image':social,'logo':ORIGIN+'/assets/logo.png','telephone':'+447581223870','email':EMAIL,'address':{'@type':'PostalAddress','addressLocality':'Colne','addressRegion':'Lancashire','addressCountry':'GB'},'areaServed':[{'@type':'Place','name':n} for n in ['Colne','Burnley','Pendle','Barnoldswick','Skipton']]},
        {'@type':'WebPage','@id':url+'#webpage','url':url,'name':title,'description':description,'isPartOf':{'@id':ORIGIN+'/#website'},'about':{'@id':ORIGIN+'/#business'},'inLanguage':'en-GB'}
    ]
    if breadcrumbs:
        graph.append({'@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':i+1,'name':name,'item':ORIGIN+href} for i,(name,href) in enumerate(breadcrumbs)]})
    if extra_schema:
        graph.extend(extra_schema)
    html = f'''<!doctype html><html lang="en-GB"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(title)}</title><meta name="description" content="{e(description)}"><meta name="robots" content="{'noindex,follow' if noindex else 'index,follow,max-image-preview:large'}"><link rel="canonical" href="{url}"><meta name="theme-color" content="#292328"><link rel="icon" href="/assets/favicon.svg" type="image/svg+xml"><link rel="alternate icon" href="/assets/favicon-48x48.png" type="image/png"><link rel="apple-touch-icon" href="/assets/apple-touch-icon.png"><link rel="manifest" href="/site.webmanifest"><link rel="preload" href="/assets/manrope-latin.woff2" as="font" type="font/woff2" crossorigin><link rel="stylesheet" href="/assets/site.css?v=20261109"><script defer src="/assets/site.js?v=20261109"></script><meta property="og:locale" content="en_GB"><meta property="og:type" content="website"><meta property="og:site_name" content="{NAME}"><meta property="og:url" content="{url}"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(description)}"><meta property="og:image" content="{e(social)}"><meta property="og:image:alt" content="{e(social_photo['alt'])}"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{e(title)}"><meta name="twitter:description" content="{e(description)}"><meta name="twitter:image" content="{e(social)}"><script type="application/ld+json">{json.dumps({'@context':'https://schema.org','@graph':graph},ensure_ascii=False).replace('<','<'.replace('<', chr(92)+'u003c'))}</script></head><body>{header(path)}<main id="main">{body}</main>{footer()}{lightbox()}</body></html>'''
    destination = OUT / (path.strip('/') + '/index.html' if path != '/' else 'index.html')
    if path == '/404.html':
        destination = OUT / '404.html'
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(html)
    if not noindex:
        PAGES.append((path, title))

def page_head(label, heading, intro, path, parent=None):
    crumb = '<a href="/">Home</a><span>/</span>'
    if parent:
        crumb += f'<a href="{parent[1]}">{e(parent[0])}</a><span>/</span>'
    crumb += e(label)
    return f'<section class="page-head"><div class="wrap"><div class="breadcrumb" aria-label="Breadcrumb">{crumb}</div><span class="eyebrow">{e(label)}</span><h1>{e(heading)}</h1><p class="lead">{e(intro)}</p></div></section>'

def photo_card(p):
    largest = max(p['variants'], key=lambda v:v['width'])
    return f'''<figure class="photo-card" data-photo-card data-category="{e(p['category'])}"><a class="photo-button" data-photo-link href="/assets/photos/{e(largest['src'])}" data-alt="{e(p['alt'])}" data-caption="{e(p['caption'])}" aria-label="Enlarge: {e(p['caption'])}">{image(p['slug'], '(max-width:740px) 50vw, 380px',thumb=True)}<span class="enlarge" aria-hidden="true">+</span></a><figcaption><small>{e(p['category'])}</small>{e(p['caption'])}</figcaption></figure>'''

def project_grid(slugs):
    return '<div class="project-grid">' + ''.join(photo_card(PHOTO[s]) for s in slugs) + '</div>'

def service_cards():
    cards = ''
    for slug,(title,desc,photo) in SERVICE_INFO.items():
        cards += f'<article class="service-card"><a href="/services/{slug}/" aria-label="Explore {e(title)}">{image(photo, "(max-width:420px) 100vw, (max-width:740px) 50vw, 380px",thumb=True)}</a><div class="card-body"><h3><a href="/services/{slug}/">{e(title)}</a></h3><p>{e(desc)}</p><a class="text-link" href="/services/{slug}/">Explore {e(title.lower())}<span aria-hidden="true">↗</span></a></div></article>'
    return '<div class="service-grid">' + cards + '</div>'

REVIEWS = [
    ('Ian Harvey','George and his team did a brilliant job on my patio. Great price too, anybody looking for a reliable company I would highly recommend.'),
    ('Abigail Roscoe','George and his team did an amazing job transforming our patio. We are so happy with the work and could not fault them at all. Would highly recommend them to anyone!'),
    ('John and Rosalyn','George and his team, Brian and Lloyd, did an excellent job on our drive recently, we have nothing but praise for their hard work, pride in their job and politeness - we would certainly recommend them to anyone. This is the second job they have completed for us, again carried out to a high standard. Thank you all, good luck for the future.'),
    ('Nicola Laycock','5 Stars. Excellent service and quality.'),
]
def reviews(count=2):
    return '<div class="reviews-grid">' + ''.join(f'<blockquote class="review"><span class="quote-mark" aria-hidden="true">“</span><p>{e(text)}</p><footer>{e(name)}<span>Customer feedback</span></footer></blockquote>' for name,text in REVIEWS[:count]) + '</div>'

def areas():
    return '<div class="area-list">' + ''.join(f'<span>{town}</span>' for town in ['Colne','Burnley','Pendle','Barnoldswick','Skipton']) + '</div>'

def faq(items):
    return '<div class="faq-list">' + ''.join(f'<details><summary>{e(item["q"])}</summary><p>{e(item["a"])}</p></details>' for item in items) + '</div>'

def build():
    PAGES.clear()
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(ROOT/'assets', OUT/'assets')
    home = f'''<section class="hero"><div class="wrap hero-grid"><div class="hero-copy"><span class="eyebrow">George Entwistle · Driveways & Paving</span><h1>Driveways & paving<br>in <em>Colne.</em></h1><p>Driveways, patios and paving in Colne, Burnley and Pendle. Thoughtfully planned, carefully laid, and made for everyday life.</p><div class="actions">{button('Arrange a free quote')}{button('Explore our work','/gallery/','outline')}</div><div class="hero-bottom"><span>Based in Colne</span><span>Free site visits</span><span>No-obligation quotes</span></div></div><div class="hero-image">{image('finished-block-paved-driveway-wide','(max-width:640px) 100vw, 55vw',eager=True)}<div class="image-note"><span class="note-number" aria-hidden="true">GE.</span><div><small>Real work. Considered details.</small><strong>Block paving, finished with care.</strong></div></div></div></div></section>
    <div class="trust"><div class="wrap"><div class="trust-item"><strong>Your local paving team</strong>Colne & surrounding areas</div><div class="trust-item"><strong>Made around your home</strong>Practical advice & design</div><div class="trust-item"><strong>From groundwork to finish</strong>One considered plan</div><div class="trust-item"><strong>Start with a conversation</strong>Speak directly with George</div></div></div>
    <section class="section"><div class="wrap"><div class="section-heading"><div><span class="eyebrow">Our services</span><h2>Good groundwork.<br>Beautiful results.</h2></div><p>From a new entrance to a place to sit out in the garden, we help bring the whole space together.</p></div>{service_cards()}</div></section>
    <section class="section white"><div class="wrap split">{image('grey-paved-patio-seating-area',cls='split-photo')}<div class="split-copy"><span class="eyebrow">Built around you</span><h2>Make room for<br>more outside.</h2><p>A driveway needs to work as well as it looks. A patio should feel like a natural extension of your home. We start by understanding how you use the space, then talk through materials, layout and the finishing details.</p><p>George Entwistle Driveways & Paving is based in Colne, serving homeowners across Burnley, Pendle, Barnoldswick and Skipton.</p><ul class="check-list"><li>Driveways in tarmac, resin and block paving</li><li>Patios, paths and practical garden layouts</li><li>Fencing and landscaping to complete the space</li></ul><a class="text-link" href="/about/">A little more about us <span aria-hidden="true">↗</span></a></div></div></section>
    <section class="section"><div class="wrap"><div class="section-heading"><div><span class="eyebrow">The latest from our work</span><h2>The details make<br>the difference.</h2></div><a class="text-link" href="/gallery/">See all 37 photos <span aria-hidden="true">↗</span></a></div>{project_grid(['charcoal-block-paved-driveway-house','garden-paving-steps-raised-patio','stone-paved-entrance-lawn-edge'])}</div></section>
    <section class="section process"><div class="wrap"><div class="section-heading"><div><span class="eyebrow">From an idea to your doorstep</span><h2>A clear path to your<br>next project.</h2></div><p>A conversation, a proper look at your site, and a plan that makes sense for your home.</p></div><div class="process-grid"><div><span class="process-number">01</span><h3>Tell us what you need.</h3><p>Call or email George with your ideas, the area you want to improve and any photos of the space.</p></div><div><span class="process-number">02</span><h3>Look at the possibilities.</h3><p>Arrange a free site visit to discuss the layout, ground levels, material options and your priorities.</p></div><div><span class="process-number">03</span><h3>Agree the work.</h3><p>Review your no-obligation quote and discuss the scope, access and timing before the project begins.</p></div></div></div></section>
    <section class="section"><div class="wrap"><div class="section-heading"><div><span class="eyebrow">What our customers say</span><h2>Happy with the finish.<br>Happy to recommend.</h2></div><a class="text-link" href="/testimonials/">Read customer feedback <span aria-hidden="true">↗</span></a></div>{reviews()}</div></section>
    <section class="section white"><div class="wrap split"><div><span class="eyebrow">Local to you</span><h2>Based in Colne.<br>Working across the area.</h2><p class="muted">We carry out driveway, patio, paving and landscaping projects in Colne, Burnley, Pendle, Barnoldswick and Skipton. Get in touch to check availability for your address.</p>{areas()}</div><div><h3>A new driveway or patio in mind?</h3><p class="muted">Send a few photographs and tell us what you would like to change. We can arrange a visit and help you explore the options.</p>{button('Check your area','/areas/','outline')}</div></div></section>{cta()}'''
    write_page('/', 'Driveways & Paving in Colne & Burnley | George Entwistle', 'George Entwistle Driveways & Paving: driveways, patios, block paving, landscaping and fencing in Colne, Burnley and Pendle. Call for a free site visit.', home)

    body = page_head('Services','Driveways, patios and gardens that work for you.','Explore our paving and landscaping services in Colne, Burnley, Pendle, Barnoldswick and Skipton. Start with the part of your property you would like to improve.','/services/')
    body += f'<section class="section"><div class="wrap">{service_cards()}<div class="info-box"><h3>Planning more than one improvement?</h3><p>Driveways, paths, fencing and garden levels often need to work together. Talk us through the whole space at your site visit so we can consider the practical details as part of one plan.</p></div></div></section>{cta()}'
    write_page('/services/','Paving & Landscaping Services in Colne | George Entwistle','Explore driveway installation, block paving, patios, garden landscaping and fencing in Colne, Burnley and Pendle. Free site visits and no-obligation quotes.',body,[('Home','/'),('Services','/services/')])

    for slug, data in SERVICES.items():
        name,desc,photo = SERVICE_INFO[slug]
        path = '/services/'+slug+'/'
        sections = ''.join(f'<h2>{e(s["heading"])}</h2><p>{e(s["body"])}</p>' for s in data['sections'])
        related = ''.join(f'<li><a href="/services/{key}/">{e(info[0])} <span aria-hidden="true">↗</span></a></li>' for key,info in SERVICE_INFO.items() if key != slug)
        projects = [p['slug'] for p in PHOTOS if p['category'] == ('Driveways' if slug in ['driveways','block-paving'] else {'patios':'Patios','landscaping':'Landscaping','fencing':'Fencing'}[slug])][:3]
        if slug == 'block-paving':
            projects = ['finished-block-paved-driveway-wide','block-paved-driveway-house-16','block-paved-driveway-curved-doorstep']
        content = page_head(name,data['h1'],data['intro'],path,('Services','/services/'))
        content += f'<section class="section"><div class="wrap content-layout"><article>{image(photo,cls="service-feature",eager=True)}{sections}<h2>Things to consider before your site visit</h2><ul class="check-list">'+''.join(f'<li>{e(s)}</li>' for s in data['considerations'])+f'</ul><h2>Your questions, answered</h2>{faq(data["faqs"])}</article><aside class="service-aside"><span class="eyebrow">Start with a site visit</span><h2>Let’s talk about your project.</h2><p>Tell George what you have in mind. Free site visits and no-obligation quotes across Colne and the surrounding areas.</p>{button("Call "+PHONE,"tel:+447581223870")}{button("Send an enquiry","/contact/","outline")}<h3 style="margin-top:30px">Explore our services</h3><ul>{related}</ul></aside></div></section>'
        content += f'<section class="section white"><div class="wrap"><div class="section-heading"><div><span class="eyebrow">Our work</span><h2>Take a closer look.</h2></div><a class="text-link" href="/gallery/">Explore the full gallery <span aria-hidden="true">↗</span></a></div>{project_grid(projects)}</div></section>{cta()}'
        schema = [{'@type':'Service','@id':ORIGIN+path+'#service','name':name,'serviceType':name,'url':ORIGIN+path,'provider':{'@id':ORIGIN+'/#business'},'areaServed':['Colne','Burnley','Pendle','Barnoldswick','Skipton'],'description':data['description']}]
        write_page(path,data['title'],data['description'],content,[('Home','/'),('Services','/services/'),(name,path)],schema,hero=photo)

    body = page_head('Our work','Real projects. Every detail.','Browse driveway, patio, garden and fencing photos from our work. Select a category, then open any image for a closer look.','/gallery/')
    filters = ''.join(f'<button type="button" data-filter="{cat}" aria-pressed="{str(cat=="All").lower()}">{cat if cat != "All" else "All photos"}</button>' for cat in ['All','Driveways','Patios','Landscaping','Fencing'])
    gallery = ''.join(photo_card(p) for p in PHOTOS)
    body += f'<section class="section"><div class="wrap"><div class="filters" data-gallery-filters hidden role="group" aria-label="Filter project photos">{filters}</div><p class="gallery-count" data-gallery-count aria-live="polite">{len(PHOTOS)} photos · including our latest driveway and garden work</p><div class="gallery-grid">{gallery}</div><div class="info-box"><h3>Seen something you like?</h3><p>Tell us which finish or detail caught your eye. We can discuss how a similar idea could work at your own property.</p>{button("Discuss your ideas")}</div></div></section>{cta()}'
    write_page('/gallery/','Driveway, Patio & Garden Photo Gallery | Entwistle Paving','Explore 37 real photos of block paved and tarmac driveways, garden patios, landscaping and timber fencing from George Entwistle Driveways & Paving.',body,[('Home','/'),('Gallery','/gallery/')])

    body = page_head('About us','A local team. A considered approach.','George Entwistle Driveways & Paving is based in Colne, creating driveways, patios and garden spaces across Pendle and the surrounding areas.','/about/')
    body += f'<section class="section white"><div class="wrap split">{image("garden-patio-lawn-landscaping",cls="split-photo",eager=True)}<div class="split-copy"><span class="eyebrow">George Entwistle Driveways & Paving</span><h2>Good spaces start with understanding the details.</h2><p>The way you arrive home. The route from the back door to the garden. Somewhere to sit, park or gather. These everyday details are where a paving project starts.</p><p>We work on driveways, block paving, Indian stone and porcelain patios, fencing and garden landscaping. We look at how the different parts of your property fit together, from groundwork and drainage to borders, paths and the final finish.</p><p>Speak directly with George about your plans. A free site visit gives us a chance to see the space and discuss practical options before you decide.</p>{button("Speak to George")}</div></div></section><section class="section"><div class="wrap"><div class="section-heading"><div><span class="eyebrow">What matters</span><h2>A space you will use.<br>A finish you will enjoy.</h2></div><p>Our focus is simple: understand what you need, plan the work carefully and pay attention to the finishing details.</p></div><div class="process-grid"><div><h3>Practical planning</h3><p class="muted">Access, ground levels, water run-off and how you use the property all shape the right layout.</p></div><div><h3>Materials that suit</h3><p class="muted">We discuss colour, finish, upkeep and the look of your home so you can make an informed choice.</p></div><div><h3>The whole space</h3><p class="muted">Paths, edges, steps, fencing and lawns deserve the same care as the main paved area.</p></div></div></div></section>{cta()}'
    write_page('/about/','About George Entwistle Driveways & Paving | Colne','Meet George Entwistle Driveways & Paving, based in Colne. Driveways, patios, landscaping and fencing across Burnley, Pendle, Barnoldswick and Skipton.',body,[('Home','/'),('About','/about/')])

    body = page_head('Customer feedback','Recommended by the people we work for.','A selection of customer comments shared on our website, about driveway and patio projects completed by George and the team.','/testimonials/')
    body += f'<section class="section"><div class="wrap">{reviews(4)}<div class="info-box"><p>Thinking about your own project? Take a look through our work and get in touch to discuss what you would like to achieve.</p><div class="actions">{button("View our work","/gallery/","outline")}{button("Talk to George")}</div></div></div></section>{cta()}'
    write_page('/testimonials/','Customer Reviews | George Entwistle Driveways & Paving','Read customer feedback about George Entwistle Driveways & Paving. Explore our driveway and patio work, then contact George for a free site visit and quote.',body,[('Home','/'),('Customer feedback','/testimonials/')])

    body = page_head('Contact George','Your next project starts here.','A new driveway, a garden patio or a bigger change outdoors? Call or email George to arrange a free site visit and a no-obligation quote.','/contact/')
    mail = 'mailto:'+EMAIL+'?subject='+quote('Driveway / patio enquiry')+'&body='+quote('Hello George,\n\nI would like to discuss a project.\n\nMy name:\nLocation / postcode:\nType of work:\nApproximate size:\nPreferred contact number:\n\nThank you')
    body += f'<section class="section"><div class="wrap contact-grid"><div class="contact-card"><span class="eyebrow">Get in touch</span><h2>Let’s see what’s possible.</h2><p class="muted">Speak directly to George about your ideas, material choices and arranging a visit.</p><div class="contact-detail"><strong>Call George</strong><a href="tel:+447581223870">{PHONE}</a></div><div class="contact-detail"><strong>Email your enquiry</strong><a class="email" href="mailto:{EMAIL}">{EMAIL}</a></div><div class="contact-detail"><strong>Where we work</strong><p>Based in Colne. Covering Burnley, Pendle, Barnoldswick, Skipton and nearby areas.</p></div>{button("Start an email enquiry",mail)}</div><div>{image("grey-paved-patio-seating-area",cls="contact-image",eager=True)}<h3>A little detail helps us get started.</h3><ul class="check-list"><li>Your postcode or the location of the property</li><li>What you would like to change or improve</li><li>A rough size and a few photos, if you have them</li><li>Your preferred materials or examples you like</li></ul><p class="muted">Not sure where to start? Give George a call. We can talk through the options at your site visit.</p></div></div></section>'
    body += '<section class="section white"><div class="wrap"><div class="section-heading"><div><span class="eyebrow">Before we visit</span><h2>A few useful answers.</h2></div></div>'+faq([{'q':'Is the quote free?','a':'Yes. Contact George to arrange a free site visit and a no-obligation quote for your project.'},{'q':'Can I send photos first?','a':'Yes. Email photographs of the existing space with your location and a brief description of the work you have in mind.'},{'q':'Do you cover my address?','a':'We are based in Colne and cover Burnley, Pendle, Barnoldswick, Skipton and the surrounding areas. Call or email with your postcode to check availability.'}])+'</div></section>'
    write_page('/contact/','Contact George Entwistle | Free Driveway & Patio Quotes','Call George Entwistle on 07581 223870 for driveway, patio, paving, landscaping and fencing quotes in Colne, Burnley and Pendle. Free site visits.',body,[('Home','/'),('Contact','/contact/')])

    body = page_head('Areas we cover','Local paving, from Colne and across the area.','Driveway, patio, fencing and landscaping projects in Colne, Burnley, Pendle, Barnoldswick and Skipton.','/areas/')
    body += f'<section class="section"><div class="wrap content-layout"><article><h2>Based in Colne</h2><p>Colne is the base for George Entwistle Driveways & Paving. Whether you need to improve parking at the front of your home or make better use of a back garden, we can arrange a site visit to talk through the space.</p><h2>Burnley and Pendle</h2><p>We work across Burnley and Pendle on driveways, block paving, patios, fencing and landscaping. Every property has different levels, access and existing ground conditions, so a visit helps us work out a suitable layout and scope of work.</p><h2>Barnoldswick and Skipton</h2><p>We also serve Barnoldswick, Skipton and surrounding areas. Share your postcode, the kind of work you are considering and a few photos when you get in touch. George can confirm availability for your address and discuss a visit.</p><h2>One project, considered as a whole</h2><p>You may be replacing a driveway, creating a seating area or planning a wider garden improvement. It helps to consider adjoining paths, steps, lawn edges and boundaries at the same time, so the different surfaces connect neatly and work for the way you use your home.</p>{areas()}<h2>Not sure whether we cover your area?</h2><p>Call {PHONE} or email <a href="mailto:{EMAIL}">{EMAIL}</a> with your location. Site visits and quotes are free and there is no obligation to go ahead.</p></article><aside class="service-aside"><h2>What would you like to improve?</h2><ul>'+''.join(f'<li><a href="/services/{slug}/">{e(info[0])}</a></li>' for slug,info in SERVICE_INFO.items())+f'</ul>{button("Check availability")}</aside></div></section>{cta()}'
    write_page('/areas/','Paving in Colne, Burnley, Pendle & Skipton | Areas Covered','George Entwistle Driveways & Paving covers Colne, Burnley, Pendle, Barnoldswick and Skipton. Contact George to check availability for your property.',body,[('Home','/'),('Areas we cover','/areas/')])

    body = '<section class="error-page"><div class="wrap"><span class="eyebrow">Page not found</span><h1>Let’s get you back<br>on the right path.</h1><p class="lead">This page may have moved. Explore our services or get in touch with George.</p><div class="actions" style="justify-content:center">'+button('Back to home','/')+button('Our services','/services/','outline')+'</div></div></section>'
    write_page('/404.html','Page not found | Entwistle Paving','Find your way to Entwistle Paving services and contact details.',body,noindex=True)
    (OUT/'robots.txt').write_text('User-agent: *\nAllow: /\n\nSitemap: '+ORIGIN+'/sitemap.xml\n')
    (OUT/'_headers').write_text('/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n  X-Frame-Options: SAMEORIGIN\n/assets/*\n  Cache-Control: public, max-age=86400, stale-while-revalidate=604800\n')
    ns='http://www.sitemaps.org/schemas/sitemap/0.9'; ins='http://www.google.com/schemas/sitemap-image/1.1'
    ET.register_namespace('',ns); ET.register_namespace('image',ins)
    sitemap=ET.Element('{'+ns+'}urlset')
    for path,_ in PAGES:
        node=ET.SubElement(sitemap,'{'+ns+'}url');ET.SubElement(node,'{'+ns+'}loc').text=ORIGIN+path
        if path=='/gallery/':
            for p in PHOTOS:
                item=ET.SubElement(node,'{'+ins+'}image');ET.SubElement(item,'{'+ins+'}loc').text=ORIGIN+'/assets/photos/'+max(p['variants'],key=lambda v:v['width'])['src']
    ET.ElementTree(sitemap).write(OUT/'sitemap.xml',encoding='utf-8',xml_declaration=True)
    redirects=['/index.html / 301!','/index / 301!']
    for path,_ in PAGES:
        if path!='/':
            legacy=path.strip('/')
            redirects.extend([f'/{legacy}.html {path} 301!',f'/{legacy} {path} 301!'])
    redirects += ['/reviews /testimonials/ 301!','/reviews/ /testimonials/ 301!','/reviews.html /testimonials/ 301!', 'https://entwistlepaving.netlify.app/* '+ORIGIN+'/:splat 301!', 'https://www.entwistlepaving.co.uk/* '+ORIGIN+'/:splat 301!']
    (OUT/'_redirects').write_text('\n'.join(redirects)+'\n')
    (OUT/'site.webmanifest').write_text(json.dumps({'name':NAME,'short_name':'Entwistle Paving','start_url':'/','display':'browser','theme_color':'#292328','background_color':'#f8f6f2','icons':[{'src':'/assets/apple-touch-icon.png','sizes':'180x180','type':'image/png'}]}))
    # Preserve old externally linked image URLs while serving only the improved variants in pages.
    shutil.copytree(ROOT/'images',OUT/'images')
    for name in ['favicon.svg','favicon-48x48.png','apple-touch-icon.png']:
        shutil.copy(ROOT/'assets'/name,OUT/name)
    print(f'Built {len(PAGES)} indexable pages, custom 404, {len(PHOTOS)} unique gallery photos, sitemap and redirects.')

if __name__ == '__main__':
    build()
