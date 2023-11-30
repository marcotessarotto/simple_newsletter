from bs4 import BeautifulSoup


def ensure_correct_base_url(base_url):
    """Ensure the base URL does not end with a slash."""
    if base_url.endswith('/'):
        return base_url[:-1]
    return base_url


def make_urls_absolute(html_content, base_url):
    """
    Make all urls in the html_content absolute by prepending the base_url.
    :param html_content:
    :param base_url:
    :return:
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    base_url = ensure_correct_base_url(base_url)

    for img_tag in soup.find_all('img'):
        if img_tag['src'].startswith('/'):
            img_tag['src'] = base_url + img_tag['src']

    return str(soup)

# # Example usage
# base_url = 'https://www.example.com' # Replace with your actual base URL
# html_content = """
# <p>this is a test</p>
# <p>&nbsp;</p>
# <p><img alt="" src="/media/content/ckeditor/2023/11/30/logo_esteso_bsbf2024.jpg" style="height:199px; width:280px" /></p>
# <p>&nbsp;</p>
# """
#
# updated_html = make_urls_absolute(html_content, base_url)
# print(updated_html)
