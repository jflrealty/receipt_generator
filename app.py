from flask import Flask, render_template, request, send_file
from datetime import datetime
from fpdf import FPDF
import os
import io
from num2words import num2words

app = Flask(__name__)

def valor_por_extenso(valor):
    inteiro = int(valor)
    centavos = int(round((valor - inteiro) * 100))
    texto = f"{num2words(inteiro, lang='en')}"
    if centavos > 0:
        texto += f" and {centavos} cents"
    else:
        texto += " and 00 cents"
    return texto

@app.route('/')
def index():
    return render_template('form.html')

@app.route('/gerar', methods=['POST'])
def gerar():
    nome = request.form['nome']
    valor = float(request.form['valor'])
    unidade = request.form['unidade']
    data_inicio = request.form['data_inicio']
    data_fim = request.form['data_fim']
    data_emissao = datetime.strptime(request.form['data_emissao'], '%Y-%m-%d')

    buffer = io.BytesIO()
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    logo_path = os.path.join("static", "logo.png")
    pdf.image(logo_path, x=10, y=8, w=40)

    pdf.set_font("Arial", size=12)
    pdf.ln(40)
    pdf.multi_cell(0, 10, txt=(
        "JFL Administradora Imobiliária Nações Unidas Ltda., registered under Brazil Tax number 49.826.447/0001-03,\n"
        "located at Rebouças Avenue, 3.084, Floor 4º, Pinheiros, São Paulo - SP, representing the company\n"
        "SPE JFL AVNU EMPREEENDIMENTO IMOBILIARIO S.A., Tax number 35.946.965/0001-56, have received from\n"
        f"{nome}, the amount of BRL {valor:,.2f} ({valor_por_extenso(valor)}), regarding lease of unit {unidade} at\n"
        "building Av.NU, located at Nações Unidas Av, 15.187."
    ))

    pdf.ln(10)
    pdf.cell(0, 10, f"Resident: {nome}", ln=True)
    pdf.cell(0, 10, f"Lease Period: {datetime.strptime(data_inicio, '%Y-%m-%d').strftime('%B %d, %Y')} to {datetime.strptime(data_fim, '%Y-%m-%d').strftime('%B %d, %Y')}", ln=True)
    pdf.ln(5)
    pdf.cell(0, 10, f"São Paulo, {data_emissao.strftime('%B %d, %Y')}", ln=True)

    pdf.ln(15)
    pdf.cell(0, 10, "JFL Administradora Imobiliária Nações Unidas Ltda.", ln=True)

    pdf.output(buffer)
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name="recibo.pdf", mimetype='application/pdf')

if __name__ == '__main__':
    app.run(debug=True)
