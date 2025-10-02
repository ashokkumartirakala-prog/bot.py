from flask import Flask, render_template_string, jsonify
import openai
import os

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

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
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                font-family: Arial, sans-serif;
                text-align: center;
                padding: 40px;
                background: #f4f6f9;
            }}
            .box {{
                background: white;
                border: 1px solid #ddd;
                padding: 20px;
                border-radius: 12px;
                display: inline-block;
                width: 90%;
                max-width: 400px;
                box-shadow: 0 4px 10px rgba(0,0,0,0.1);
            }}
            p#review {{
                font-size: 16px;
                padding: 15px;
                border: 1px dashed #aaa;
                border-radius: 10px;
                background: #f1f1f9;
                min-height: 60px;
            }}
            button {{
                margin-top: 10px;
                padding: 14px 0;
                font-size: 16px;
                border-radius: 8px;
                cursor: pointer;
                border: none;
                background: #4CAF50;
                color: white;
                width: 100%;
                transition: 0.3s;
            }}
            button:hover {{
                background: #45a049;
            }}

            /* Modal styles */
            .modal {{
                display: none;
                position: fixed;
                z-index: 9999;
                left: 0;
                top: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0,0,0,0.6);
                align-items: center;
                justify-content: center;
                padding: 15px;
            }}
            .modal-content {{
                background: white;
                padding: 40px 30px;
                border-radius: 20px;
                text-align: center;
                width: 90%;
                max-width: 400px;
                box-shadow: 0 8px 25px rgba(0,0,0,0.3);
                animation: fadeIn 0.3s ease;
            }}
            .checkmark {{
                width: 80px;
                height: 80px;
                border-radius: 50%;
                display: inline-block;
                border: 5px solid #4CAF50;
                position: relative;
                animation: pop 0.3s ease;
            }}
            .checkmark:after {{
                content: "";
                position: absolute;
                left: 24px;
                top: 12px;
                width: 24px;
                height: 48px;
                border: solid #4CAF50;
                border-width: 0 5px 5px 0;
                transform: rotate(45deg);
                animation: draw 0.5s ease forwards;
            }}
            @keyframes pop {{
                from {{ transform: scale(0.5); opacity: 0; }}
                to {{ transform: scale(1); opacity: 1; }}
            }}
            @keyframes draw {{
                from {{ height: 0; }}
                to {{ height: 48px; }}
            }}
            @keyframes fadeIn {{
                from {{ opacity: 0; }}
                to {{ opacity: 1; }}
            }}
            .modal-content p {{
                font-size: 22px;
                color: #333;
                margin-top: 25px;
                font-weight: 600;
            }}

            /* Mobile-specific adjustments */
            @media (max-width: 480px) {{
                .modal-content {{
                    width: 95%;
                    padding: 50px 25px;
                }}
                .checkmark {{
                    width: 100px;
                    height: 100px;
                }}
                .checkmark:after {{
                    left: 30px;
                    top: 15px;
                    width: 30px;
                    height: 60px;
                }}
                .modal-content p {{
                    font-size: 24px;
                    margin-top: 30px;
                }}
            }}
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
            <button onclick="copyAndReview()">📋 Copy & Review</button>
            <button onclick="newSuggestion()">🔄 New Suggestion</button>
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

@app.route("/new_review/<code>")
def new_review(code):
    if code not in businesses:
        return jsonify({"review": "Invalid business code"})
    business = businesses[code]
    suggested_review = generate_review(business["name"], business["type"])
    return jsonify({"review": suggested_review})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
