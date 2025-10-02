from flask import Flask, render_template_string, jsonify
import openai
import os

app = Flask(__name__)

# Get OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# Business details
businesses = {
    "salonA": {
        "name": "Salon A",
        "type": "salon",
        "google_review_url": "https://search.google.com/local/writereview?placeid=ChIJZ9bhmVqLXzkRFNPVjQcPi3w"
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
        max_tokens=60,
        temperature=0.7
    )
    return response.choices[0].message.content.strip()

# Review page
@app.route("/r/<code>")
def review_page(code):
    if code not in businesses:
        return "Invalid business code", 404

    business = businesses[code]
    suggested_review = generate_review(business["name"], business["type"])

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{business['name']} Review</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                font-family: Arial, sans-serif;
                text-align: center;
                padding: 20px;
                background: #f4f6f9;
                margin: 0;
            }}
            .box {{
                background: #fff;
                border-radius: 15px;
                padding: 20px;
                display: inline-block;
                width: 95%;
                max-width: 420px;
                box-shadow: 0 6px 15px rgba(0,0,0,0.15);
                margin-top: 30px;
            }}
            h2 {{
                margin-bottom: 15px;
                color: #333;
            }}
            p#review {{
                font-size: 16px;
                padding: 15px;
                border: 1px dashed #aaa;
                border-radius: 12px;
                background: #f9f9ff;
                min-height: 60px;
            }}
            button {{
                margin-top: 12px;
                padding: 14px 0;
                font-size: 16px;
                border-radius: 10px;
                cursor: pointer;
                border: none;
                width: 100%;
                transition: 0.3s;
                font-weight: bold;
            }}
            button.copy-btn {{
                background: #4CAF50;
                color: white;
            }}
            button.copy-btn:hover {{ background: #45a049; }}
            button.new-btn {{
                background: #007BFF;
                color: white;
            }}
            button.new-btn:hover {{ background: #0069d9; }}

            /* Bottom Sheet Modal */
            .modal {{
                display: none;
                position: fixed;
                z-index: 1000;
                left: 0;
                top: 0;
                width: 100%;
                height: 100%;
                background: rgba(0,0,0,0.5);
                justify-content: center;
                align-items: flex-end;
            }}
            .modal.show {{
                display: flex;
            }}
            .modal-content {{
                background: white;
                width: 100%;
                border-radius: 20px 20px 0 0;
                padding: 25px;
                text-align: center;
                animation: slideUp 0.4s ease-out;
            }}
            @keyframes slideUp {{
                from {{ transform: translateY(100%); }}
                to {{ transform: translateY(0); }}
            }}
            .checkmark {{
                width: 70px;
                height: 70px;
                border-radius: 50%;
                display: inline-block;
                border: 5px solid #4CAF50;
                position: relative;
            }}
            .checkmark:after {{
                content: "";
                position: absolute;
                left: 20px;
                top: 10px;
                width: 20px;
                height: 40px;
                border: solid #4CAF50;
                border-width: 0 5px 5px 0;
                transform: rotate(45deg);
            }}
            .modal-content p {{
                font-size: 18px;
                color: #333;
                margin-top: 15px;
                font-weight: 600;
            }}
        </style>
        <script>
            function copyAndReview() {{
                const reviewText = document.getElementById("review").innerText;
                navigator.clipboard.writeText(reviewText).then(() => {{
                    const modal = document.getElementById("myModal");
                    modal.classList.add("show");
                    setTimeout(() => {{
                        window.open("{business['google_review_url']}", "_blank");
                        modal.classList.remove("show");
                    }}, 1800);
                }}).catch(() => {{
                    alert("❌ Copy failed, please try again.");
                }});
            }}

            async function newSuggestion() {{
                const response = await fetch("/new_review/{code}");
                const data = await response.json();
                document.getElementById("review").innerText = data.review;
            }}
        </script>
    </head>
    <body>
        <div class="box">
            <h2>{business['name']}</h2>
            <p id="review">{suggested_review}</p>
            <button class="copy-btn" onclick="copyAndReview()">📋 Copy & Review</button>
            <button class="new-btn" onclick="newSuggestion()">🔄 New Suggestion</button>
        </div>

        <!-- Modal -->
        <div id="myModal" class="modal">
            <div class="modal-content">
                <div class="checkmark"></div>
                <p>Copied! Redirecting...</p>
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(html)

# Endpoint for new review suggestion
@app.route("/new_review/<code>")
def new_review(code):
    if code not in businesses:
        return jsonify({"review": "Invalid business code"})
    business = businesses[code]
    return jsonify({"review": generate_review(business["name"], business["type"])})

# Run only in dev mode locally
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
