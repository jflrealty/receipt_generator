from flask import Flask, render_template, request, send_file
from datetime import datetime
from fpdf import FPDF
import os
import io
import zipfile
from num2words import num2words

app = Flask(__name__)

def valor_por_extenso(valor):
    inteiro = int(valor)
    centavos = int(round((valor - inteiro) * 100))
    texto = f"{num2words(inteiro, lang='en').replace(',', '')}"
    if centavos > 0:
        texto += f" and {num2words(centavos, lang='en')} cents"
    texto += " of Brazilian reais"
    return texto

@app.route('/')
def index():
    return render_template('form.html')

@app.route('/gerar', methods=['POST'])
def gerar():
    total_linhas = int(request.form['total_linhas'])
    pdf_buffers = []

    for i in range(total_linhas):
        nome = request.form.get(f'nome_{i}')
        if not nome:
            continue
        valor_str = request.form.get(f'valor_{i}', '').replace('R$', '').replace('.', '').replace(',', '.').strip()
        valor = float(valor_str) if valor_str else 0.0
        unidade = request.form.get(f'unidade_{i}')
        data_inicio = request.form.get(f'data_inicio_{i}')
        data_fim = request.form.get(f'data_fim_{i}')
        data_emissao = datetime.strptime(request.form.get(f'data_emissao_{i}'), '%Y-%m-%d')
        responsavel = request.form.get(f'responsavel_{i}')

        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)

        logo_path = os.path.join("static", "logo.png")
        if os.path.exists(logo_path):
            pdf.image(logo_path, x=85, y=10, w=40)

        pdf.ln(45)  # mais espaço da logo

        numero = f"REC-{datetime.now().strftime('%Y%m%d')}-{str(i+1).zfill(4)}"
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 10, f"Receipt No.: {numero}", ln=True, align='R')

        pdf.set_font("Arial", size=10)
        pdf.ln(2)

        pdf.multi_cell(0, 6, txt=(
            f"JFL Administradora Imobiliária Nações Unidas Ltda., registered under Brazil Tax number "
            f"49.826.447/0001-03, located at Rebouças Avenue, 3.084, 4th Floor , Pinheiros, São Paulo - SP, "
            f"representing company SPE JFL AVNU Empreendimento Imobiliario S.A., Tax number 35.946.965/0001-56, "
            f"has received from {nome}, the amount of BRL {valor:,.2f} ({valor_por_extenso(valor)}), "
            f"regarding lease unit {unidade} at building Av.NU, located at Nações Unidas Av, 15.187."
        ), align='J')

        pdf.ln(8)
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(0, 10, f"Resident: {nome}", ln=True, align='L')
        pdf.cell(0, 10, f"Lease Period: {datetime.strptime(data_inicio, '%Y-%m-%d').strftime('%B %d, %Y')} to {datetime.strptime(data_fim, '%Y-%m-%d').strftime('%B %d, %Y')}", ln=True, align='L')
        pdf.ln(5)
        pdf.set_font("Arial", size=10)
        pdf.cell(0, 10, f"São Paulo, {data_emissao.strftime('%B %d, %Y')}", ln=True, align='L')

        pdf.ln(25)
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, responsavel, ln=True, align='C')  # assinatura agora em cima da linha
        pdf.cell(0, 10, "__________________________", ln=True, align='C')
        pdf.set_font("Arial", size=10)
        pdf.cell(0, 10, "JFL Administradora Imobiliária Nações Unidas Ltda.", ln=True, align='C')

        pdf_bytes = pdf.output(dest='S').encode('latin1')
        safe_nome = nome.strip().replace(" ", "_").replace("/", "_").replace("\\", "_")
        pdf_buffers.append((f"jfl_invoice_{safe_nome}.pdf", pdf_bytes))

    if not pdf_buffers:
        return "Nenhum recibo válido para gerar. Volte e preencha pelo menos um."

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zipf:
        for filename, content in pdf_buffers:
            zipf.writestr(filename, content)
    zip_buffer.seek(0)

    return send_file(zip_buffer, mimetype='application/zip', as_attachment=True, download_name='recibos_jfl.zip')
