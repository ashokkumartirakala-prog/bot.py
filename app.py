import os
from flask import Flask, render_template_string
from openai import OpenAI

app = Flask(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Business categories mapping
business_categories = {
    "salonA": "salon and beauty services",
    "hospitalB": "hospital and healthcare",
    "cafeC": "coffee shop and cafe",
}

@app.route("/")
def home():
    return "Welcome! Use /r/<code> to see a business review page."

@app.route("/r/<code>")
def review_page(code):
    if code not in business_categories:
        return "This business is not registered yet."

    # Generate AI review suggestion
    prompt = f"Write a short, positive Google review (1-2 sentences) for a {business_categories[code]}."
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # lightweight + cost effective
        messages=[{"role": "user", "content": prompt}],
        max_tokens=60,
    )

    review = response.choices[0].message.content.strip()

    html = f"""
    <html>
      <head>
        <title>Review for {code}</title>
      </head>
      <body style="font-family: Arial; text-align: center; margin-top: 50px;">
        <h2>Leave a Review</h2>
        <p>Suggested review:</p>
        <textarea rows="4" cols="50">{review}</textarea>
        <br><br>
        <a href="https://www.google.com/maps/search/?api=1&query={code}" target="_blank">
          👉 Click here to post on Google Reviews
        </a>
      </body>
    </html>
    """
    return render_template_string(html)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
