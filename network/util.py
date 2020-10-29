from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def paginate(posts, page):
    paginator = Paginator(posts, 10)
    
    try:
        return paginator.page(page)
    except PageNotAnInteger:
        return paginator.page(1)
    except EmptyPage:
        return paginator.page(paginator.num_pages)