from flask import Flask, render_template, request, Response
from datetime import datetime
from fpdf import FPDF
import os
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
    recibos = []
    total_linhas = int(request.form['total_linhas'])
    print(f"🔢 Gerando {total_linhas} recibo(s)")

    for i in range(total_linhas):
        nome = request.form.get(f'nome_{i}')
        valor_str = request.form.get(f'valor_{i}')
        valor = float(valor_str.replace('R$', '').replace('.', '').replace(',', '.').strip())
        unidade = request.form.get(f'unidade_{i}')
        data_inicio = request.form.get(f'data_inicio_{i}')
        data_fim = request.form.get(f'data_fim_{i}')
        data_emissao = request.form.get(f'data_emissao_{i}')

        print(f"🧾 Recibo {i+1}: {nome} - R$ {valor:.2f} - Unidade: {unidade}")

        data_emissao_dt = datetime.strptime(data_emissao, '%Y-%m-%d')

        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)

        logo_path = os.path.join("static", "logo.png")
        if os.path.exists(logo_path):
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
        pdf.cell(0, 10, f"São Paulo, {data_emissao_dt.strftime('%B %d, %Y')}", ln=True)

        pdf.ln(15)
        pdf.cell(0, 10, "JFL Administradora Imobiliária Nações Unidas Ltda.", ln=True)

        pdf_bytes = pdf.output(dest='S').encode('latin1')
        recibos.append(pdf_bytes)

    print("✅ Recibo(s) gerado(s) com sucesso!")
    return Response(
        recibos[0],
        mimetype='application/pdf',
        headers={"Content-Disposition": "attachment;filename=recibo.pdf"}
    )
