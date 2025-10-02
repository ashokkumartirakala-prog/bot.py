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
        "name": "Salon Unisex",
        "type": "unisex salon",
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
            body {{
                font-family: 'Segoe UI', Arial, sans-serif;
                background: #f9fafc;
                text-align: center;
                padding: 40px;
            }}
            .box {{
                background: #fff;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                padding: 30px;
                border-radius: 16px;
                display: inline-block;
                max-width: 400px;
                width: 90%;
            }}
            h2 {{ color: #333; }}
            p#review {{
                font-size: 16px;
                padding: 15px;
                border: 1px dashed #aaa;
                border-radius: 10px;
                background: #f1f1f9;
            }}
            button {{
                margin-top: 20px;
                padding: 14px 24px;
                font-size: 16px;
                border: none;
                border-radius: 12px;
                cursor: pointer;
                background: #4CAF50;
                color: white;
                transition: 0.3s;
                width: 100%;
            }}
            button:hover {{
                background: #43a047;
            }}
            /* Responsive full-width modal */
            .modal {{
                display: none;
                position: fixed;
                z-index: 9999;
                left: 0;
                top: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0,0,0,0.6);
                display: flex;
                align-items: center;
                justify-content: center;
            }}
            .modal-content {{
                background-color: #fff;
                padding: 20px;
                border-radius: 16px;
                width: 90%;
                max-width: 400px;
                text-align: center;
                animation: fadeIn 0.4s;
            }}
            @keyframes fadeIn {{
                from {{opacity: 0; transform: translateY(-20px);}}
                to {{opacity: 1; transform: translateY(0);}}
            }}
        </style>
        <script>
            function copyAndReview() {{
                const reviewText = document.getElementById("review").innerText;
                navigator.clipboard.writeText(reviewText).then(() => {{
                    document.getElementById("myModal").style.display = "flex";
                    setTimeout(() => {{
                        window.open("{business['google_review_url']}", "_blank");
                        document.getElementById("myModal").style.display = "none";
                    }}, 1500);
                }});
            }}
        </script>
    </head>
    <body>
        <div class="box">
            <h2>{business['name']}</h2>
            <p id="review">{suggested_review}</p>
            <button onclick="copyAndReview()">📋 Copy & Leave Review</button>
        </div>

        <!-- Modal -->
        <div id="myModal" class="modal">
            <div class="modal-content">
                <p>✅ Review copied! Redirecting you to Google Reviews...</p>
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(html)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
