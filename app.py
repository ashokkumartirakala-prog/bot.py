from flask import Flask, request, render_template_string
import os
import openai

app = Flask(__name__)

# Set OpenAI API key as environment variable on Render
openai.api_key = os.getenv("OPENAI_API_KEY")

# Example business mapping
business_links = {
    "salonA": "https://g.page/salonA/review",
    "hospitalB": "https://g.page/hospitalB/review",
    # Add more businesses here
}

# Route for QR links
@app.route("/r/<business_id>")
def review_page(business_id):
    review_link = business_links.get(business_id)
    if not review_link:
        return "Invalid Business QR", 404

    # Generate dynamic review suggestion from OpenAI
    prompt = f"Generate a short 2-3 sentence 5-star Google review for {business_id}. Keep it natural and professional."
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=80
        )
        suggested_review = response.choices[0].message.content.strip()
    except Exception as e:
        suggested_review = "⭐⭐⭐⭐⭐ Great service! Highly recommended."

    # Render simple webpage with notification-style banner
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <title>Suggested Review</title>
      <style>
        #reviewNotification {{
          display: block;
          position: fixed;
          top: 20px;
          left: 50%;
          transform: translateX(-50%);
          background: #f1f1f1;
          padding: 15px 20px;
          border-radius: 10px;
          box-shadow: 0 4px 6px rgba(0,0,0,0.2);
          width: 90%;
          max-width: 400px;
          text-align: center;
          font-family: sans-serif;
          z-index: 1000;
        }}
        button {{
          margin: 5px;
          padding: 8px 15px;
          border: none;
          border-radius: 5px;
          background: #007bff;
          color: white;
          cursor: pointer;
        }}
        button:hover {{ background: #0056b3; }}
      </style>
    </head>
    <body>
      <div id="reviewNotification">
        <p id="reviewText"><strong>{suggested_review}</strong></p>
        <button onclick="copyReview()">Copy Review</button>
        <button onclick="leaveReview()">Leave Review</button>
      </div>

      <script>
        function copyReview() {{
          let text = document.getElementById("reviewText").innerText;
          navigator.clipboard.writeText(text).then(() => {{
            alert("Review copied! Please paste it in Google Reviews.");
          }});
        }}

        function leaveReview() {{
          window.open("{review_link}", "_blank");
        }}
      </script>
    </body>
    </html>
    """
    return html

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
