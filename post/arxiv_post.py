import arxiv
import requests
import pdfplumber
from io import BytesIO
import time
import os
import anthropic


class ArxivPost:
    def __init__(self, api_key, query="cat:cs.AI", max_results=1):
        self.api_key = api_key
        self.query = query
        self.max_results = max_results
        self.client = arxiv.Client()
        self.current_date = time.strftime("%Y-%m-%d")
        self.date_time = time.strftime("%Y-%m-%d-%H-%M-%S")
        self.anthropic_client = anthropic.Anthropic(api_key=self.api_key)

    def fetch_latest_arxiv_paper(self):
        search = arxiv.Search(
            query=self.query,
            max_results=self.max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending,
        )
        return next(self.client.results(search), None)

    def extract_pdf_text(self, pdf_url):
        response = requests.get(pdf_url)
        with pdfplumber.open(BytesIO(response.content)) as pdf:
            return "".join(page.extract_text() for page in pdf.pages)

    def read_format_file(self, file_path="format.md"):
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()

    def generate_system_message(self, format_content):
        return f'''
        You are an expert in SEO and artificial intelligence (AI). Your task is to generate 
        optimized articles that explain complex AI research in a clear and concise manner. 
        You should structure your content in an SEO-friendly way, using relevant keywords, 
        headings, and internal linking strategies. The article should include practical 
        code examples where applicable, with detailed explanations of each part. Your writing 
        should be professional, informative, and accessible for both technical and non-technical 
        readers. The goal is to create high-quality content that ranks well on search engines.

        You should use this format for the article:
        {format_content}

        Make sure to use markdown formatting for HTML (so that the article can load into HTML 
        in the best way).
        '''

    def generate_user_message(self, full_text):
        return f'''
        Make the white paper SEO optimized from this arXiv AI research paper, but explaining it 
        in a short way that anyone can understand:

        {full_text}

        Please create a comprehensive, SEO-optimized article based on the research. Summarize the 
        key findings, provide code examples where relevant, and explain the concepts in detail. 
        Make sure to structure the article with proper headings, keywords, and make it suitable 
        for a technical audience. The goal is for the article to rank high on search engines and 
        be informative for both experts and beginners in AI. The current date is: {self.current_date}.

        Make sure the links in the article work
        '''

    def create_optimized_article(self, full_text, format_content):
        system_message = self.generate_system_message(format_content)
        user_message = self.generate_user_message(full_text)
        response = self.anthropic_client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=3000,
            system=system_message,
            messages=[{"role": "user", "content": user_message}],
        )
        return response.content[0].text

    def save_article(self, content):
        directory = "post/posts/"
        file_path = f"{directory}{self.date_time}.md"
        
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content)

    def run(self):
        paper = self.fetch_latest_arxiv_paper()
        if not paper:
            print("No papers found.")
            return

        full_text = self.extract_pdf_text(paper.pdf_url)
        format_content = self.read_format_file()
        article_content = self.create_optimized_article(full_text, format_content)
        self.save_article(article_content)