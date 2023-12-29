import discord_webhook as dw
from pyquery import PyQuery
from markdownify import MarkdownConverter
import requests
import re

WEBHOOK_URL = "https://discord.com/api/webhooks/1190373198345285723/sHuP-N3KPBmaD1MG_bHUIoJoEEogmTb6rhMFc6Eomy8dxSA4EKiEh27ccS6QNrW6AfID"
ATLAS_OBSCURA_RANDOM_URL = "https://www.atlasobscura.com/random"
LINK_EXTRACTOR = re.compile(r'<a href="([^"]+)">')


webhook = dw.DiscordWebhook(WEBHOOK_URL);

def get_obscura_url():
	response = requests.get(ATLAS_OBSCURA_RANDOM_URL, allow_redirects=False)
	url = LINK_EXTRACTOR.search(response.text.replace('\n',"")).group(1)
	return url


def chomp(text):
    """
    If the text in an inline tag like b, a, or em contains a leading or trailing
    space, strip the string and return a space as suffix of prefix, if needed.
    This function is used to prevent conversions like
        <b> foo</b> => ** foo**
    """
    prefix = ' ' if text and text[0] == ' ' else ''
    suffix = ' ' if text and text[-1] == ' ' else ''
    text = text.strip()
    return (prefix, suffix, text)


class ContentProcessor(MarkdownConverter):
	def should_convert_tag(self, tag):
		return super().should_convert_tag(tag)
	def __init__(self):
		super().__init__(convert = ("a", "span"))
	
	def convert_span(self, el, text, convert_as_inline):
		try:
			if "section-start-text" in el.get("class"):
				return f"**{text}**"
			else:
				return text
		except:
			return text
	
	def convert_a(self, el, text, convert_as_inline):
		prefix, suffix, text = chomp(text)
		if not text:
			return ''
		href = el.get('href')
		title = el.get('title')
		# For the replacement see #29: text nodes underscores are escaped
		if (self.options['autolinks']
				and text.replace(r'\_', '_') == href
				and not title
				and not self.options['default_title']):
			# Shortcut syntax
			return '<%s>' % href
		if self.options['default_title'] and not title:
			title = href
		title_part = ' "%s"' % title.replace('"', r'\"') if title else ''
		return '%s[%s](<%s%s>)%s' % (prefix, text, href, title_part, suffix) if href else text

def get_paragraph(content, processor=ContentProcessor()):
	return (processor.convert(PyQuery(i).html()) for i in content)

def extract_paragraph(url: str):
	response = requests.get(url)
	d = PyQuery(response.text)
	
	content_paragraph = d("#place-body p")
	
	return get_paragraph(content_paragraph)

def post_message(url, content):
	webhook.set_content(f"# IT'S ATLAS OBSCURA TIME!!!\n[View it here]({url})")
	webhook.execute()
	for paragraph in content:
		webhook.set_content(paragraph)
		webhook.execute()

def main():
	url = get_obscura_url()
	paragraph = extract_paragraph(url)
	post_message(url, paragraph)

if __name__ == "__main__":
	main()