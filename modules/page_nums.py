

def page_num_control(pagination,page_lenth):
    """
    Args:
        pagination (_type_): 传递一个分页对象 pagination
        page_lenth (_type_): 固定页数的长度 比如固定显示 5 页

    Returns:
        _type_: 返回值为一个列表 列表中的元素为页码例如[1,2,3,4,5]
    """
    #========实现显示固定分页数====================

    # 1 需要显示的固定页数长度
    page_control = page_lenth
    
    # 2 计算当前页到尾页的长度
    page_len = pagination.pages - pagination.page
    
    # 3 比较当前页到尾页的长度与设定的长度
    if pagination.pages < page_control:
        # 3.1 总页数小于固定页数长度
        middle_page = range(1,pagination.pages+1)
    elif page_len < page_control <= pagination.pages:
        # 3.2 当前页到尾页全部显示
        middle_page = range(pagination.pages-page_control+1,pagination.pages+1)
    else:
        # 3.3 当前页到设置的长度
        middle_page = range(pagination.page,pagination.page+page_control)
    
    return middle_page