from flask import Flask, render_template, send_file
import pandas as pd
import io
from scraper import run_scraping

app = Flask(__name__)
cached_data = []  # メモリキャッシュ

@app.route("/")
def index():
    return render_template("index.html", companies=cached_data)

@app.route("/scrape")
def scrape():
    global cached_data
    cached_data = run_scraping()
    return render_template("index.html", companies=cached_data, message=f"{len(cached_data)}件取得しました")

@app.route("/export")
def export():
    df = pd.DataFrame(cached_data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="SES企業リスト")
    output.seek(0)
    return send_file(output, download_name="ses_companies.xlsx",
                     as_attachment=True, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

if __name__ == "__main__":
    app.run(debug=True)