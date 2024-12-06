import random
import time
import os
import anthropic


class TopicPost:
    def __init__(self, api_key):
        self.api_key = api_key
        self.query_dict = {
            "AI Basics": [
                "artificial intelligence", "neural network", "AI tools", "machine learning", "deep learning",
                "natural language processing", "computer vision", "reinforcement learning"
            ],
            "AI Applications": [
                "AI in healthcare", "AI in finance", "AI in education", "AI in marketing", "AI in cybersecurity",
                "AI in robotics", "AI in space exploration", "AI in smart cities", "AI in IoT"
            ],
            "Advanced Techniques": [
                "neural networks architectures", "transformers in AI", "GANs", "deep reinforcement learning", 
                "convolutional neural networks", "attention mechanisms", "AI in quantum computing"
            ],
            "Ethical and Social Issues": [
                "AI ethics", "bias in AI", "AI fairness", "AI privacy", "AI accountability", "AI governance"
            ],
            "AI and the Future": [
                "AI trends", "AI and future jobs", "AI for digital transformation", "AI and creativity in media",
                "AI for social impact", "AI in climate change", "AI in space missions"
            ],
            "Tech Integration": [
                "AI and blockchain", "AI and big data", "AI and 5G", "AI in autonomous vehicles", "AI in drones"
            ]
        }
        self.client = anthropic.Client(api_key=self.api_key)
        self.current_date = time.strftime("%Y-%m-%d")
        self.date_time = time.strftime("%Y-%m-%d-%H-%M-%S")

    def select_random_query(self):
        category = random.choice(list(self.query_dict.keys()))
        return category, random.sample(self.query_dict[category], 3)

    def generate_title_prompt(self, selected_query):
        return (
            f"Generate one catchy and SEO-optimized article title based on the following keywords: {selected_query}. "
            f"Ensure the titles are engaging, concise, and relevant for ranking on Google search. The titles should reflect "
            f"common search queries, incorporate trending topics in AI, and be structured to attract user clicks. "
            f"Give me only the title."
        )

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

    def create_article_prompt(self, title):
        return f'''
        Create an SEO optimized article on this topic, explain it in a short way that anyone can 
        understand: {title}

        Please create a comprehensive, SEO-optimized article based on the research. Summarize the 
        key findings, provide code examples where relevant, and explain the concepts in detail. 
        Make sure to structure the article with proper headings, keywords, and make it suitable 
        for a technical audience. The goal is for the article to rank high on search engines and 
        be informative for both experts and beginners in AI. The current date is: {self.current_date}.

        JUST GIVE ME THE ARTICLE, DON'T WRITE ANYTHING ELSE

        Make sure the links in the article work
        '''

    def read_format_file(self, file_path="format.md"):
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()

    def call_anthropic(self, system_message, prompt, max_tokens=3000, temperature=0.7):
        response = self.client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_message,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text

    def save_article(self, content):
        directory = "post/posts/"
        file_path = f"{directory}{self.date_time}.md"
        
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content)

    def run(self):
        category, selected_query = self.select_random_query()

        title_prompt = self.generate_title_prompt(selected_query)
        title = self.call_anthropic("You are an AI that specializes in SEO optimization for article titles.", title_prompt, max_tokens=32)

        format_content = self.read_format_file()

        system_message = self.generate_system_message(format_content)
        article_prompt = self.create_article_prompt(title)
        article = self.call_anthropic(system_message, article_prompt)

        self.save_article(article)