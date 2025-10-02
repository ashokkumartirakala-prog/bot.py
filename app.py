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
        max_tokens=50,
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
    <html>
    <head>
        <title>{business['name']} Review</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ font-family: Arial; text-align: center; padding: 40px; background: #f4f6f9; }}
            .box {{ background: white; border-radius: 12px; padding: 20px; display: inline-block; width: 90%; max-width: 400px; box-shadow:0 4px 10px rgba(0,0,0,0.1); }}
            p#review {{ font-size:16px; padding:15px; border:1px dashed #aaa; border-radius:10px; background:#f1f1f9; min-height:60px; }}
            button {{ margin-top:10px; padding:14px 0; font-size:16px; border-radius:8px; cursor:pointer; border:none; background:#4CAF50; color:white; width:100%; transition:0.3s; }}
            button:hover {{ background:#45a049; }}
            .modal {{ display:none; position:fixed; z-index:9999; left:0; bottom:0; width:100%; height:auto; background-color: rgba(0,0,0,0.4); justify-content:center; align-items:flex-end; padding:0; }}
            .modal-content {{ background:white; padding:30px 20px; border-radius:20px 20px 0 0; text-align:center; width:100%; max-width:500px; box-shadow:0 -4px 15px rgba(0,0,0,0.3); transform: translateY(100%); transition: transform 0.4s ease-out; }}
            .modal.show .modal-content {{ transform: translateY(0); }}
            .checkmark {{ width:80px; height:80px; border-radius:50%; display:inline-block; border:5px solid #4CAF50; position:relative; margin:0 auto; }}
            .checkmark:after {{ content:""; position:absolute; left:24px; top:12px; width:24px; height:48px; border: solid #4CAF50; border-width: 0 5px 5px 0; transform: rotate(45deg); }}
            .modal-content p {{ font-size:20px; color:#333; margin-top:20px; font-weight:600; }}
        </style>
        <script>
            function copyAndReview(){{
                const reviewText = document.getElementById("review").innerText;
                navigator.clipboard.writeText(reviewText).then(()=>{
                    const modal = document.getElementById("myModal");
                    modal.classList.add("show");
                    setTimeout(()=>{{ window.open("{business['google_review_url']}", "_blank"); modal.classList.remove("show"); }}, 1500);
                }}).catch(()=>{{ alert("❌ Copy failed, please try again."); }});
            }}

            async function newSuggestion(){{
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

# Only run Flask dev server locally
if __name__ == "__main__":
    app.run(debug=True)
