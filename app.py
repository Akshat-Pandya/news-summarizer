import streamlit as st
from PIL import Image
import requests
import google.generativeai as genai
import trafilatura
from newspaper import Article
import io
import nltk

nltk.download('punkt')

st.set_page_config(page_title='InNews🇮🇳: A Summarised News📰 Portal', page_icon='./Meta/newspaper.ico')

# ✅ Configure Gemini API
genai.configure(api_key="AIzaSyBegl0hIl3E2cXT5yFr8y-UcwCZCGGDZjk")
model = genai.GenerativeModel(model_name="gemini-2.5-flash")

# ✅ NewsAPI key
NEWS_API_KEY = "e39b42bd2c4843118a5de396ee7eacce"

# 🔹 Function to get only news URLs
def get_news_urls(api_key, query="India news", page_size=10):
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "sortBy": "publishedAt",
        "pageSize": page_size,
        "language": "en",
        "apiKey": api_key
    }
    response = requests.get(url, params=params)
    data = response.json()
    if data.get("status") == "ok" and data.get("articles"):
        return data["articles"]
    else:
        return []

# 🔹 Extract full text from article
def extract_article_content(url):
    text = ""
    try:
        article = Article(url)
        article.download()
        article.parse()
        text = article.text
    except:
        pass

    if not text or len(text.split()) < 50:
        try:
            downloaded = trafilatura.fetch_url(url)
            if downloaded:
                text = trafilatura.extract(downloaded)
        except:
            pass

    return text

# 🔹 Generate AI summary
def generate_ai_summary(title, content):
    if not content or len(content.split()) < 20:
        return "Content could not be extracted for this article."
    try:
        prompt = f"""
        Summarize the following news article in 3-5 sentences, focusing on the key facts:
        Title: {title}
        Content: {content}
        """
        response = model.generate_content(prompt)
        return response.text.strip() if response and hasattr(response, "text") else "No summary available."
    except:
        return "AI summarization failed."

# 🔹 Display news articles
def display_news(articles):
    for i, news in enumerate(articles, start=1):
        title = news.get("title", "No Title")
        url = news.get("url", "#")
        description = news.get("description", "No description available")
        image_url = news.get("urlToImage", "./Meta/no_image.jpg")

        st.write(f"### ({i}) {title}")

        # Display image
        try:
            if image_url:
                img_data = requests.get(image_url, timeout=5).content
                image = Image.open(io.BytesIO(img_data))
                st.image(image, use_container_width=True)
        except:
            image = Image.open('./Meta/no_image.jpg')
            st.image(image, use_container_width=True)

        # Extract and summarize
        content = extract_article_content(url)
        ai_summary = generate_ai_summary(title, content)

        with st.expander("📝 View Details"):
            st.write("**AI-Generated Summary:**")
            st.markdown(f"<p style='text-align: justify;'>{ai_summary}</p>", unsafe_allow_html=True)

            if content:
                st.write("**🔹 Briefing (First Paragraph):**")
                briefing = " ".join(content.split(". ")[:3]) + "."
                st.markdown(f"<p style='text-align: justify;'>{briefing}</p>", unsafe_allow_html=True)

            st.markdown(f"[Read full article here...]({url})")

        st.success("Published Date: " + str(news.get("publishedAt", "Unknown")))

# ✅ Main Streamlit app
def run():
    st.title("InNews🇮🇳: A Summarised News📰")
    image = Image.open('./Meta/newspaper.png')
    st.image(image, use_container_width=False)

    st.subheader("📰 Latest Headlines")

    # ✅ Using get_news_urls function
    articles = get_news_urls(NEWS_API_KEY, query="India news", page_size=10)
    if articles:
        display_news(articles)
    else:
        st.error("No news articles found. Please try again later.")

run()
