# app.py
from flask import Flask, render_template, request, send_file
from datetime import datetime
from fpdf import FPDF
import os
import zipfile
import tempfile
from num2words import num2words

app = Flask(__name__)

def valor_por_extenso(valor):
    inteiro = int(valor)
    centavos = int(round((valor - inteiro) * 100))
    texto = f"{num2words(inteiro, lang='en')}"
    if centavos > 0:
        texto += f" and {num2words(centavos, lang='en')} cents"
        texto += " of Brazilian reais"
    else:
        texto += " of Brazilian reais"
    return texto

@app.route('/')
def index():
    return render_template('form.html')

@app.route('/gerar', methods=['POST'])
def gerar():
    total_linhas = int(request.form['total_linhas'])
    recibos_paths = []

    with tempfile.TemporaryDirectory() as tmpdir:
        for i in range(total_linhas):
            nome = request.form.get(f'nome_{i}')
            valor_str = request.form.get(f'valor_{i}')
            valor = float(valor_str.replace('R$', '').replace('.', '').replace(',', '.').strip())
            unidade = request.form.get(f'unidade_{i}')
            data_inicio = request.form.get(f'data_inicio_{i}')
            data_fim = request.form.get(f'data_fim_{i}')
            data_emissao = request.form.get(f'data_emissao_{i}')
            responsavel = request.form.get(f'responsavel_{i}', ' ')  # assinatura opcional

            data_emissao_dt = datetime.strptime(data_emissao, '%Y-%m-%d')

            pdf = FPDF()
            pdf.add_page()

            pdf.set_auto_page_break(auto=True, margin=15)

            logo_path = os.path.join("static", "logo.png")
            if os.path.exists(logo_path):
                pdf.image(logo_path, x=70, y=8, w=70)

            # Número do recibo no canto superior direito
            numero = f"REC-{datetime.now().strftime('%Y%m%d')}-{str(i+1).zfill(4)}"
            pdf.set_xy(150, 10)
            pdf.set_font("Arial", "", 10)
            pdf.cell(0, 10, f"No.: {numero}", ln=False, align='R')

            pdf.set_font("Arial", size=11)
            pdf.ln(60)

            pdf.multi_cell(0, 8, txt=(
                "JFL Administradora Imobiliária Nações Unidas Ltda., registered under Brazil Tax number 49.826.447/0001-03,\n"
                "located at Rebouças Avenue, 3.084, 4th Floor , Pinheiros, São Paulo - SP, representing company\n"
                "SPE JFL AVNU Empreendimento Imobiliario S.A., Tax number 35.946.965/0001-56, has received\n"
                f"from\n"
                f"{nome}, the amount of BRL {valor:,.2f} ({valor_por_extenso(valor)}),\n"
                f"regarding lease unit {unidade} at\n"
                "building Av.NU, located at Nações Unidas Av, 15.187."
            ), align='J')

            pdf.ln(10)
            pdf.set_font("Arial", "B", 11)
            pdf.multi_cell(0, 8, f"Resident: {nome}", align='L')
            pdf.multi_cell(0, 8, f"Lease Period: {datetime.strptime(data_inicio, '%Y-%m-%d').strftime('%B %d, %Y')} to {datetime.strptime(data_fim, '%Y-%m-%d').strftime('%B %d, %Y')}", align='L')
            pdf.ln(5)
            pdf.set_font("Arial", size=11)
            pdf.cell(0, 10, f"São Paulo, {data_emissao_dt.strftime('%B %d, %Y')}", ln=True, align='L')

            pdf.ln(15)
            pdf.set_font("Arial", size=11)
            pdf.cell(0, 10, "________________________", ln=True, align='C')
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, responsavel.upper(), ln=True, align='C')
            pdf.set_font("Arial", size=11)
            pdf.cell(0, 10, "JFL Administradora Imobiliária Nações Unidas Ltda.", ln=True, align='C')

            safe_nome = nome.strip().replace(" ", "_").replace("/", "_").replace("\\", "_")
            path_pdf = os.path.join(tmpdir, f"jfl_invoice_{safe_nome}.pdf")
            pdf.output(path_pdf)
            recibos_paths.append(path_pdf)

        zip_path = os.path.join(tmpdir, "recibos.zip")
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for path in recibos_paths:
                zipf.write(path, os.path.basename(path))

        return send_file(zip_path, as_attachment=True, download_name="recibos.zip")
