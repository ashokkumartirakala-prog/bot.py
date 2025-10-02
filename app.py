from flask import Flask, render_template_string
import openai
import os

app = Flask(__name__)

# Set your OpenAI API key in environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")

# Business details with their Google review links
businesses = {
    "salonA": {
        "name": "Salon A",
        "type": "salon",
        "google_review_url": "https://search.google.com/local/writereview?placeid=ChIJZ9bhmVqLXzkRFNPVjQcPi3w"  # Replace with actual link
    },
    "hospitalB": {
        "name": "Hospital B",
        "type": "hospital",
        "google_review_url": "https://g.page/r/YYYYYYYY"
    }
    "salonunisex": {
        "name": "salon unisex",
        "type": "unisex salon",
        "google_review_url": "https://search.google.com/local/writereview?placeid=ChIJZ9bhmVqLXzkRFNPVjQcPi3w"

}

# Generate AI-powered review
def generate_review(business_name, business_type):
    prompt = f"Write a short, natural and positive Google review for a {business_type} named {business_name}. Keep it friendly and realistic."
    
    response = openai.chat.completions.create(
        model="gpt-4o-mini",  # lightweight + cheap
        messages=[
            {"role": "system", "content": "You generate short, natural-sounding Google review suggestions."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=50,
        temperature=0.7
    )
    
    return response.choices[0].message.content.strip()

@app.route("/r/<code>")
def review_page(code):
    if code not in businesses:
        return "Invalid business code", 404

    business = businesses[code]
    suggested_review = generate_review(business["name"], business["type"])

    html = f"""
    <html>
    <head>
        <title>{business['name']} Review</title>
        <style>
            body {{ font-family: Arial, sans-serif; text-align: center; padding: 40px; }}
            .box {{ border: 1px solid #ccc; padding: 20px; border-radius: 12px; display: inline-block; }}
            button {{ margin: 10px; padding: 10px 20px; font-size: 16px; border-radius: 8px; cursor: pointer; }}
        </style>
        <script>
            function copyReview() {{
                const reviewText = document.getElementById("review").innerText;
                navigator.clipboard.writeText(reviewText).then(() => {{
                    alert("✅ Review copied! Now click 'Write Google Review'.");
                }});
            }}
        </script>
    </head>
    <body>
        <div class="box">
            <h2>{business['name']}</h2>
            <p id="review">{suggested_review}</p>
            <button onclick="copyReview()">📋 Copy Review</button>
            <a href="{business['google_review_url']}" target="_blank">
                <button>✍️ Write Google Review</button>
            </a>
        </div>
    </body>
    </html>
    """
    return render_template_string(html)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
