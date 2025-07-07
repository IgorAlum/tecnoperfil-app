import streamlit as st
import pandas as pd
from io import BytesIO
from fpdf import FPDF

st.set_page_config(page_title="Proposta Automática - Extrusão", layout="centered")
st.title("Tecnoperfil - Proposta Automática")

st.header("Informações da Peça")
area = st.number_input("Área da Peça (cm²)", min_value=0.0, step=0.1)
perimetro = st.number_input("Perímetro (mm)", min_value=0.0, step=0.1)
tipo = st.selectbox("Tipo da Peça", ["", "Sólido", "Tubular"])
dcc = st.number_input("DCC (mm)", min_value=0.0, step=0.1)
maior_linear = st.number_input("Maior Medida Linear (mm)", min_value=0.0, step=0.1)

st.header("Informações Comerciais")
comprimento = st.number_input("Comprimento da Peça (mm)", min_value=0.0, step=1.0)
liga = st.selectbox("Tipo de Liga", ["", "6063", "6005", "6351"])
acabamento = st.selectbox("Acabamento", ["", "Bruto", "Pintado"])
exclusiva = st.selectbox("Exclusividade", ["", "Sim", "Não"])
volume_mensal = st.number_input("Volume Mensal Estimado (kg)", min_value=0.0, step=1.0)

if st.button("Gerar Proposta"):
    if not all([area, dcc, maior_linear, comprimento, tipo, liga, acabamento, exclusiva]):
        st.warning("Por favor, preencha todos os campos obrigatórios.")
    else:
        pe = area * 2.71
        pl = maior_linear * (0.004 if tipo == "Sólido" else 0.006)

        velocidade_stem = 14
        if liga == "6005":
            velocidade_stem = 10 if pe > 1.5 else 12
        elif liga == "6351":
            velocidade_stem = 8 if pe > 1.5 else 10

        tipo_serra = "Volante" if maior_linear <= 3000 else "Fixa"
        perda = 1.3 if tipo_serra == "Volante" else 2.0

        qtd_max_furos = int(1.3 // pe) if pe > 0 else 0

        largura_necessaria = dcc + 100
        pacotes = ["228x130", "250x170", "300x170", "300x209", "400x170"]
        larguras = [228, 250, 300, 300, 400]
        pacote = "Fora do padrão"
        for p, l in zip(pacotes, larguras):
            if tipo == "Tubular" and p == "228x130":
                continue
            if largura_necessaria <= l:
                pacote = p
                break

        peso_linear = pe
        comprimento_real = comprimento / 1000 + perda
        puxada_maxima = 50  # metros
        cortes_por_tarugo = int(puxada_maxima // comprimento_real)

        peso_tarugo = peso_linear * comprimento_real * cortes_por_tarugo
        eficiencia_maquina = 0.85
        produtividade_kg_h = peso_tarugo * (velocidade_stem * eficiencia_maquina * 60 / puxada_maxima)
        fator_transformacao = produtividade_kg_h / velocidade_stem if velocidade_stem else 0

        velocidade_puller = velocidade_stem * eficiencia_maquina
        puxada = comprimento_real * cortes_por_tarugo
        tamanho_tarugo = puxada * 1000  # mm

        st.success("Proposta Gerada com Sucesso")
        st.markdown(f"**Peso Específico (PE):** {pe:.3f} kg/m")
        st.markdown(f"**Planicidade (PL):** {pl:.2f} mm")
        st.markdown(f"**Velocidade do Stem:** {velocidade_stem} m/min")
        st.markdown(f"**Tipo de Serra:** {tipo_serra} (Perda: {perda} m)")
        st.markdown(f"**Quantidade Máxima de Furos por Ferramenta:** {qtd_max_furos}")
        st.markdown(f"**Pacote de Ferramenta Sugerido:** {pacote}")

        st.subheader("🔧 Cálculo Simplificado")
        st.markdown(f"**Peso do Tarugo:** {peso_tarugo:.2f} kg")
        st.markdown(f"**Produtividade Estimada:** {produtividade_kg_h:.2f} kg/h")
        st.markdown(f"**Fator de Transformação:** {fator_transformacao:.2f}")

        st.subheader("📊 Cálculo segundo Planilha 2169")
        st.markdown(f"**Velocidade do Puller:** {velocidade_puller:.2f} m/min")
        st.markdown(f"**Comprimento da Puxada:** {puxada:.2f} m")
        st.markdown(f"**Tamanho do Tarugo:** {tamanho_tarugo:.0f} mm")

        dados = {
            "Área (cm²)": [area],
            "Perímetro (mm)": [perimetro],
            "Tipo": [tipo],
            "DCC (mm)": [dcc],
            "Maior Linear (mm)": [maior_linear],
            "Comprimento (mm)": [comprimento],
            "Liga": [liga],
            "Acabamento": [acabamento],
            "Exclusiva": [exclusiva],
            "Volume Mensal (kg)": [volume_mensal],
            "Peso Específico (kg/m)": [pe],
            "Planicidade (mm)": [pl],
            "Velocidade Stem (m/min)": [velocidade_stem],
            "Tipo de Serra": [tipo_serra],
            "Pacote Ferramenta": [pacote],
            "Máx. Furos": [qtd_max_furos],
            "Peso Tarugo (kg)": [peso_tarugo],
            "Produtividade (kg/h)": [produtividade_kg_h],
            "Fator Transformação": [fator_transformacao],
            "Velocidade Puller (m/min)": [velocidade_puller],
            "Puxada (m)": [puxada],
            "Tamanho Tarugo (mm)": [tamanho_tarugo],
        }

        df = pd.DataFrame(dados)

        # Excel
        output_excel = BytesIO()
        with pd.ExcelWriter(output_excel, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name="Proposta")
        output_excel.seek(0)

        st.download_button(
            label="📄 Baixar Proposta em Excel",
            data=output_excel,
            file_name="proposta_automatica.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        # PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "Tecnoperfil - Proposta Técnica e Comercial", ln=True, align="C")

        pdf.set_font("Arial", size=11)
        pdf.ln(5)
        for key, val in dados.items():
            pdf.cell(90, 8, f"{key}:", border=0)
            pdf.cell(40, 8, f"{val[0]}", ln=True)

        output_pdf = BytesIO()
        pdf.output(output_pdf)
        output_pdf.seek(0)

        st.download_button(
            label="📑 Baixar Proposta em PDF",
            data=output_pdf,
            file_name="proposta_automatica.pdf",
            mime="application/pdf"
        )
