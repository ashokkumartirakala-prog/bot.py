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
        "google_review_url": "https://search.google.com/local/writereview?placeid=ChIJZ9bhmVqLXzkRFNPVjQcPi3w"
    },
    "hospitalB": {
        "name": "Hospital B",
        "type": "hospital",
        "google_review_url": "https://g.page/r/YYYYYYYY"
    },
    "salonunisex": {
        "name": "Salon Unisex & Bridal Studio",
        "type": "unisex salon and bridal studio",
        "google_review_url": "https://search.google.com/local/writereview?placeid=ChIJZ9bhmVqLXzkRFNPVjQcPi3w"
    }
}

# Generate AI-powered review
def generate_review(business_name, business_type):
    prompt = f"Write a short, natural and positive Google review for a {business_type} named {business_name}. Keep it friendly and realistic."
    
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
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
            body {{ font-family: Arial, sans-serif; text-align: center; padding: 40px; background: #f4f6f9; }}
            .box {{ background: white; border: 1px solid #ddd; padding: 20px; border-radius: 12px; display: inline-block; width: 90%; max-width: 400px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }}
            button {{ margin: 15px; padding: 12px 20px; font-size: 16px; border-radius: 8px; cursor: pointer; border: none; background: #4CAF50; color: white; }}
            button:hover {{ background: #45a049; }}
            /* Modal styles */
            .modal {{ display: none; position: fixed; z-index: 9999; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.6); display: flex; align-items: center; justify-content: center; }}
            .modal-content {{ background: white; padding: 30px; border-radius: 12px; text-align: center; width: 80%; max-width: 300px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }}
            .checkmark {{
                width: 56px; height: 56px; border-radius: 50%; display: inline-block;
                border: 4px solid #4CAF50; position: relative; animation: pop 0.3s ease;
            }}
            .checkmark:after {{
                content: ""; position: absolute; left: 14px; top: 6px;
                width: 14px; height: 28px; border: solid #4CAF50; border-width: 0 4px 4px 0;
                transform: rotate(45deg); animation: draw 0.5s ease forwards;
            }}
            @keyframes pop {{ from {{ transform: scale(0.5); opacity: 0; }} to {{ transform: scale(1); opacity: 1; }} }}
            @keyframes draw {{ from {{ height: 0; }} to {{ height: 28px; }} }}
        </style>
        <script>
            function copyAndReview() {{
                const reviewText = document.getElementById("review").innerText;
                navigator.clipboard.writeText(reviewText).then(() => {{
                    const modal = document.getElementById("myModal");
                    modal.style.display = "flex";
                    setTimeout(() => {{
                        window.open("{business['google_review_url']}", "_blank");
                        modal.style.display = "none";
                    }}, 1500);
                }}).catch(() => {{
                    alert("❌ Copy failed, please try again.");
                }});
            }}
        </script>
    </head>
    <body>
        <div class="box">
            <h2>{business['name']}</h2>
            <p id="review">{suggested_review}</p>
            <button onclick="copyAndReview()">📋 Copy & Review</button>
        </div>

        <!-- Modal -->
        <div id="myModal" class="modal">
            <div class="modal-content">
                <div class="checkmark"></div>
                <p style="margin-top:15px; font-size:16px; color:#333;">Copied! Redirecting...</p>
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(html)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
