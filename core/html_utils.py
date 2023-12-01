from bs4 import BeautifulSoup


def ensure_correct_base_url(base_url):
    """Ensure the base URL does not end with a slash."""
    if base_url.endswith('/'):
        return base_url[:-1]
    return base_url


def make_urls_absolute(html_content, base_url, set_a_target=None):
    """
    Make all URLs in the html_content absolute by prepending the base_url and optionally set target attribute for <a> tags.
    :param html_content: HTML content as a string.
    :param base_url: The base URL to prepend.
    :param set_a_target: Optional target attribute value for <a> tags. example: "_blank"
    :return: Updated HTML content with absolute URLs and optional target attributes.
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    base_url = ensure_correct_base_url(base_url)

    # Update src for img tags
    for img_tag in soup.find_all('img'):
        if img_tag.get('src', '').startswith('/'):
            img_tag['src'] = base_url + img_tag['src']

    # Update href for a tags and optionally set target
    for a_tag in soup.find_all('a'):
        if a_tag.get('href', '').startswith('/'):
            a_tag['href'] = base_url + a_tag['href']
        if set_a_target:
            a_tag['target'] = set_a_target

    return str(soup)

# # Example usage
# html_content = """
# <p>this is a test</p>
# <p><a href="/home">Home</a></p>
# <p><img alt="" src="/media/image.jpg" /></p>
# """
# base_url = "https://www.example.com"
# updated_html = make_urls_absolute(html_content, base_url, set_a_target="_blank")
# print(updated_html)
